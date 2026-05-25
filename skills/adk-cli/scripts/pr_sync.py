"""pr_sync.py — `adk pr-sync`: the one-stop "freshen everything" command.

Composes the smaller subcommands into a deterministic 6-step pipeline so the
user doesn't have to remember the order:

  1. pr-scan                 walk configured Slack channels for new PR links
  2. pr-queue update --all   refresh each row's metadata (head_sha + merged +
                             declined) — origin API is the source of truth
  3. pr-queue clean          drop merged + declined rows + their on-disk task folders
  4. pr-task clean-orphans   drop on-disk task folders with no queue row
  5. pr-queue remind         Slack-reply reminder for any PR reviewed >=24h
                             ago with no new commits since
  5.5. base-index audit      promote a target branch to a base index when N+
                             queued PRs share it; refresh on age-staleness
                             OR remote-tip drift; bases promoted here are
                             tagged created_by=auto for the cleanup pass.
  5.6. auto-base cleanup     delete auto-promoted bases whose queue users
                             are all terminal (no in-use rows).
  6. pr-task prepare --all   create/refresh task folders for remaining rows
                             (Phase 3 short-circuits when head_sha unchanged)

Every step is opt-out (--no-scan, --no-prepare, --no-remind). `--detailed`
forwards the detailed embedding path into `pr-task prepare`; `--deep` is
accepted for PR-review flag symmetry. Per-step
failures are surfaced but do not abort the rest of the pipeline. The final
terminal summary reports per-step status so you can spot stalls at a glance.

Idempotent. Safe to wire into a launchd job, a cron, or `adk loop`.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
# `_common` lives under the pr-review skill, alongside parse_pr_url et al.
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
SCRIPTS_ROOT = THIS_DIR.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))
CODE_INDEX_LIB = SCRIPTS_ROOT / "lib" / "code_index"
sys.path.insert(0, str(CODE_INDEX_LIB))

from _common import (  # noqa: E402
    RunEvent,
    emit_event,
    format_file_ref,
    get_logger,
    is_orchestrated,
    parse_event_line,
    parse_pr_url,
    status_glyph,
)
from queue_io import DEFAULT_QUEUE_PATH, TERMINAL_STATUSES, read_queue  # noqa: E402
from tui_plan import SyncPlanWriter  # noqa: E402

_PR_SYNC_STEPS = [
    "pr-scan",
    "pr-queue update --all",
    "pr-queue clean (merged)",
    "pr-task clean-orphans",
    "pr-queue remind",
    "base-index audit",
    "auto-base cleanup",
    "pr-task prepare --all",
]


# Internal audit-mode states:
#   "act"     — run fix commands (default).
#   "ask"     — prompt before each fix command (-i / --interactive).
#   "preview" — print intended commands without running them (--dry-run).
#   "off"     — skip the audit entirely (--no-base-audit).
_AUDIT_MODES = ("act", "ask", "preview", "off")

def _load_pr_sync_setting(key: str, default):
    """Read one key under `pr_sync:` in adk-cli.json5, then `default`. Safe on fresh
    installs — missing files return `default`."""
    try:
        from config_io import get_adk_cli  # noqa: WPS433
        return get_adk_cli("pr_sync", key, default=default)
    except Exception:
        return default


def _remote_tip(repo: str, branch: str) -> str | None:
    """Resolve the current remote tip of `branch` via the bare clone's
    `git ls-remote`. Returns the 40-char SHA, or None on any failure (no
    bare clone, network error, branch missing on remote). Single network
    round-trip — call sparingly (once per indexed branch per audit)."""
    import subprocess
    from _common import repo_clone_for  # noqa: WPS433
    bare = repo_clone_for(repo)
    if not (bare / "HEAD").exists():
        return None
    try:
        cp = subprocess.run(
            ["git", "-C", str(bare), "ls-remote", "--exit-code",
             "origin", f"refs/heads/{branch}"],
            capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if cp.returncode != 0:
        return None
    line = (cp.stdout or "").strip().splitlines()
    if not line:
        return None
    sha = line[0].split("\t", 1)[0].strip()
    return sha or None


def _audit_base_indexes(queue_path: str, *, mode: str, embed_model: str | None,
                        log, promote_threshold: int = 2,
                        refresh_min_age_hours: float = 1.0,
                        emit_progress: bool = False) -> dict:
    """Group queued non-merged rows by (repo, target_branch) and decide
    promote / refresh / nothing for each group.

    Decision rules per group (count = number of non-terminal queued PRs):
      - exact base PRESENT and not drifted from remote and age-fresh → no-op.
      - exact base PRESENT and (age-stale OR (drifted AND age >= refresh_min_age_hours))
            → STALE / DRIFTED gap; `adk repo update <repo> --branch <target>`.
      - exact base MISSING and count >= promote_threshold
            → MISSING gap; `adk repo branch add <repo> --branch <target> --auto`.
            Tagged created_by=auto so step 5.6 (auto-base cleanup) can demote
            it when the queue drops back to zero.
      - exact base MISSING and count < promote_threshold
            → BELOW_THRESHOLD informational gap; no command, no action even
            under auto mode. The PR's prepare path will fall back to the
            repo's default branch index.

    Behavior is gated by `mode` (Model-1 semantics — act by default, opt in
    to asking with -i, opt in to previewing with --dry-run):
      - "act"     — run the command for each *actionable* gap. (Default.)
      - "ask"     — prompt before each *actionable* gap (-i). Non-actionable
                    gaps (below_threshold) never prompt.
      - "preview" — log every intended command but execute none (--dry-run).
      - "off"     — silent; only count gaps and return them in the summary.

    Never blocks downstream steps — returns rc=0 regardless of gaps.
    """
    def progress(detail: str) -> None:
        if emit_progress:
            emit_event(RunEvent(kind="step_progress", name="base index",
                                status="run", detail=detail))

    try:
        from base_index import (  # noqa: WPS433
            get_branch_index, is_fresh, pick_base_index,
        )
    except Exception as e:
        log.warning("base-index audit: base_index module unavailable (%s); skipping", e)
        return {"audited": False, "reason": "lib-unavailable"}

    queue = read_queue(Path(queue_path).expanduser())
    rows = queue.get("prs") or []

    groups: dict[tuple[str, str], list[str]] = {}
    skipped_no_target = 0
    for r in rows:
        link = r.get("pr_url")
        if not link:
            continue
        if (r.get("status") or "pending") in TERMINAL_STATUSES:
            continue
        target_branch = (r.get("target_branch") or "").strip()
        if not target_branch:
            # target_branch is captured by `pr-queue update --all`; on first
            # encounter (new queue rows) the field may be missing. The next
            # pr-sync picks it up. Skip silently here.
            skipped_no_target += 1
            continue
        try:
            p = parse_pr_url(link)
        except ValueError:
            continue
        key = (p["repo"], target_branch)
        groups.setdefault(key, []).append(link)

    progress(f"checking {len(groups)} branch group(s)")
    gaps: list[dict] = []
    sorted_groups = sorted(groups.items())
    for group_idx, ((repo, target_branch), links) in enumerate(sorted_groups, start=1):
        count = len(links)
        progress(f"group {group_idx}/{len(sorted_groups)} {repo}/{target_branch}: checking index")
        exact = get_branch_index(repo, target_branch)
        if exact is None:
            if count < promote_threshold:
                # Below the promote bar — surface for visibility but no action.
                fallback = pick_base_index(repo, target_branch)
                gaps.append({
                    "repo": repo, "target_branch": target_branch,
                    "kind": "below_threshold",
                    "queued_prs": count,
                    "promote_threshold": promote_threshold,
                    "fallback_to": (fallback.branch if fallback and fallback.branch != target_branch
                                    else None),
                    "command": None,
                })
                continue
            fallback = pick_base_index(repo, target_branch)
            gaps.append({
                "repo": repo, "target_branch": target_branch,
                "kind": "missing",
                "queued_prs": count,
                "fallback_to": (fallback.branch if fallback and fallback.branch != target_branch
                                else None),
                "command": f"adk repo branch add {repo} --branch {target_branch} --auto",
            })
            continue
        age_fresh = is_fresh(exact)
        # Drift check: did the remote tip move since we indexed? Only fire
        # when the local index is older than refresh_min_age_hours — this
        # keeps us from re-embedding on every 10-minute merge to develop.
        age_hours = exact.age_days * 24.0
        drift_remote = None
        drifted = False
        if age_hours >= refresh_min_age_hours:
            progress(f"group {group_idx}/{len(sorted_groups)} {repo}/{target_branch}: checking remote tip")
            drift_remote = _remote_tip(repo, target_branch)
            if drift_remote and drift_remote != exact.indexed_sha:
                drifted = True
        if age_fresh and not drifted:
            continue
        gaps.append({
            "repo": repo, "target_branch": target_branch,
            "kind": "stale" if not age_fresh else "drifted",
            "queued_prs": count,
            "age_days": round(exact.age_days, 1),
            "indexed_sha": exact.indexed_sha,
            "remote_tip": drift_remote,
            "command": f"adk repo update {repo} --branch {target_branch}",
        })

    if not gaps:
        log.info("base-index audit: all %d queued group(s) covered by a fresh per-branch base",
                 len(groups))
        return {"audited": True, "groups": len(groups), "gaps": [],
                "skipped_no_target_branch": skipped_no_target,
                "promote_threshold": promote_threshold,
                "refresh_min_age_hours": refresh_min_age_hours,
                "mode": mode}

    # Log a one-liner per gap in every visible mode (act / ask / preview).
    # "off" stays silent.
    if mode in ("act", "ask", "preview"):
        for g in gaps:
            if g["kind"] == "missing":
                fallback_note = (f" (falls back to {g['fallback_to']})"
                                 if g["fallback_to"] else "")
                log.warning("base-index audit: %s/%s not indexed (%d queued PR%s)%s — %s",
                            g["repo"], g["target_branch"], g["queued_prs"],
                            "" if g["queued_prs"] == 1 else "s",
                            fallback_note, g["command"])
            elif g["kind"] == "stale":
                log.warning("base-index audit: %s/%s stale (%s days, %d queued PR%s) — %s",
                            g["repo"], g["target_branch"], g["age_days"],
                            g["queued_prs"],
                            "" if g["queued_prs"] == 1 else "s",
                            g["command"])
            elif g["kind"] == "drifted":
                log.warning("base-index audit: %s/%s drifted from remote "
                            "(indexed=%s remote=%s, %d queued PR%s) — %s",
                            g["repo"], g["target_branch"],
                            (g["indexed_sha"] or "?")[:12],
                            (g["remote_tip"] or "?")[:12],
                            g["queued_prs"],
                            "" if g["queued_prs"] == 1 else "s",
                            g["command"])
            elif g["kind"] == "below_threshold":
                fallback_note = (f" (falls back to {g['fallback_to']})"
                                 if g["fallback_to"] else "")
                log.info("base-index audit: %s/%s has only %d queued PR (< promote_threshold=%d)%s — "
                         "no auto-promote; default-branch index will be used",
                         g["repo"], g["target_branch"], g["queued_prs"],
                         g["promote_threshold"], fallback_note)

    if mode in ("act", "ask", "preview"):
        actionable = [g for g in gaps if g.get("command")]
        if not actionable:
            if mode == "act":
                log.info("base-index audit: no actionable gaps "
                         "(all gaps below promote_threshold=%d)", promote_threshold)
        else:
            verb = {"act": "running", "ask": "ready", "preview": "would run"}[mode]
            log.info("base-index audit: %s mode — %s %d fix command(s)",
                     mode, verb, len(actionable))
            from repo import main as repo_main  # noqa: WPS433
            for g in actionable:
                if g["kind"] == "missing":
                    argv = ["branch", "add", g["repo"], "--branch", g["target_branch"],
                            "--auto", "--auto-reason",
                            f"queued_prs={g['queued_prs']} (>= promote_threshold={promote_threshold})"]
                else:
                    argv = ["update", g["repo"], "--branch", g["target_branch"]]
                if embed_model:
                    argv += ["--embed-model", embed_model]
                cmdline = "adk repo " + " ".join(argv)
                if mode == "preview":
                    log.info("base-index audit: [preview] %s", cmdline)
                    g["fix_rc"] = None
                    g["fix_status"] = "previewed"
                    continue
                if mode == "ask":
                    try:
                        ans = input(f"  run `{cmdline}`? [Y/n] ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        ans = "n"
                    if ans and ans not in ("y", "yes"):
                        log.info("base-index audit: skipped (user declined): %s", cmdline)
                        g["fix_rc"] = None
                        g["fix_status"] = "declined"
                        continue
                try:
                    progress(f"{mode}: {cmdline}")
                    rc = repo_main(argv)
                    g["fix_rc"] = rc
                    g["fix_status"] = "ok" if rc == 0 else f"rc={rc}"
                    progress(f"finished {cmdline} rc={rc}")
                    if rc != 0:
                        log.warning("base-index audit: command failed (rc=%d): %s",
                                    rc, cmdline)
                except SystemExit as e:
                    g["fix_rc"] = 1
                    g["fix_status"] = "error"
                    g["fix_error"] = str(e)
                    progress(f"failed {cmdline}: {e}")
                    log.warning("base-index audit: command failed: %s: %s", cmdline, e)

    return {"audited": True, "groups": len(groups), "gaps": gaps,
            "skipped_no_target_branch": skipped_no_target,
            "promote_threshold": promote_threshold,
            "refresh_min_age_hours": refresh_min_age_hours,
            "mode": mode}


class _LiveEventBuffer:
    """Capture normal child output while forwarding ADK_EVENT lines live."""

    def __init__(self, event_stream) -> None:
        self.event_stream = event_stream
        self._pending = ""
        self._detail_lines: list[str] = []
        self.events: list[dict] = []

    def write(self, text: str) -> int:
        if not text:
            return 0
        self._pending += text
        while "\n" in self._pending:
            line, self._pending = self._pending.split("\n", 1)
            self._handle_line(line)
        return len(text)

    def flush(self) -> None:
        flush = getattr(self.event_stream, "flush", None)
        if callable(flush):
            flush()

    def captured_text(self) -> str:
        if self._pending:
            self._handle_line(self._pending)
            self._pending = ""
        return "\n".join(self._detail_lines).strip()

    def last_event(self, kind: str) -> dict | None:
        for event in reversed(self.events):
            if event.get("kind") == kind:
                return event
        return None

    def _handle_line(self, line: str) -> None:
        event = parse_event_line(line)
        if event is not None:
            print(line, file=self.event_stream, flush=True)
            self.events.append(event)
        elif line.strip():
            self._detail_lines.append(line)


def _run_step(name: str, fn, log, *, plan: SyncPlanWriter | None = None,
              plan_name: str | None = None, quiet: bool = False) -> dict:
    """Run one pipeline step. Capture rc + a short status; never raise."""
    if not quiet:
        log.info("=== step: %s ===", name)
    pname = plan_name or name
    if plan is not None:
        plan.step_start(pname)
    if quiet:
        emit_event(RunEvent(kind="step_start", name=name, status="run",
                            detail="starting"))
    try:
        child_done_event = None
        if quiet:
            buf = _LiveEventBuffer(sys.stdout)
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = fn()
            captured = buf.captured_text()
            child_done_event = buf.last_event("step_done")
            if captured:
                log.info("%s output:\n%s", name, captured)
        else:
            rc = fn()
        status = "ok" if rc == 0 else "warn"
        if plan is not None:
            plan.step_done(pname, status=status, rc=rc)
        result = {"step": name, "rc": rc, "status": status}
        if quiet and child_done_event is None:
            emit_event(RunEvent(kind="step_done", name=name,
                                status="done" if rc == 0 else "warn",
                                detail=_step_detail(name, result)))
        return result
    except SystemExit as e:
        # die() raises SystemExit; treat as a step-level failure, keep going.
        log.warning("%s: %s", name, e)
        if plan is not None:
            plan.step_done(pname, status="failed", rc=1)
        result = {"step": name, "rc": 1, "status": "failed", "reason": str(e)}
        if quiet:
            emit_event(RunEvent(kind="step_done", name=name, status="fail",
                                detail=str(e)))
            emit_event(RunEvent(kind="attention", name=name, status="fail",
                                detail=f"{name} failed", reason=str(e)))
        return result
    except Exception as e:
        log.warning("%s: unexpected %s", name, e)
        if plan is not None:
            plan.step_done(pname, status="failed", rc=1)
        result = {"step": name, "rc": 1, "status": "failed", "reason": str(e)}
        if quiet:
            emit_event(RunEvent(kind="step_done", name=name, status="fail",
                                detail=str(e)))
            emit_event(RunEvent(kind="attention", name=name, status="fail",
                                detail=f"{name} failed", reason=str(e)))
        return result


def _step_detail(name: str, result: dict) -> str:
    if result.get("reason"):
        return str(result["reason"])
    return f"rc={result.get('rc', 0)}"


def _print_sync_summary(queue: str, results: list[dict]) -> None:
    failed = [r for r in results if r.get("status") == "failed"]
    warned = [r for r in results if r.get("status") == "warn"]
    skipped = [r for r in results if r.get("status") == "skipped"]
    print(f"\n{'✅' if not failed else '⚠️'} adk pr-sync complete")
    print(f"   ├─ queue: {format_file_ref(queue)}")
    print(f"   ├─ steps: {len(results)}")
    print(f"   ├─ failed: {len(failed)}")
    print(f"   ├─ warnings: {len(warned)}")
    print(f"   └─ skipped: {len(skipped)}")
    print("\n   Steps:")
    for r in results:
        status = r.get("status") or "ok"
        line = f"   ├─ {status_glyph(status)} {r.get('step', '?')} · {status}"
        if r.get("rc") is not None:
            line += f" · rc={r.get('rc')}"
        if r.get("reason"):
            line += f" · {r.get('reason')}"
        print(line)
        audit = r.get("audit") or {}
        if audit:
            gaps = audit.get("gaps") or []
            groups = audit.get("groups")
            print(f"   │  └─ base indexes: groups={groups}, gaps={len(gaps)}, mode={audit.get('mode')}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="adk pr-sync",
        description="One-stop PR sync: scan → refresh metadata → drop merged → "
                    "clean orphans → prepare task folders.",
    )
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    ap.add_argument("--no-scan", action="store_true",
                    help="skip step 1 (pr-scan)")
    ap.add_argument("--no-clean-orphans", action="store_true",
                    help="skip step 4 (orphan task-folder cleanup); default is to delete")
    ap.add_argument("--no-remind", action="store_true",
                    help="skip step 5 (Slack reminders for stale reviews); default is to post")
    ap.add_argument("--no-prepare", action="store_true",
                    help="skip step 6 (pr-task prepare --all); metadata + cleanup only")
    ap.add_argument("--no-base-audit", action="store_true",
                    help="skip the base-index audit step (5.5).")
    ap.add_argument("-i", "--interactive", action="store_true",
                    help="ask before each base-index fix command (promote / refresh). "
                         "Without -i, the audit acts on every actionable gap; "
                         "with --dry-run it previews; with --no-base-audit it skips.")
    ap.add_argument("--embed-model", default=None,
                    help="forwarded to `adk repo branch add` / `adk repo update` "
                         "during audit auto-mode (default: nomic-embed-text)")
    ap.add_argument("--promote-threshold", type=int, default=None,
                    help="minimum number of non-terminal queued PRs sharing a target branch "
                         "before audit auto-mode will `adk repo branch add --auto` that branch. "
                         "Default: from core.yaml pr_sync.base_index_promote_threshold, fallback 2.")
    ap.add_argument("--refresh-min-age-hours", type=float, default=None,
                    help="minimum age (hours) of a base index before audit will check for "
                         "remote-tip drift. Prevents thrashing on rapidly-merging branches. "
                         "Default: from core.yaml pr_sync.base_index_refresh_min_age_hours, fallback 1.0.")
    ap.add_argument("--no-auto-demote", action="store_true",
                    help="skip step 5.6 (auto-base cleanup); default is to demote auto-added "
                         "bases whose queue rows are all terminal.")
    ap.add_argument("--dry-run", action="store_true",
                    help="preview the destructive steps (orphan cleanup, reminder posts) "
                         "without applying them; metadata refresh + scan still run")
    ap.add_argument("--remind-threshold-hours", type=float, default=24.0,
                    help="hours since review before a reminder qualifies (default: 24)")
    ap.add_argument("--detailed", action="store_true",
                    help="forwarded to pr-task prepare: use bge-m3 embeddings")
    ap.add_argument("--deep", action="store_true",
                    help="forwarded to pr-task prepare for /adk-pr-review flag symmetry; "
                         "model depth is selected by the review harness")
    ap.add_argument("--rebuild", action="store_true",
                    help="forwarded to pr-task prepare: force full re-index")
    ap.add_argument("--since-hours", type=float, default=0.0,
                    help="forwarded to pr-scan")
    ap.add_argument("--since-days", type=int, default=0,
                    help="forwarded to pr-scan")
    ap.add_argument("--channels", default="",
                    help="forwarded to pr-scan (comma-separated; overrides config)")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="accepted for uniformity with other adk subcommands; pr-sync's "
                         "destructive steps are actual-by-default")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to $ADK_DATA_HOME/logs/")
    ap.add_argument("--quiet", action="store_true",
                    help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-sync", enabled=True, argv=argv)

    log = get_logger("pr-sync")
    quiet = bool(args.quiet or is_orchestrated())
    queue = args.queue
    results: list[dict] = []
    plan_writer = SyncPlanWriter(queue=queue, argv=list(argv or []),
                                 step_names=_PR_SYNC_STEPS)

    # 1. pr-scan
    if not args.no_scan:
        from pr_scan import main as scan_main  # type: ignore[import-not-found]
        scan_argv = ["--queue", queue, "-y"]
        if quiet:
            scan_argv.append("--quiet")
        if args.since_hours:
            scan_argv += ["--since-hours", str(args.since_hours)]
        if args.since_days:
            scan_argv += ["--since-days", str(args.since_days)]
        if args.channels:
            scan_argv += ["--channels", args.channels]
        results.append(_run_step("pr-scan", lambda: scan_main(scan_argv), log,
                                 plan=plan_writer, quiet=quiet))
    else:
        plan_writer.step_done("pr-scan", status="skipped")
        results.append({"step": "pr-scan", "status": "skipped"})

    # 2. pr-queue update --all (metadata refresh; no --full — that happens in step 5)
    from pr_queue import main as queue_main  # type: ignore[import-not-found]
    results.append(_run_step(
        "pr-queue update --all",
        lambda: queue_main(["--queue", queue, "update", "--all"]),
        log,
        plan=plan_writer,
        quiet=quiet,
    ))

    # 3. pr-queue clean (drop merged + their task folders; no --yes needed for
    #    the merged-only path, which is the default).
    results.append(_run_step(
        "pr-queue clean (merged)",
        lambda: queue_main(["--queue", queue, "clean"]),
        log,
        plan=plan_writer,
        quiet=quiet,
    ))

    # 4. pr-task clean-orphans (drop on-disk folders with no queue row)
    from pr_task import main as task_main  # type: ignore[import-not-found]
    if not args.no_clean_orphans:
        orphan_argv = ["clean-orphans", "--queue", queue]
        if args.dry_run:
            orphan_argv.append("--dry-run")
        else:
            orphan_argv.append("-y")
        results.append(_run_step(
            "pr-task clean-orphans" + (" (dry-run)" if args.dry_run else ""),
            lambda: task_main(orphan_argv),
            log,
            plan=plan_writer,
            plan_name="pr-task clean-orphans",
            quiet=quiet,
        ))
    else:
        plan_writer.step_done("pr-task clean-orphans", status="skipped")
        results.append({"step": "pr-task clean-orphans", "status": "skipped"})

    # 5. pr-queue remind (Slack pings for stale reviews)
    if not args.no_remind:
        remind_argv = ["--queue", queue, "remind",
                       "--threshold-hours", str(args.remind_threshold_hours)]
        if args.dry_run:
            remind_argv.append("--dry-run")
        results.append(_run_step(
            "pr-queue remind" + (" (dry-run)" if args.dry_run else ""),
            lambda: queue_main(remind_argv),
            log,
            plan=plan_writer,
            plan_name="pr-queue remind",
            quiet=quiet,
        ))
    else:
        plan_writer.step_done("pr-queue remind", status="skipped")
        results.append({"step": "pr-queue remind", "status": "skipped"})

    # 5.5. base-index audit (per-(repo, target_branch) coverage).
    #
    # Mode resolution:
    #   --no-base-audit              → "off"
    #   --dry-run                    → "preview"
    #   -i / --interactive           → "ask"
    #   (default)                    → "act"
    if not args.no_base_audit:
        if args.dry_run:
            mode = "preview"
        elif args.interactive:
            mode = "ask"
        else:
            # Allow a long-tail override via adk-cli.json5.pr_sync.audit_mode
            # for users who want preview-by-default in their environment.
            override = _load_pr_sync_setting("audit_mode", None)
            if override in _AUDIT_MODES:
                mode = override
            elif override is None:
                mode = "act"
            else:
                log.warning("pr_sync.audit_mode: ignoring invalid value %r "
                            "(allowed: %s); using 'act'",
                            override, ", ".join(_AUDIT_MODES))
                mode = "act"
        promote_threshold = args.promote_threshold
        if promote_threshold is None:
            try:
                promote_threshold = int(_load_pr_sync_setting(
                    "base_index_promote_threshold", default=2))
            except (TypeError, ValueError):
                promote_threshold = 2
        refresh_min_age_hours = args.refresh_min_age_hours
        if refresh_min_age_hours is None:
            try:
                refresh_min_age_hours = float(_load_pr_sync_setting(
                    "base_index_refresh_min_age_hours", default=1.0))
            except (TypeError, ValueError):
                refresh_min_age_hours = 1.0
        def _do_audit():
            res = _audit_base_indexes(
                queue, mode=mode, embed_model=args.embed_model, log=log,
                promote_threshold=promote_threshold,
                refresh_min_age_hours=refresh_min_age_hours,
                emit_progress=quiet,
            )
            # Surface a tally so the final pr-sync JSON shows the audit result.
            results.append({
                "step": "base-index audit",
                "status": "ok",
                "audit": res,
            })
            return 0
        # Don't go through _run_step here — we want the audit summary inline
        # in the step record, not a single rc.
        plan_writer.step_start("base-index audit")
        if quiet:
            emit_event(RunEvent(kind="step_start", name="base index",
                                status="run", detail="checking branch coverage"))
        try:
            if quiet:
                buf = _LiveEventBuffer(sys.stdout)
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    _do_audit()
                captured = buf.captured_text()
                if captured:
                    log.info("base-index audit output:\n%s", captured)
            else:
                _do_audit()
            plan_writer.step_done("base-index audit", status="ok", rc=0)
            audit = results[-1].get("audit", {}) if results else {}
            gaps = audit.get("gaps") or []
            if quiet:
                emit_event(RunEvent(
                    kind="step_done",
                    name="base index",
                    status="done",
                    detail=f"groups={audit.get('groups', 0)}, gaps={len(gaps)}, mode={audit.get('mode')}",
                ))
                for g in gaps:
                    if g.get("command"):
                        emit_event(RunEvent(
                            kind="attention",
                            name="base index",
                            status="warn",
                            detail=(f"{g.get('repo')}/{g.get('target_branch')} "
                                    f"{g.get('kind')} ({g.get('queued_prs')} queued PRs)"),
                            reason=g.get("command", ""),
                        ))
        except Exception as e:
            log.warning("base-index audit: unexpected %s", e)
            plan_writer.step_done("base-index audit", status="failed", rc=1)
            results.append({"step": "base-index audit",
                            "status": "failed", "reason": str(e)})
            if quiet:
                emit_event(RunEvent(kind="step_done", name="base index",
                                    status="fail", detail=str(e)))
    else:
        plan_writer.step_done("base-index audit", status="skipped")
        results.append({"step": "base-index audit", "status": "skipped"})

    # 5.6. auto-base cleanup (demote auto-added bases whose queue users are
    # all terminal). Safe to run even when nothing was promoted this round —
    # it's idempotent and short-circuits when there are no auto-bases. We
    # capture cmd_auto_bases_clean's own JSON output so it doesn't leak
    # into pr-sync's top-level summary; the captured detail is attached to
    # the step record instead.
    if not args.no_auto_demote:
        from repo import cmd_auto_bases_clean  # noqa: WPS433
        ns = argparse.Namespace(
            queue=queue, dry_run=bool(args.dry_run), yes=True,
            force=False, name=None, branch=None,
        )
        if not quiet:
            log.info("=== step: auto-base cleanup ===")
        plan_writer.step_start("auto-base cleanup")
        if quiet:
            emit_event(RunEvent(kind="step_start", name="auto-base cleanup",
                                status="run", detail="checking unused auto bases"))
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = cmd_auto_bases_clean(ns)
            captured = buf.getvalue().strip()
            detail = None
            if captured:
                try:
                    detail = json.loads(captured)
                except Exception:
                    detail = {"raw": captured}
            status = "ok" if (rc or 0) == 0 else "warn"
            plan_writer.step_done("auto-base cleanup", status=status, rc=rc or 0)
            results.append({
                "step": "auto-base cleanup",
                "rc": rc or 0,
                "status": status,
                "detail": detail,
            })
            if quiet:
                emit_event(RunEvent(kind="step_done", name="auto-base cleanup",
                                    status="done" if status == "ok" else "warn",
                                    detail=f"rc={rc or 0}"))
        except SystemExit as e:
            log.warning("auto-base cleanup: SystemExit %s", e)
            plan_writer.step_done("auto-base cleanup", status="failed", rc=1)
            results.append({"step": "auto-base cleanup", "rc": 1,
                            "status": "failed", "reason": str(e)})
            if quiet:
                emit_event(RunEvent(kind="step_done", name="auto-base cleanup",
                                    status="fail", detail=str(e)))
        except Exception as e:
            log.warning("auto-base cleanup: unexpected %s", e)
            plan_writer.step_done("auto-base cleanup", status="failed", rc=1)
            results.append({"step": "auto-base cleanup", "rc": 1,
                            "status": "failed", "reason": str(e)})
            if quiet:
                emit_event(RunEvent(kind="step_done", name="auto-base cleanup",
                                    status="fail", detail=str(e)))
    else:
        plan_writer.step_done("auto-base cleanup", status="skipped")
        results.append({"step": "auto-base cleanup", "status": "skipped"})

    # 6. pr-task prepare --all
    if not args.no_prepare:
        prep_argv = ["prepare", "--all", "--queue", queue]
        if args.detailed:
            prep_argv.append("--detailed")
        if args.deep:
            prep_argv.append("--deep")
        if args.rebuild:
            prep_argv.append("--rebuild")
        if quiet:
            prep_argv.append("--quiet")
        results.append(_run_step(
            "pr-task prepare --all",
            lambda: task_main(prep_argv),
            log,
            plan=plan_writer,
            quiet=quiet,
        ))
    else:
        plan_writer.step_done("pr-task prepare --all", status="skipped")
        results.append({"step": "pr-task prepare --all", "status": "skipped"})

    if not quiet:
        _print_sync_summary(queue, results)
    rc_out = 1 if any(r.get("status") == "failed" for r in results) else 0
    plan_writer.finish(rc_out)
    return rc_out


if __name__ == "__main__":
    raise SystemExit(main())
