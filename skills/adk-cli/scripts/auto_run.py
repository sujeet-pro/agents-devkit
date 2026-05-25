"""auto_run.py — `adk pr-review-all` headless review orchestrator.

Per `docs/plans/adk-v4-overhaul.md` §7: runs the full pipeline without
interactive input. Scheduler-friendly (cron, launchd, GitHub Action).

Flow:
  1. `adk pr-sync` — runs the full DAG (Phase A→F).
  2. Enumerate non-terminal queue rows where `ready_for_review` holds
     (§6.u eligibility predicate from queue_io.py).
  3. Apply guards: --max-reviews, --exclude, --dry-run.
  4. For each eligible PR (up to --max-reviews), spawn the selected runner:
        claude: <agent> -p "/adk-pr-review <pr_url> [--detailed] [--deep]"
        cursor: cursor agent --print --force --trust --workspace <repo> "/adk-pr-review <pr_url> ..."
     Default runner: claude/Sonnet. Cursor defaults to Composer 2.5. --deep
     selects the deep profile (Claude Opus, Cursor GPT 5.5) and is auto-added
     for large/high-risk PRs unless --no-auto-deep is set.
  5. Capture per-PR exit code + stdout last line.
  6. Aggregate to `$ADK_DATA_HOME/skill-setup/auto-runs/<ts>/report.md`.

Exit codes:
  0 — every spawned review succeeded
  1 — at least one review failed
  2 — aborted by guard (e.g. invalid args)

Constitution §I.3 is absolute: this verb NEVER merges. The agent (via
the skill) posts inline comments + approves where §6.z allows, but
merges are always human-driven.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import selectors
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
# _common.py lives in the adk-pr-review skill, not adk-cli.
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
SCRIPTS_ROOT = THIS_DIR.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

from _common import die, get_logger  # type: ignore  # noqa: E402
from _common import parse_pr_url, pr_review_file, task_dir_for  # type: ignore  # noqa: E402
from adk_log import (  # type: ignore  # noqa: E402
    RunDashboard,
    extract_failure_reason,
    format_file_ref,
    format_pr_ref,
    parse_event_line,
    status_glyph,
)
from agent_harness import build_agent_cmd, resolve_runner_model  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, read_queue, review_work_needed, TERMINAL_STATUSES,
    WORK_COMMENTS, WORK_NONE, REVIEW_ATTEMPT_STARTED, REVIEW_ATTEMPT_FAILED,
    find_row, update_pr_entry,
)
from run_state import (  # noqa: E402
    complete_worker,
    file_link,
    run_id as make_run_state_id,
    update_run,
    update_worker,
    worker_id as make_worker_state_id,
    write_run,
    write_worker,
)
from skill_preflight import preflight  # noqa: E402

PY = sys.executable
REPO_ROOT = THIS_DIR.parent.parent.parent
ADK_BIN = REPO_ROOT / "bin" / "adk"

_LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_data_home, adk_skill_home  # noqa: E402

ADK_HOME = adk_data_home()
AUTO_RUNS_ROOT = adk_skill_home("setup") / "auto-runs"

# Per-agent rough cost coefficient (USD per review). Used by --max-cost-usd
# as a pre-flight estimate. Conservative; doesn't account for retries.
# Source: rough ballpark from observed runs; tune via core.yaml later.
AGENT_COST_USD = {
    "claude": 0.50,
    "codex": 0.30,
    "cursor": 0.30,
    "opencode": 0.30,
}


def _parse_quiet_hours(spec: str) -> tuple[int, int]:
    """Parse 'WW-XX' (24h, local) → (start_hour, end_hour). Inclusive of start,
    exclusive of end. '00-08' means 00:00 ≤ now < 08:00 → quiet.

    Wrap-around supported: '22-06' means 22:00 ≤ now OR now < 06:00.
    """
    import re as _re
    m = _re.match(r"^(\d{1,2})-(\d{1,2})$", spec.strip())
    if not m:
        raise ValueError(f"--quiet-hours must look like 'HH-HH' (24h), got {spec!r}")
    a, b = int(m.group(1)), int(m.group(2))
    if not (0 <= a < 24 and 0 <= b < 24):
        raise ValueError(f"--quiet-hours: hours must be 0-23, got {spec!r}")
    return a, b


def _in_quiet_hours(spec: str, now=None) -> bool:
    """True if `now` (local clock) falls within the quiet window."""
    if not spec:
        return False
    import datetime as _dt
    if now is None:
        now = _dt.datetime.now()
    a, b = _parse_quiet_hours(spec)
    h = now.hour
    if a == b:
        return False  # zero-length window
    if a < b:
        return a <= h < b
    return h >= a or h < b  # wrap-around


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _ts_for_run() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def _eligible_rows(queue_path: Path, *, exclude: set[str]) -> list[dict]:
    """Return non-terminal rows passing ready_for_review, minus excluded URLs.

    FIFO order follows the queue file order exactly.
    """
    q = read_queue(queue_path)
    prs = q.get("prs", []) or []
    eligible = []
    for e in prs:
        if (e.get("status") or "") in TERMINAL_STATUSES:
            continue
        if e.get("pr_url") in exclude:
            continue
        work_mode = review_work_needed(e)
        if work_mode == WORK_NONE:
            continue
        e["_adk_work_mode"] = work_mode
        eligible.append(e)
    return eligible


_PHASE_RE = re.compile(
    r"^[\s\-#*>]*"
    r"(?:\[[^\]]+\]\s*)?"
    r"[Pp]hase\s+"
    r"([0-9]+[a-zA-Z]?)"
    r"(?:\s*[:—\-]\s*([^.\n*:]{1,60}))?"
)


def _parse_phase_marker(text: str) -> str | None:
    m = _PHASE_RE.match(text)
    if m is None:
        return None
    num = m.group(1)
    desc = (m.group(2) or "").strip().rstrip("- ").rstrip()
    label = f"phase {num}: {desc}" if desc else f"phase {num}"
    return label[:80]


def _runner_cost_key(runner: str, agent: str) -> str:
    return runner if runner != "custom" else Path(agent).name


def _int_or_none(value) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _task_pr_json(pr_url: str) -> dict:
    try:
        p = parse_pr_url(pr_url)
        path = pr_review_file(task_dir_for(p["repo"], p["pr_number"]), "pr.json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def _complexity_reason(row: dict, args) -> str | None:
    """Return a reason to auto-select --deep for a PR, or None."""
    pr = _task_pr_json(row.get("pr_url", ""))
    changed_files = (
        _int_or_none(pr.get("changedFiles"))
        or _int_or_none(pr.get("changed_files"))
        or _int_or_none(row.get("changed_files"))
        or _int_or_none(row.get("changedFiles"))
    )
    additions = _int_or_none(pr.get("additions")) or _int_or_none(row.get("additions")) or 0
    deletions = _int_or_none(pr.get("deletions")) or _int_or_none(row.get("deletions")) or 0
    changed_lines = additions + deletions
    file_threshold = int(_cfg("auto_deep_file_threshold", 20))
    line_threshold = int(_cfg("auto_deep_line_threshold", 800))
    if changed_files is not None and changed_files >= file_threshold:
        return f"{changed_files} files >= {file_threshold}"
    if changed_lines >= line_threshold:
        return f"{changed_lines} changed lines >= {line_threshold}"
    title = str(pr.get("title") or row.get("title") or "").lower()
    if any(word in title for word in ("migration", "auth", "security", "payments", "permissions")):
        return "title indicates high-risk surface"
    return None


def _annotate_depth(rows: list[dict], args) -> None:
    for row in rows:
        reason = "forced by --deep" if args.deep else None
        if reason is None and args.auto_deep:
            reason = _complexity_reason(row, args)
        row["_adk_deep"] = bool(reason)
        row["_adk_deep_reason"] = reason


def _build_agent_cmd(pr_url: str, *, runner: str, agent: str | None,
                     model: str | None = None, detailed: bool = False,
                     deep: bool = False, work_mode: str | None = None,
                     rebuild: bool = False) -> list[str]:
    flags = []
    if detailed:
        flags.append("--detailed")
    if deep:
        flags.append("--deep")
    if rebuild:
        flags.append("--rebuild")
    if work_mode == WORK_COMMENTS:
        flags.append("--comments-only")
    prompt = " ".join(["/adk-pr-review", pr_url] + flags)
    resolved_model = resolve_runner_model(
        runner=runner,
        explicit_model=model,
        deep=deep,
    )
    try:
        return build_agent_cmd(
            prompt,
            runner=runner,
            agent=agent,
            model=resolved_model,
            workspace=REPO_ROOT,
        )
    except ValueError as e:
        die(str(e))


def _print_attention(title: str, *, reason: str, run_dir: Path,
                     status: str = "failed") -> None:
    print(f"\n{status_glyph(status)} {title}")
    print(f"   ├─ reason: {reason}")
    print(f"   └─ run: {format_file_ref(run_dir)}")


def _print_dry_run(eligible: list[dict], args, run_dir: Path) -> None:
    print("\n🧪 Dry run: no review agents were spawned")
    print(f"   ├─ runner: {args.runner}")
    print(f"   ├─ default model: {resolve_runner_model(runner=args.runner, explicit_model=args.agent_model, deep=False) or 'harness-default'}")
    print(f"   ├─ deep model: {resolve_runner_model(runner=args.runner, explicit_model=args.agent_model, deep=True) or 'harness-default'}")
    print(f"   ├─ detailed embeddings: {args.detailed}")
    print(f"   ├─ rebuild: {args.rebuild}")
    print(f"   ├─ auto deep: {args.auto_deep}")
    print(f"   ├─ parallel: {args.parallel}")
    print(f"   ├─ max reviews: {args.max_reviews}")
    if args.quiet_hours:
        print(f"   ├─ quiet hours: {args.quiet_hours}")
    if args.max_cost_usd is not None:
        print(f"   ├─ cost cap: ${args.max_cost_usd:.2f}")
    print(f"   └─ run: {format_file_ref(run_dir)}")
    if not eligible:
        print("   ⏭️  no eligible PRs")
        return
    print("\n   Would review:")
    for row in eligible:
        depth = "deep" if row.get("_adk_deep") else "standard"
        reason = row.get("_adk_deep_reason")
        suffix = f" ({reason})" if reason else ""
        work = row.get("_adk_work_mode") or "code"
        print(f"   ├─ {format_pr_ref(row.get('pr_url', ''))} · {work} · {depth}{suffix}")


def _print_review_result(result: dict) -> None:
    status = result.get("status")
    ref = format_pr_ref(result.get("pr_url", ""))
    elapsed = result.get("elapsed_s")
    log = result.get("log")
    parts = [f"{status_glyph(status)} {ref}"]
    if elapsed is not None:
        parts.append(f"{elapsed}s")
    if result.get("exit_code") is not None:
        parts.append(f"rc={result.get('exit_code')}")
    print("   ├─ " + " · ".join(parts))
    reason = result.get("reason") or result.get("error")
    if reason:
        print(f"   │  ⚠️  {reason}")
    if log:
        print(f"   │  └─ log: {format_file_ref(log)}")


def _mark_review_attempt(queue: str, pr_url: str, status: str, *,
                         work_mode: str | None = None, error: str | None = None) -> None:
    queue_path = Path(queue).expanduser()
    try:
        row = find_row(queue_path, pr_url)
        if row is None:
            return
        updates = {
            "last_review_attempt_at": _now_iso(),
            "last_review_attempt_status": status,
            "last_review_attempt_work_mode": work_mode,
            "last_review_attempt_head_sha": row.get("head_sha"),
            "last_review_attempt_comment_activity_hash": row.get("comment_activity_hash"),
        }
        if error is not None:
            updates["last_review_attempt_error"] = error
            updates["taken_at"] = None
            updates["taken_by"] = None
        update_pr_entry(queue_path, pr_url, updates)
    except Exception:
        return


def _spawn_review(pr_url: str, agent: str | None, run_dir: Path, log,
                  *, runner: str = "claude", model: str | None = None,
                  detailed: bool = False, deep: bool = False,
                  rebuild: bool = False,
                  deep_reason: str | None = None,
                  run_state_id: str | None = None,
                  queue: str = str(DEFAULT_QUEUE_PATH),
                  work_mode: str | None = None) -> dict:
    """Spawn one agent for one PR. Captures stdout/stderr to a log file
    under run_dir; returns a summary dict.
    """
    log_path = run_dir / f"{pr_url.replace('/', '_').replace(':', '')}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_model = resolve_runner_model(
        runner=runner,
        explicit_model=model,
        deep=deep,
    )
    cmd = _build_agent_cmd(
        pr_url,
        runner=runner,
        agent=agent,
        model=model,
        detailed=detailed,
        deep=deep,
        rebuild=rebuild,
        work_mode=work_mode,
    )
    if work_mode == WORK_COMMENTS:
        cmd = [
            PY, str(ADK_BIN), "pr-task", "review-comments", pr_url,
            "--queue", queue,
        ]
    if os.environ.get("ADK_VERBOSE") == "1":
        log.info("review %s", format_pr_ref(pr_url))
        log.info("$ %s", " ".join(shlex.quote(c) for c in cmd))
    worker_state_id = make_worker_state_id(run_state_id, pr_url) if run_state_id else None
    links = {
        "pr": pr_url,
        "log": file_link(log_path),
    }
    started = time.time()
    _mark_review_attempt(queue, pr_url, REVIEW_ATTEMPT_STARTED, work_mode=work_mode)
    try:
        with open(log_path, "w", encoding="utf-8") as fh:
            if worker_state_id:
                write_worker(worker_state_id, {
                    "run_id": run_state_id,
                    "pid": os.getpid(),
                    "task_type": "review",
                    "subject": pr_url,
                    "pr_url": pr_url,
                    "status": "running",
                    "current_phase": "context refresh",
                    "agent": runner,
                    "model": resolved_model,
                    "queue": queue,
                    "started_at": _now_iso(),
                    "log_path": str(log_path),
                    "links": links,
                    "artifacts": {},
                })
            if work_mode != WORK_COMMENTS:
                refresh_cmd = [
                    PY, str(ADK_BIN), "pr", "--queue", queue,
                    "context-refresh", pr_url, "--no-prepare",
                ]
                fh.write("$ " + " ".join(shlex.quote(c) for c in refresh_cmd) + "\n")
                fh.flush()
                refresh = subprocess.run(
                    refresh_cmd, stdout=fh, stderr=subprocess.STDOUT,
                    text=True, check=False,
                )
                if refresh.returncode != 0:
                    fh.write(f"(context-refresh exited rc={refresh.returncode}; continuing)\n")
                    fh.flush()
            if worker_state_id:
                update_worker(worker_state_id, {
                    "status": "running",
                    "current_phase": "review agent starting",
                })
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            if worker_state_id:
                update_worker(worker_state_id, {
                    "run_id": run_state_id,
                    "pid": proc.pid,
                    "task_type": "review",
                    "subject": pr_url,
                    "pr_url": pr_url,
                    "status": "running",
                    "current_phase": "spawned review agent",
                    "agent": runner,
                    "model": resolved_model,
                    "queue": queue,
                    "started_at": _now_iso(),
                    "log_path": str(log_path),
                    "links": links,
                    "artifacts": {},
                })
            next_heartbeat = time.time()
            current_phase = "spawned review agent"
            selector = selectors.DefaultSelector()
            if proc.stdout is not None:
                selector.register(proc.stdout, selectors.EVENT_READ)
            while proc.poll() is None:
                for key, _ in selector.select(timeout=0.2):
                    line = key.fileobj.readline()
                    if not line:
                        continue
                    fh.write(line)
                    fh.flush()
                    phase = _parse_phase_marker(line)
                    if worker_state_id and phase is not None:
                        current_phase = phase
                        update_worker(worker_state_id, {
                            "status": "running",
                            "current_phase": phase,
                        })
                if worker_state_id and time.time() >= next_heartbeat:
                    update_worker(worker_state_id, {
                        "status": "running",
                        "current_phase": current_phase,
                    })
                    next_heartbeat = time.time() + 5
            if proc.stdout is not None:
                for line in proc.stdout:
                    fh.write(line)
                    fh.flush()
                    phase = _parse_phase_marker(line)
                    if worker_state_id and phase is not None:
                        current_phase = phase
                        update_worker(worker_state_id, {
                            "status": "running",
                            "current_phase": phase,
                        })
            selector.close()
        elapsed = time.time() - started
        exit_code = proc.returncode
        if exit_code != 0:
            _mark_review_attempt(
                queue, pr_url, REVIEW_ATTEMPT_FAILED,
                work_mode=work_mode,
                error=extract_failure_reason(str(log_path)) or f"exit_code={exit_code}",
            )
        if worker_state_id:
            complete_worker(
                worker_state_id,
                status="ok" if exit_code == 0 else "failed",
                rc=exit_code,
                outcome="ok" if exit_code == 0 else "failed",
                current_phase="completed",
                links=links,
            )
        return {
            "pr_url": pr_url,
            "exit_code": exit_code,
            "elapsed_s": round(elapsed, 1),
            "log": str(log_path),
            "worker_id": worker_state_id,
            "model": resolved_model,
            "deep": deep,
            "deep_reason": deep_reason,
            "detailed": detailed,
            "work_mode": work_mode,
            "status": "ok" if exit_code == 0 else "failed",
        }
    except FileNotFoundError:
        if worker_state_id:
            complete_worker(
                worker_state_id,
                status="failed",
                rc=-1,
                outcome="spawn-error",
                current_phase="spawn error",
                error=f"agent binary '{cmd[0]}' not found on PATH",
                links=links,
            )
        _mark_review_attempt(
            queue, pr_url, REVIEW_ATTEMPT_FAILED,
            work_mode=work_mode,
            error=f"agent binary '{cmd[0]}' not found on PATH",
        )
        return {
            "pr_url": pr_url,
            "exit_code": -1,
            "status": "failed",
            "error": f"agent binary '{cmd[0]}' not found on PATH",
            "log": str(log_path),
            "worker_id": worker_state_id,
            "model": resolved_model,
            "deep": deep,
            "deep_reason": deep_reason,
            "detailed": detailed,
            "work_mode": work_mode,
        }
    except Exception as e:
        _mark_review_attempt(queue, pr_url, REVIEW_ATTEMPT_FAILED,
                             work_mode=work_mode, error=str(e))
        if worker_state_id:
            complete_worker(
                worker_state_id,
                status="failed",
                rc=-1,
                outcome="error",
                current_phase="error",
                error=str(e),
                links=links,
            )
        return {
            "pr_url": pr_url,
            "exit_code": -1,
            "status": "failed",
            "error": str(e),
            "log": str(log_path),
            "worker_id": worker_state_id,
            "model": resolved_model,
            "deep": deep,
            "deep_reason": deep_reason,
            "detailed": detailed,
            "work_mode": work_mode,
        }


def _run_pr_sync(*, queue: str, run_dir: Path, dashboard: RunDashboard,
                 log, args) -> int:
    sync_log = run_dir / "pr-sync.log"
    cmd = [PY, str(ADK_BIN), "pr-sync", "--queue", queue, "--quiet"]
    if args.detailed:
        cmd.append("--detailed")
    if args.deep:
        cmd.append("--deep")
    env = {**os.environ, "ADK_ORCHESTRATED": "1"}
    if os.environ.get("ADK_VERBOSE") == "1":
        log.info("sync queue: %s", " ".join(shlex.quote(c) for c in cmd))
    dashboard.apply({"kind": "step_start", "name": "pr-sync",
                     "status": "run", "detail": "starting"})
    dashboard.print_snapshot()
    with sync_log.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            fh.write(line)
            fh.flush()
            event = parse_event_line(line.strip())
            if event is not None:
                dashboard.apply(event)
                dashboard.print_snapshot()
        rc = proc.wait()
    status = "done" if rc == 0 else "warn"
    dashboard.apply({
        "kind": "step_done",
        "name": "pr-sync",
        "status": status,
        "detail": f"rc={rc}; log {format_file_ref(sync_log, label='pr-sync.log')}",
    })
    if rc != 0:
        dashboard.apply({
            "kind": "attention",
            "level": "warn",
            "title": "pr-sync exited non-zero; continuing to review eligible rows",
            "reason": f"rc={rc}",
            "log_path": str(sync_log),
        })
    dashboard.print_snapshot()
    return rc


def _write_report(run_dir: Path, results: list[dict], started: str, ended: str,
                  ran_sync: bool, dry_run: bool) -> Path:
    n_ok = sum(1 for r in results if r.get("status") == "ok")
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    md = run_dir / "report.md"
    lines = [
        "# adk pr-review-all — review run",
        "",
        f"- Started: `{started}`",
        f"- Ended: `{ended}`",
        f"- Reviews: {len(results)} (ok: {n_ok}, failed: {n_fail})",
        f"- Sync ran: {ran_sync}",
        f"- Dry run: {dry_run}",
        "",
        "## Per-PR results",
        "",
    ]
    for r in results:
        url = r.get("pr_url", "?")
        status = r.get("status", "?")
        ec = r.get("exit_code", "?")
        elapsed = r.get("elapsed_s", "?")
        line = f"- [{url}]({url}) — status: **{status}** · exit_code: {ec}"
        if elapsed != "?":
            line += f" · elapsed: {elapsed}s"
        reason = r.get("reason") or r.get("error")
        if reason:
            line += f" · reason: {reason}"
        if r.get("model"):
            line += f" · model: {r['model']}"
        if r.get("deep"):
            line += f" · deep: {r.get('deep_reason') or True}"
        if r.get("detailed"):
            line += " · detailed"
        lines.append(line)
        # Per-PR log link (file://) so the user can click through to the
        # spawned agent's output.
        if r.get("log"):
            lines.append(f"  - log: <file://{Path(r['log']).resolve()}>")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md


def _print_run_tail(run_dir: Path, results: list[dict], report_path: Path) -> None:
    """Print a scannable terminal summary at the end of every automated run.

    The compact PR labels are OSC-8 linked when the terminal supports it.
    """
    n_ok = sum(1 for r in results if r.get("status") == "ok")
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    headline = "completed" if n_fail == 0 else "completed with failures"
    print(f"\n{'✅' if n_fail == 0 else '⚠️'} adk pr-review-all {headline}")
    print(f"   ├─ reviewed: {len(results)}")
    print(f"   ├─ ok: {n_ok}")
    print(f"   ├─ failed: {n_fail}")
    print(f"   ├─ report: {format_file_ref(report_path)}")
    print(f"   └─ run dir: {format_file_ref(run_dir)}")
    if not results:
        return
    print("\n   PRs:")
    for r in results:
        _print_review_result(r)


def _cfg(key: str, default):
    """Read `pr_review_all.<key>` from adk-cli.json5; fall back to `default`."""
    try:
        from config_io import get_adk_cli  # noqa: WPS433
        return get_adk_cli("pr_review_all", key, default=default)
    except Exception:
        return default


def _cfg_bool(key: str, default: bool) -> bool:
    val = _cfg(key, default)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() not in {"0", "false", "no", "off"}
    return bool(val)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="adk pr-review-all",
        description="Headless review orchestrator. Runs pr-sync + spawns "
                    "agents to review eligible PRs. No interactive input. "
                    "Scheduler-friendly. Constitution §I.3: never merges.",
    )
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH),
                    help="path to pr-queue.json5")
    ap.add_argument("--max-reviews", type=int,
                    default=int(_cfg("max_reviews", 20)),
                    help="cap on number of PRs reviewed in this run "
                         "(default: pr_review_all.max_reviews, fallback 20)")
    ap.add_argument("--parallel", type=int,
                    default=int(_cfg("parallel", 1)),
                    help="number of concurrent agent subprocesses "
                         "(default: pr_review_all.parallel, fallback 1)")
    ap.add_argument("--runner",
                    choices=("claude", "cursor", "codex", "custom"),
                    default=_cfg("runner", _cfg("agent_runner", "claude")),
                    help="agent runner interface to use (default: pr_review_all.runner, fallback 'claude')")
    ap.add_argument("--agent", default=_cfg("agent", None),
                    help="override runner binary. Defaults: claude, cursor, codex. "
                         "With --runner custom, receives '-p /adk-pr-review <url>'.")
    ap.add_argument("--agent-model", default=_cfg("agent_model", "inherit"),
                    help="optional model passed to runners that support it. "
                         "Use 'inherit' (default) to omit --model and let the harness choose.")
    ap.add_argument("--detailed", action="store_true",
                    help="forward --detailed to /adk-pr-review; controls programmatic "
                         "retrieval detail such as the PR embed model.")
    ap.add_argument("--deep", action="store_true",
                    help="force the deep model profile for every spawned review "
                         "(Claude=Opus, Cursor=GPT 5.5 by default).")
    ap.add_argument("--rebuild", "--fresh", action="store_true",
                    help="force a fresh full rerun/reindex instead of resuming cached prep")
    ap.add_argument("--no-auto-deep", dest="auto_deep", action="store_false",
                    default=_cfg_bool("auto_deep", True),
                    help="disable automatic --deep for large or high-risk PRs.")
    ap.add_argument("--exclude", action="append", default=[],
                    help="PR URL to skip (repeat for several)")
    ap.add_argument("--pr", default=None,
                    help="review only this PR URL (skips queue eligibility "
                         "scan). The URL must already exist in the queue.")
    ap.add_argument("--no-sync", action="store_true",
                    help="skip the pre-flight `adk pr-sync` step")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen; spawn no agents")
    ap.add_argument("--quiet-hours", default=_cfg("quiet_hours", None),
                    help="refuse to spawn during this local-clock window (e.g. '00-08' "
                         "= 00:00 ≤ now < 08:00; '22-06' wraps around midnight). "
                         "Useful so a scheduled job doesn't ping people overnight. "
                         "(default: pr_review_all.quiet_hours, fallback none)")
    ap.add_argument("--max-cost-usd", type=float,
                    default=_cfg("max_cost_usd", None),
                    help="abort with rc=2 if the pre-flight estimate "
                         "(per-agent coefficient × eligible PR count) exceeds this. "
                         "Conservative; doesn't account for retries. "
                         "(default: pr_review_all.max_cost_usd, fallback none)")
    ap.add_argument("--report-to-slack",
                    default=_cfg("report_to_slack", None),
                    help="post a summary to this Slack channel (e.g. '#pr-reviews') "
                         "at the end of the run. Requires SLACK_BOT_TOKEN_CRED. "
                         "(default: pr_review_all.report_to_slack, fallback none)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to $ADK_DATA_HOME/logs/")
    args = ap.parse_args(argv)
    guard_json = bool(args.quiet_hours or args.max_cost_usd is not None or args.report_to_slack)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-review-all", enabled=True, argv=argv)
        os.environ["ADK_VERBOSE"] = "1"

    log = get_logger("pr-review-all")
    started_ts = _now_iso()
    run_id = _ts_for_run()
    state_run_id = make_run_state_id("pr-review-all")
    run_dir = AUTO_RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dashboard = RunDashboard(
        run_id=run_id,
        queue=args.queue,
        runner=args.runner,
        parallel=args.parallel,
        selected=0,
        run_dir=run_dir,
    )
    write_run(state_run_id, {
        "task_type": "pr-review-all",
        "status": "running",
        "started_by": "cli",
        "queue": args.queue,
        "runner": args.runner,
        "agent": args.agent,
        "model_mode": args.agent_model or ("deep" if args.deep else "inherit"),
        "model": resolve_runner_model(
            runner=args.runner,
            explicit_model=args.agent_model,
            deep=args.deep,
        ),
        "parallel": args.parallel,
        "started_at": started_ts,
        "run_dir": str(run_dir),
        "links": {"run_dir": file_link(run_dir)},
        "steps": [{"name": "start", "status": "ok", "completed_at": started_ts}],
        "workers": [],
    })
    pf = preflight(
        "adk-pr-review",
        runner=args.runner,
        agent=args.agent,
        model=args.agent_model,
        deep=args.deep,
    )
    update_run(state_run_id, {"preflight": pf})
    if not guard_json:
        dashboard.print_snapshot()

    # Quiet hours guard — refuse to spawn if we're inside the window.
    if args.quiet_hours:
        try:
            if _in_quiet_hours(args.quiet_hours):
                if guard_json:
                    print(json.dumps({
                        "action": "aborted",
                        "reason": f"quiet-hours {args.quiet_hours}",
                        "quiet_hours": args.quiet_hours,
                    }))
                else:
                    _print_attention(
                        "Run paused by quiet hours",
                        reason=f"inside quiet-hours window ({args.quiet_hours})",
                        run_dir=run_dir,
                        status="skipped",
                    )
                update_run(state_run_id, {
                    "status": "skipped",
                    "completed_at": _now_iso(),
                    "steps": [{"name": "quiet-hours", "status": "skipped"}],
                })
                return 2
        except ValueError as e:
            if guard_json:
                print(json.dumps({"action": "aborted", "reason": str(e)}))
            else:
                _print_attention("Run aborted", reason=str(e), run_dir=run_dir)
            update_run(state_run_id, {
                "status": "failed",
                "completed_at": _now_iso(),
                "error": str(e),
            })
            return 2

    # Step 1: pr-sync (optional).
    ran_sync = False
    if not args.no_sync and not args.dry_run:
        update_run(state_run_id, {
            "steps": [{
                "name": "pr-sync",
                "status": "running",
                "started_at": _now_iso(),
                "log_path": str(run_dir / "pr-sync.log"),
            }],
        })
        rc = _run_pr_sync(queue=args.queue, run_dir=run_dir,
                          dashboard=dashboard, log=log, args=args)
        if rc != 0:
            log.warning("pr-sync exited rc=%d; continuing anyway", rc)
        update_run(state_run_id, {
            "steps": [{"name": "pr-sync",
                       "status": "ok" if rc == 0 else "warn",
                       "rc": rc,
                       "log_path": str(run_dir / "pr-sync.log"),
                       "completed_at": _now_iso()}],
        })
        ran_sync = True

    # Step 2: enumerate eligible rows.
    queue_path = Path(args.queue).expanduser()
    if args.pr:
        # Target one named PR — bypass the eligibility scan but still require
        # the URL to be a known queue row, so we never review something the
        # queue hasn't seen (and so the post-review write-back finds a home).
        from queue_io import read_queue  # noqa: WPS433
        queue = read_queue(queue_path)
        match = next((r for r in (queue.get("prs") or [])
                      if r.get("pr_url") == args.pr), None)
        if match is None:
            _print_attention(
                "Run aborted",
                reason=(f"{format_pr_ref(args.pr)} is not in the queue. "
                        f"Run `adk pr-queue add {args.pr}` first, then retry."),
                run_dir=run_dir,
            )
            return 2
        eligible = [match]
    else:
        eligible = _eligible_rows(queue_path, exclude=set(args.exclude))
        if len(eligible) > args.max_reviews:
            eligible = eligible[:args.max_reviews]
    _annotate_depth(eligible, args)
    update_run(state_run_id, {
        "eligible": len(eligible),
        "selected": len(eligible),
    })

    # Cost guard — pre-flight estimate × eligible count.
    if args.max_cost_usd is not None and eligible:
        cost_per = AGENT_COST_USD.get(
            _runner_cost_key(args.runner, args.agent or args.runner),
            0.50,
        )
        estimated = sum(cost_per * (2.0 if e.get("_adk_deep") else 1.0)
                        for e in eligible)
        if estimated > args.max_cost_usd:
            reason = (f"max-cost-usd: estimated ${estimated:.2f} exceeds cap "
                      f"${args.max_cost_usd:.2f}; runner={args.runner}, "
                      f"agent={args.agent or args.runner}, "
                      f"per_review=${cost_per:.2f}, eligible={len(eligible)}, "
                      f"deep={sum(1 for e in eligible if e.get('_adk_deep'))}")
            if guard_json:
                print(json.dumps({"action": "aborted", "reason": reason,
                                  "runner": args.runner,
                                  "max_cost_usd": args.max_cost_usd}))
            else:
                _print_attention("Run aborted by cost guard", reason=reason, run_dir=run_dir)
            update_run(state_run_id, {
                "status": "failed",
                "completed_at": _now_iso(),
                "error": "cost guard exceeded",
            })
            return 2

    if args.dry_run:
        dashboard.selected = len(eligible)
        if guard_json:
            print(json.dumps({
                "action": "dry_run",
                "runner": args.runner,
                "quiet_hours": args.quiet_hours,
                "max_cost_usd": args.max_cost_usd,
                "report_to_slack": args.report_to_slack,
                "eligible": [e.get("pr_url") for e in eligible],
                "parallel": args.parallel,
                "max_reviews": args.max_reviews,
            }))
        else:
            _print_dry_run(eligible, args, run_dir)
        update_run(state_run_id, {
            "status": "dry-run",
            "completed_at": _now_iso(),
            "selected": len(eligible),
        })
        return 0

    if not eligible:
        _print_attention("No eligible PRs", reason="queue has nothing ready for review",
                         run_dir=run_dir, status="skipped")
        update_run(state_run_id, {
            "status": "skipped",
            "completed_at": _now_iso(),
            "selected": 0,
        })
        return 0

    if pf["status"] == "blocked":
        _print_attention(
            "Run aborted by preflight",
            reason=", ".join(item.get("name") or item.get("detail", "gap")
                             for item in pf.get("blockers", [])),
            run_dir=run_dir,
        )
        update_run(state_run_id, {
            "status": "failed",
            "completed_at": _now_iso(),
            "error": "preflight blocked",
        })
        return 2

    dashboard.selected = len(eligible)
    for e in eligible:
        dashboard.apply({"kind": "pr_wait", "pr_url": e.get("pr_url", ""),
                         "status": "wait", "stage": "selected"})
    dashboard.print_snapshot()

    # Step 3: spawn agents.
    results: list[dict] = []
    if args.parallel <= 1:
        for e in eligible:
            dashboard.apply({"kind": "pr_active", "pr_url": e["pr_url"],
                             "status": "run", "stage": "review agent",
                             "detail": "agent subprocess running"})
            dashboard.print_snapshot()
            result = _spawn_review(
                e["pr_url"], args.agent, run_dir, log,
                runner=args.runner, model=args.agent_model,
                detailed=args.detailed,
                rebuild=args.rebuild,
                deep=bool(e.get("_adk_deep")),
                deep_reason=e.get("_adk_deep_reason"),
                run_state_id=state_run_id,
                queue=args.queue,
                work_mode=e.get("_adk_work_mode"),
            )
            if result.get("status") == "ok":
                dashboard.apply({"kind": "pr_done", "pr_url": e["pr_url"],
                                 "status": "done", "stage": "review agent",
                                 "elapsed_s": result.get("elapsed_s")})
            else:
                reason = result.get("error") or extract_failure_reason(result.get("log", ""))
                result["reason"] = reason
                dashboard.apply({"kind": "pr_fail", "pr_url": e["pr_url"],
                                 "status": "fail", "stage": "review agent",
                                 "reason": reason,
                                 "next_action": "open the child log or rerun this PR",
                                 "log_path": result.get("log", ""),
                                 "elapsed_s": result.get("elapsed_s")})
            dashboard.print_snapshot()
            results.append(result)
    else:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futs = {
                pool.submit(
                    _spawn_review, e["pr_url"], args.agent, run_dir, log,
                    runner=args.runner, model=args.agent_model,
                    detailed=args.detailed,
                    rebuild=args.rebuild,
                    deep=bool(e.get("_adk_deep")),
                    deep_reason=e.get("_adk_deep_reason"),
                    run_state_id=state_run_id,
                    queue=args.queue,
                    work_mode=e.get("_adk_work_mode"),
                ): e for e in eligible
            }
            for e in eligible:
                dashboard.apply({"kind": "pr_active", "pr_url": e["pr_url"],
                                 "status": "run", "stage": "review agent",
                                 "detail": "agent subprocess running"})
            dashboard.print_snapshot()
            for fut in as_completed(futs):
                e = futs[fut]
                result = fut.result()
                if result.get("status") == "ok":
                    dashboard.apply({"kind": "pr_done", "pr_url": e["pr_url"],
                                     "status": "done", "stage": "review agent",
                                     "elapsed_s": result.get("elapsed_s")})
                else:
                    reason = result.get("error") or extract_failure_reason(result.get("log", ""))
                    result["reason"] = reason
                    dashboard.apply({"kind": "pr_fail", "pr_url": e["pr_url"],
                                     "status": "fail", "stage": "review agent",
                                     "reason": reason,
                                     "next_action": "open the child log or rerun this PR",
                                     "log_path": result.get("log", ""),
                                     "elapsed_s": result.get("elapsed_s")})
                dashboard.print_snapshot()
                results.append(result)

    # Step 4: aggregate report.
    ended_ts = _now_iso()
    report_path = _write_report(run_dir, results, started_ts, ended_ts,
                                ran_sync, dry_run=False)
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    update_run(state_run_id, {
        "status": "failed" if n_fail else "ok",
        "completed_at": ended_ts,
        "workers": [r.get("worker_id") for r in results if r.get("worker_id")],
        "results": results,
        "artifacts": {"report": str(report_path)},
        "links": {
            "run_dir": file_link(run_dir),
            "report": file_link(report_path),
        },
    })
    slack_summary = None

    # Step 5: optional Slack summary post.
    if args.report_to_slack:
        try:
            _post_slack_summary(args.report_to_slack, results, report_path, log)
            slack_summary = "posted"
        except Exception as e:
            log.warning("slack summary post failed: %s", e)
            slack_summary = f"failed: {e}"

    _print_run_tail(run_dir, results, report_path)
    if slack_summary:
        print(f"   Slack summary: {slack_summary}")
    return 1 if n_fail else 0


def _post_slack_summary(channel: str, results: list[dict], report_path: Path, log) -> None:
    """Post a one-liner summary to the configured channel."""
    n_ok = sum(1 for r in results if r.get("status") == "ok")
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    glyph = "✅" if n_fail == 0 else "⚠"
    lines = [
        f"{glyph} *adk pr-review-all* — reviewed {len(results)} PR(s): {n_ok} ok, {n_fail} failed",
    ]
    for r in results:
        s = r.get("status", "?")
        bullet = "•" if s == "ok" else "❌"
        lines.append(f"{bullet} {r.get('pr_url', '?')}")
    lines.append(f"• report: `{report_path}`")
    text = "\n".join(lines)

    # Lazy import — only when --report-to-slack is set.
    from slack_helpers import SlackClient  # type: ignore
    client = SlackClient()
    channel_id = client.resolve_channel(channel)
    client.post_thread_reply(channel_id, "", text)  # not a thread; top-level
    # Note: post_thread_reply takes thread_ts="" → it'll post as top-level.
    # If that doesn't work cleanly, we fall back to the same SDK call directly.
    log.info("posted adk pr-review-all summary to %s", channel)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
