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
  6. pr-task prepare --all   create/refresh task folders for remaining rows
                             (Phase 3 short-circuits when head_sha unchanged)

Every step is opt-out (--no-scan, --no-prepare, --no-remind). Per-step
failures are surfaced but do not abort the rest of the pipeline. The final
JSON summary reports per-step counts so you can spot stalls at a glance.

Idempotent. Safe to wire into a launchd job, a cron, or `adk loop`.
"""
from __future__ import annotations

import argparse
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

from _common import get_logger, parse_pr_url  # noqa: E402
from queue_io import DEFAULT_QUEUE_PATH, TERMINAL_STATUSES, read_queue  # noqa: E402


_AUDIT_MODES = ("off", "warn", "auto")


def _load_pr_sync_setting(key: str, default):
    """Read one key under `pr_sync:` in core.yaml. Falls back to `default` if
    config_io / core.yaml aren't reachable (fresh installs)."""
    try:
        from config_io import load_core  # noqa: WPS433
        cfg = load_core() or {}
        node = cfg.get("pr_sync") or {}
        return node.get(key, default)
    except Exception:
        return default


def _audit_base_indexes(queue_path: str, *, mode: str, embed_model: str | None,
                        log) -> dict:
    """Group queued non-merged rows by (repo, target_branch) and check each
    group against `pick_base_index(repo, target_branch, require_fresh=True)`.

    Behavior is gated by `mode`:
      - "off":   silent; only count gaps and return them in the summary.
      - "warn":  log one line per gap with the exact `adk repo …` command to
                 fix it. (Default.)
      - "auto":  run the fix command for each gap, sequentially. Best paired
                 with a non-interactive shell.

    Never blocks downstream steps — returns rc=0 regardless of gaps.
    """
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

    gaps: list[dict] = []
    for (repo, target_branch), links in sorted(groups.items()):
        # Exact-branch check first — we want to distinguish "no index" from
        # "stale index" so we can emit the right command.
        exact = get_branch_index(repo, target_branch)
        if exact is not None and is_fresh(exact):
            continue
        if exact is None:
            # Maybe the default branch works; pick_base_index would fall back.
            fallback = pick_base_index(repo, target_branch)
            gaps.append({
                "repo": repo, "target_branch": target_branch,
                "kind": "missing",
                "queued_prs": len(links),
                "fallback_to": (fallback.branch if fallback and fallback.branch != target_branch
                                else None),
                "command": f"adk repo branch add {repo} --branch {target_branch}",
            })
        else:
            gaps.append({
                "repo": repo, "target_branch": target_branch,
                "kind": "stale",
                "queued_prs": len(links),
                "age_days": round(exact.age_days, 1),
                "command": f"adk repo update {repo} --branch {target_branch}",
            })

    if not gaps:
        log.info("base-index audit: all %d queued group(s) covered by a fresh per-branch base",
                 len(groups))
        return {"audited": True, "groups": len(groups), "gaps": [],
                "skipped_no_target_branch": skipped_no_target,
                "mode": mode}

    if mode in ("warn", "auto"):
        for g in gaps:
            if g["kind"] == "missing":
                fallback_note = (f" (falls back to {g['fallback_to']})"
                                 if g["fallback_to"] else "")
                log.warning("base-index audit: %s/%s not indexed (%d queued PR%s)%s — %s",
                            g["repo"], g["target_branch"], g["queued_prs"],
                            "" if g["queued_prs"] == 1 else "s",
                            fallback_note, g["command"])
            else:
                log.warning("base-index audit: %s/%s stale (%s days, %d queued PR%s) — %s",
                            g["repo"], g["target_branch"], g["age_days"],
                            g["queued_prs"],
                            "" if g["queued_prs"] == 1 else "s",
                            g["command"])

    if mode == "auto":
        log.info("base-index audit: auto mode — running %d fix command(s)", len(gaps))
        from repo import main as repo_main  # noqa: WPS433
        for g in gaps:
            if g["kind"] == "missing":
                argv = ["branch", "add", g["repo"], "--branch", g["target_branch"]]
            else:
                argv = ["update", g["repo"], "--branch", g["target_branch"]]
            if embed_model:
                argv += ["--embed-model", embed_model]
            try:
                rc = repo_main(argv)
                g["fix_rc"] = rc
                if rc != 0:
                    log.warning("base-index audit: command failed (rc=%d): adk repo %s",
                                rc, " ".join(argv))
            except SystemExit as e:
                g["fix_rc"] = 1
                g["fix_error"] = str(e)
                log.warning("base-index audit: command failed: adk repo %s: %s",
                            " ".join(argv), e)

    return {"audited": True, "groups": len(groups), "gaps": gaps,
            "skipped_no_target_branch": skipped_no_target, "mode": mode}


