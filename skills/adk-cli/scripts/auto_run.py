"""auto_run.py — `adk auto` headless review orchestrator.

Per `docs/plans/adk-v4-overhaul.md` §7: runs the full pipeline without
interactive input. Scheduler-friendly (cron, launchd, GitHub Action).

Flow:
  1. `adk pr-sync` — runs the full DAG (Phase A→F).
  2. Enumerate non-terminal queue rows where `ready_for_review` holds
     (§6.u eligibility predicate from queue_io.py).
  3. Apply guards: --max-reviews, --exclude, --dry-run.
  4. For each eligible PR (up to --max-reviews), spawn:
        <agent> -p "/adk-pr-review <pr_url>"
     Default agent: claude. Configurable via --agent.
  5. Capture per-PR exit code + stdout last line.
  6. Aggregate to `~/.agents-devkit/skill-setup/auto-runs/<ts>/report.md`.

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

from _common import die, get_logger  # type: ignore  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, read_queue, ready_for_review, TERMINAL_STATUSES,
)

PY = sys.executable
ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
AUTO_RUNS_ROOT = ADK_HOME / "skill-setup" / "auto-runs"
REPO_ROOT = THIS_DIR.parent.parent.parent
ADK_BIN = REPO_ROOT / "bin" / "adk"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _ts_for_run() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def _eligible_rows(queue_path: Path, *, exclude: set[str]) -> list[dict]:
    """Return non-terminal rows passing ready_for_review, minus excluded URLs.

    FIFO order: oldest last_checked_at first; null (never reviewed) first.
    """
    q = read_queue(queue_path)
    prs = q.get("prs", []) or []
    eligible = []
    for e in prs:
        if (e.get("status") or "") in TERMINAL_STATUSES:
            continue
        if e.get("pr_url") in exclude:
            continue
        if not ready_for_review(e):
            continue
        eligible.append(e)
    # Sort: nulls first, then by last_checked_at ascending.
    def _key(row):
        lc = row.get("last_checked_at")
        return (1, str(lc)) if lc else (0, "")
    eligible.sort(key=_key)
    return eligible


def _spawn_review(pr_url: str, agent: str, run_dir: Path, log) -> dict:
    """Spawn one agent for one PR. Captures stdout/stderr to a log file
    under run_dir; returns a summary dict.
    """
    log_path = run_dir / f"{pr_url.replace('/', '_').replace(':', '')}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [agent, "-p", f"/adk-pr-review {pr_url}"]
    log.info("$ %s", " ".join(cmd))
    started = time.time()
    try:
        with open(log_path, "w", encoding="utf-8") as fh:
            cp = subprocess.run(
                cmd, stdout=fh, stderr=subprocess.STDOUT,
                text=True, check=False,
            )
        elapsed = time.time() - started
        return {
            "pr_url": pr_url,
            "exit_code": cp.returncode,
            "elapsed_s": round(elapsed, 1),
            "log": str(log_path),
            "status": "ok" if cp.returncode == 0 else "failed",
        }
    except FileNotFoundError:
        return {
            "pr_url": pr_url,
            "exit_code": -1,
            "status": "failed",
            "error": f"agent binary '{agent}' not found on PATH",
            "log": str(log_path),
        }
    except Exception as e:
        return {
            "pr_url": pr_url,
            "exit_code": -1,
            "status": "failed",
            "error": str(e),
            "log": str(log_path),
        }


def _write_report(run_dir: Path, results: list[dict], started: str, ended: str,
                  ran_sync: bool, dry_run: bool) -> Path:
    n_ok = sum(1 for r in results if r.get("status") == "ok")
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    md = run_dir / "report.md"
    lines = [
        "# adk auto — review run",
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
        line = f"- `{url}` — status: **{status}** · exit_code: {ec}"
        if elapsed != "?":
            line += f" · elapsed: {elapsed}s"
        if r.get("error"):
            line += f" · error: {r['error']}"
        lines.append(line)
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="adk auto",
        description="Headless review orchestrator. Runs pr-sync + spawns "
                    "agents to review eligible PRs. No interactive input. "
                    "Scheduler-friendly. Constitution §I.3: never merges.",
    )
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH),
                    help="path to pr-queue.json5")
    ap.add_argument("--max-reviews", type=int, default=20,
                    help="cap on number of PRs reviewed in this run (default: 20)")
    ap.add_argument("--parallel", type=int, default=1,
                    help="number of concurrent agent subprocesses (default: 1; "
                         "1 = serial)")
    ap.add_argument("--agent", default="claude",
                    help="agent binary to spawn for each PR (default: claude). "
                         "Receives '-p /adk-pr-review <url>'")
    ap.add_argument("--exclude", action="append", default=[],
                    help="PR URL to skip (repeat for several)")
    ap.add_argument("--no-sync", action="store_true",
                    help="skip the pre-flight `adk pr-sync` step")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen; spawn no agents")
    args = ap.parse_args(argv)

    log = get_logger("adk-auto")
    started_ts = _now_iso()
    run_id = _ts_for_run()
    run_dir = AUTO_RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log.info("auto run %s starting; queue=%s", run_id, args.queue)

    # Step 1: pr-sync (optional).
    ran_sync = False
    if not args.no_sync and not args.dry_run:
        log.info("$ adk pr-sync")
        rc = subprocess.run([PY, str(ADK_BIN), "pr-sync"]).returncode
        if rc != 0:
            log.warning("pr-sync exited rc=%d; continuing anyway", rc)
        ran_sync = True

    # Step 2: enumerate eligible rows.
    queue_path = Path(args.queue).expanduser()
    eligible = _eligible_rows(queue_path, exclude=set(args.exclude))
    if len(eligible) > args.max_reviews:
        eligible = eligible[:args.max_reviews]

    if args.dry_run:
        out = {
            "action": "dry_run",
            "would_review": [e.get("pr_url") for e in eligible],
            "count": len(eligible),
            "agent": args.agent,
            "parallel": args.parallel,
            "max_reviews": args.max_reviews,
            "run_dir": str(run_dir),
        }
        print(json.dumps(out, indent=2))
        return 0

    if not eligible:
        out = {"action": "noop", "reason": "no eligible PRs", "run_dir": str(run_dir)}
        print(json.dumps(out, indent=2))
        return 0

    # Step 3: spawn agents.
    results: list[dict] = []
    if args.parallel <= 1:
        for e in eligible:
            results.append(_spawn_review(e["pr_url"], args.agent, run_dir, log))
    else:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futs = {pool.submit(_spawn_review, e["pr_url"], args.agent, run_dir, log): e
                    for e in eligible}
            for fut in as_completed(futs):
                results.append(fut.result())

    # Step 4: aggregate report.
    ended_ts = _now_iso()
    report_path = _write_report(run_dir, results, started_ts, ended_ts,
                                ran_sync, dry_run=False)
    n_fail = sum(1 for r in results if r.get("status") == "failed")
    summary = {
        "action": "completed",
        "run_dir": str(run_dir),
        "report": str(report_path),
        "reviews": len(results),
        "ok": sum(1 for r in results if r.get("status") == "ok"),
        "failed": n_fail,
    }
    print(json.dumps(summary, indent=2))
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