def _run_step(name: str, fn, log) -> dict:
    """Run one pipeline step. Capture rc + a short status; never raise."""
    log.info("=== step: %s ===", name)
    try:
        rc = fn()
        return {"step": name, "rc": rc, "status": "ok" if rc == 0 else "warn"}
    except SystemExit as e:
        # die() raises SystemExit; treat as a step-level failure, keep going.
        log.warning("%s: %s", name, e)
        return {"step": name, "rc": 1, "status": "failed", "reason": str(e)}
    except Exception as e:
        log.warning("%s: unexpected %s", name, e)
        return {"step": name, "rc": 1, "status": "failed", "reason": str(e)}


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
    ap.add_argument("--audit-mode", choices=_AUDIT_MODES, default=None,
                    help="how the audit reacts to missing / stale per-branch base "
                         "indexes (off | warn | auto). Default: from core.yaml "
                         "pr_sync.auto_update_base_indexes, fallback 'warn'.")
    ap.add_argument("--embed-model", default=None,
                    help="forwarded to `adk repo branch add` / `adk repo update` "
                         "during audit auto-mode (default: nomic-embed-text)")
    ap.add_argument("--dry-run", action="store_true",
                    help="preview the destructive steps (orphan cleanup, reminder posts) "
                         "without applying them; metadata refresh + scan still run")
    ap.add_argument("--remind-threshold-hours", type=float, default=24.0,
                    help="hours since review before a reminder qualifies (default: 24)")
    ap.add_argument("--detailed", action="store_true",
                    help="forwarded to pr-task prepare: use bge-m3 embeddings")
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
    args = ap.parse_args(argv)

    log = get_logger("pr-sync")
    queue = args.queue
    results: list[dict] = []

    # 1. pr-scan
    if not args.no_scan:
        from pr_scan import main as scan_main  # type: ignore[import-not-found]
        scan_argv = ["--queue", queue, "-y"]
        if args.since_hours:
            scan_argv += ["--since-hours", str(args.since_hours)]
        if args.since_days:
            scan_argv += ["--since-days", str(args.since_days)]
        if args.channels:
            scan_argv += ["--channels", args.channels]
        results.append(_run_step("pr-scan", lambda: scan_main(scan_argv), log))
    else:
        results.append({"step": "pr-scan", "status": "skipped"})

    # 2. pr-queue update --all (metadata refresh; no --full — that happens in step 5)
    from pr_queue import main as queue_main  # type: ignore[import-not-found]
    results.append(_run_step(
        "pr-queue update --all",
        lambda: queue_main(["--queue", queue, "update", "--all"]),
        log,
    ))

    # 3. pr-queue clean (drop merged + their task folders; no --yes needed for
    #    the merged-only path, which is the default).
    results.append(_run_step(
        "pr-queue clean (merged)",
        lambda: queue_main(["--queue", queue, "clean"]),
        log,
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
        ))
    else:
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
        ))
    else:
        results.append({"step": "pr-queue remind", "status": "skipped"})

    # 5.5. base-index audit (per-(repo, target_branch) coverage)
    if not args.no_base_audit:
        mode = args.audit_mode or _load_pr_sync_setting(
            "auto_update_base_indexes", default="warn",
        )
        if mode not in _AUDIT_MODES:
            log.warning("audit-mode: ignoring invalid value %r (allowed: %s); using 'warn'",
                        mode, ", ".join(_AUDIT_MODES))
            mode = "warn"
        def _do_audit():
            res = _audit_base_indexes(
                queue, mode=mode, embed_model=args.embed_model, log=log,
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
        try:
            _do_audit()
        except Exception as e:
            log.warning("base-index audit: unexpected %s", e)
            results.append({"step": "base-index audit",
                            "status": "failed", "reason": str(e)})
    else:
        results.append({"step": "base-index audit", "status": "skipped"})

    # 6. pr-task prepare --all
    if not args.no_prepare:
        prep_argv = ["prepare", "--all", "--queue", queue]
        if args.detailed:
            prep_argv.append("--detailed")
        if args.rebuild:
            prep_argv.append("--rebuild")
        results.append(_run_step(
            "pr-task prepare --all",
            lambda: task_main(prep_argv),
            log,
        ))
    else:
        results.append({"step": "pr-task prepare --all", "status": "skipped"})

    summary = {
        "queue": queue,
        "steps": results,
        "failed": [r for r in results if r.get("status") == "failed"],
    }
    print(json.dumps(summary, indent=2, default=str))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
