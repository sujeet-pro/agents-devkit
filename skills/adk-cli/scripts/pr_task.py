"""pr_task.py — `adk pr-task` subcommands.

The stable CLI surface for managing the per-PR task folder under
~/.agents-devkit/skill-pr-review/<repo>_pr-<n>/. The /adk-pr-review skill calls
through this binary so it doesn't depend on internal script paths.

prepare <pr-url>     Create or refresh the task folder for one PR. Runs the
                     same Phase 0-4a prep that /adk-pr-review's orchestrator
                     would: clone fetch, worktree at the PR head, PR metadata
                     + comments + diff, supporting docs index, tree-sitter
                     chunks + ollama embeddings + (optional) SCIP, precis.md.
                     Does NOT claim the queue's `taken_at` lock and does NOT
                     run a review. Idempotent: re-running on an unchanged
                     head_sha short-circuits the index step.

info <pr-url>        JSON view of a task folder's current state: paths,
                     head_sha, last_indexed_head, whether findings.json
                     exists. Used by the skill (and by humans) to decide
                     whether the folder is ready for an interactive review.

list                 Names of every task folder under
                     ~/.agents-devkit/skill-pr-review/. Pair with `--paths` to
                     get the full paths instead. Powers shell completion.

Internals: prepare delegates to skills/adk-pr-review/scripts/run_review.py
--prepare-only. This module is a stable wrapper — the skill (and any
external caller) doesn't need to know that path.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
SCRIPTS_ROOT = THIS_DIR.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import parse_pr_url, task_dir_for, die, get_logger, ADK_HOME, read_state  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, STATUS_MERGED, STATUS_PENDING,
    TERMINAL_STATUSES, read_queue,
)


def _default_prepare_jobs() -> int:
    """Read `pr_sync.prepare_jobs` from `~/.agents-devkit/config/core.yaml`.
    Returns 1 if the file or key is absent (today's behavior). The bound is
    enforced at the cmd_prepare seam — this helper just resolves the default.
    """
    try:
        from config_io import load_core  # noqa: WPS433
        cfg = load_core() or {}
        val = (cfg.get("pr_sync") or {}).get("prepare_jobs")
        if val is None:
            return 1
        return max(1, int(val))
    except Exception:
        return 1

# v4: per-skill task root is skill-pr-review/ (was pr-reviews/ pre-v4).
# Falls back to the legacy path when only it exists on disk, so the user's
# in-flight task folders survive between P2 landing and P7 migrating.
PR_REVIEW_ROOT = ADK_HOME / "skill-pr-review"
LEGACY_PR_REVIEW_ROOT = ADK_HOME / "pr-reviews"


def _resolve_pr_review_root() -> Path:
    """Return the live task root. Prefer skill-pr-review/; fall back to the
    legacy pr-reviews/ ONLY if the new one is absent and the legacy one
    exists. Once P7 migrates, the legacy path goes away.
    """
    if PR_REVIEW_ROOT.exists():
        return PR_REVIEW_ROOT
    if LEGACY_PR_REVIEW_ROOT.exists():
        return LEGACY_PR_REVIEW_ROOT
    return PR_REVIEW_ROOT


PR_REVIEWS_ROOT = PR_REVIEW_ROOT  # legacy import name; new code uses _resolve_pr_review_root().
RUN_REVIEW = ADK_PR_REVIEW_SCRIPTS / "run_review.py"
VALIDATE_FINDINGS = ADK_PR_REVIEW_SCRIPTS / "validate_findings.py"


def _queued_task_dirs(queue_path: Path) -> dict[str, Path]:
    """Map of `pr_url → task_dir` for every non-merged row in the queue.

    Used by `prepare --all` (iterate eligible rows) and `clean-orphans`
    (decide which folders on disk no longer have a backing queue row).
    """
    out: dict[str, Path] = {}
    queue = read_queue(queue_path)
    for e in queue.get("prs", []) or []:
        link = e.get("pr_url")
        if not link:
            continue
        # Skip rows that have reached a terminal state (merged or declined).
        # Their task folders will be reaped by `pr-queue clean` /
        # `pr-task clean-orphans` later in the sync pipeline.
        if (e.get("status") or STATUS_PENDING) in TERMINAL_STATUSES:
            continue
        try:
            p = parse_pr_url(link)
        except ValueError:
            continue
        out[link] = task_dir_for(p["repo"], p["pr_number"])
    return out


def _task_dir_for(pr_url: str) -> Path:
    p = parse_pr_url(pr_url)
    return task_dir_for(p["repo"], p["pr_number"])


# ----- prepare -------------------------------------------------------------

def _prepare_one(pr_url: str, *, queue: str, rebuild: bool, detailed: bool,
                 embed_model: str | None, log) -> dict:
    """Spawn run_review.py --prepare-only for one PR. Returns a structured
    dict so the --all caller can aggregate. Never raises."""
    cmd = [sys.executable, str(RUN_REVIEW), "--prepare-only",
           "--queue", str(Path(queue).expanduser())]
    if rebuild:
        cmd.append("--rebuild")
    if detailed:
        cmd.append("--detailed")
    if embed_model:
        cmd += ["--embed-model", embed_model]
    cmd.append(pr_url)

    log.info("$ %s --prepare-only %s", RUN_REVIEW.name, pr_url)
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        return {"pr_url": pr_url, "status": "failed", "reason": str(e)}
    if cp.returncode != 0:
        return {"pr_url": pr_url, "status": "failed",
                "reason": (cp.stderr or cp.stdout or "")[-400:]}
    last_line = (cp.stdout or "").strip().splitlines()[-1:] or [""]
    try:
        body = json.loads(last_line[0])
        return {"pr_url": pr_url, **body}
    except Exception:
        return {"pr_url": pr_url, "status": "prepared",
                "raw": last_line[0][-200:]}


def cmd_prepare(args) -> int:
    log = get_logger("pr-task-prepare")
    if not RUN_REVIEW.exists():
        die(f"run_review.py not found at {RUN_REVIEW} — check your install")

    if args.all:
        if args.pr_url:
            die("pass either <pr-url> or --all, not both")
        queued = _queued_task_dirs(Path(args.queue).expanduser())
        if not queued:
            print(json.dumps({"prepared": [], "reason": "no non-merged rows"},
                             indent=2))
            return 0
        urls = list(queued)
        jobs = args.jobs if args.jobs is not None else _default_prepare_jobs()
        jobs = max(1, min(jobs, len(urls)))
        log.info("preparing %d task folder(s) (jobs=%d)", len(urls), jobs)
        results: list[dict] = []
        had_failure = False

        if jobs == 1:
            for url in urls:
                r = _prepare_one(url, queue=args.queue, rebuild=args.rebuild,
                                 detailed=args.detailed,
                                 embed_model=args.embed_model, log=log)
                if r.get("status") == "failed":
                    had_failure = True
                results.append(r)
        else:
            # Each worker spawns its own run_review.py subprocess. Effective
            # parallelism is capped further by (1) the per-repo clone lock
            # held briefly during Phase 1a/1b in run_review and (2) Ollama's
            # OLLAMA_NUM_PARALLEL for concurrent embed requests. Failures are
            # isolated by _prepare_one (it never raises).
            total = len(urls)
            done = 0
            with ThreadPoolExecutor(max_workers=jobs) as ex:
                futures = {
                    ex.submit(_prepare_one, url,
                              queue=args.queue, rebuild=args.rebuild,
                              detailed=args.detailed,
                              embed_model=args.embed_model, log=log): url
                    for url in urls
                }
                for fut in as_completed(futures):
                    url = futures[fut]
                    done += 1
                    try:
                        r = fut.result()
                    except Exception as e:
                        r = {"pr_url": url, "status": "failed",
                             "reason": f"worker exception: {e}"}
                    if r.get("status") == "failed":
                        had_failure = True
                        log.warning("(%d/%d) failed %s: %s", done, total, url,
                                    (r.get("reason") or "")[:200])
                    else:
                        log.info("(%d/%d) prepared %s", done, total, url)
                    results.append(r)

        print(json.dumps({"prepared": results, "count": len(results)},
                         indent=2, default=str))
        return 1 if had_failure else 0

    if not args.pr_url:
        die("missing <pr-url>. Pass a URL or `--all`.")

    # Single-PR path: stream stdout/stderr through unchanged so the caller
    # sees the orchestrator's live phase log, not just the trailing JSON.
    cmd = [sys.executable, str(RUN_REVIEW), "--prepare-only",
           "--queue", str(Path(args.queue).expanduser())]
    if args.rebuild:
        cmd.append("--rebuild")
    if args.detailed:
        cmd.append("--detailed")
    if args.embed_model:
        cmd += ["--embed-model", args.embed_model]
    cmd.append(args.pr_url)
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode


# ----- validate ------------------------------------------------------------

def cmd_validate(args) -> int:
    """Phase 3 gate: drop findings whose anchor drifted or whose suggested
    fix isn't actionable. Reads `<task_dir>/findings.json` (agent's Phase 2
    output) and writes `validated-findings.json` + `initial-findings.json`.
    """
    if not VALIDATE_FINDINGS.exists():
        die(f"validate_findings.py not found at {VALIDATE_FINDINGS} — check your install")
    task_dir = _task_dir_for(args.pr_url)
    if not task_dir.exists():
        die(f"task dir not found: {task_dir} — run `adk pr-task prepare {args.pr_url}` first")
    log = get_logger("pr-task-validate")
    cmd = [sys.executable, str(VALIDATE_FINDINGS),
           "--task-dir", str(task_dir), "--json"]
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode


# ----- clean-orphans -------------------------------------------------------

def cmd_clean_orphans(args) -> int:
    """Drop task folders under ~/.agents-devkit/skill-pr-review/ that no longer
    have a matching queue row (or whose row is merged). Idempotent."""
    log = get_logger("pr-task-clean-orphans")
    root = _resolve_pr_review_root()
    if not root.exists():
        print(json.dumps({"removed": [], "reason": "no task folders"}, indent=2))
        return 0

    queued = _queued_task_dirs(Path(args.queue).expanduser())
    queued_names = {p.name for p in queued.values()}

    candidates = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if d.name in queued_names:
            continue
        candidates.append(d)

    if not candidates:
        print(json.dumps({"removed": [], "count": 0, "reason": "no orphans"},
                         indent=2))
        return 0

    if args.dry_run:
        print(json.dumps({"would_remove": [str(d) for d in candidates],
                          "count": len(candidates)}, indent=2))
        return 0

    if not args.yes:
        print(f"About to remove {len(candidates)} orphan task folder(s):")
        for d in candidates:
            print(f"  - {d}")
        print("Re-run with --yes to confirm (or --dry-run to preview).")
        return 2

    import shutil
    removed = []
    failed = []
    for d in candidates:
        try:
            shutil.rmtree(d)
            removed.append(str(d))
        except OSError as e:
            failed.append({"path": str(d), "error": str(e)})
            log.warning("failed to remove %s: %s", d, e)

    print(json.dumps({"removed": removed, "failed": failed,
                      "count": len(removed)}, indent=2))
    return 1 if failed else 0


# ----- info ----------------------------------------------------------------

def cmd_info(args) -> int:
    task_dir = _task_dir_for(args.pr_url)
    info = {
        "pr_url": args.pr_url,
        "task_dir": str(task_dir),
        "exists": task_dir.exists(),
    }
    if task_dir.exists():
        pr_json = task_dir / "pr.json"
        precis = task_dir / "precis.md"
        findings = task_dir / "findings.json"
        info.update({
            "has_pr_json": pr_json.exists(),
            "has_precis": precis.exists(),
            "has_findings": findings.exists(),
        })
        # head_sha + last index head come from state.json (phase markers).
        state = read_state(task_dir) or {}
        phases = state.get("phases") or {}
        fetch_phase = phases.get("2a_fetch_pr") or {}
        index_phase = phases.get("3_index") or {}
        if fetch_phase.get("head_sha"):
            info["head_sha"] = fetch_phase["head_sha"]
        if index_phase.get("head_sha_at_index"):
            info["last_indexed_head"] = index_phase["head_sha_at_index"]
        if pr_json.exists():
            try:
                pr = json.loads(pr_json.read_text(encoding="utf-8"))
                info["title"] = pr.get("title")
                info["state"] = pr.get("state") or pr.get("status")
            except Exception:
                pass
    print(json.dumps(info, indent=2, default=str))
    return 0


# ----- list ----------------------------------------------------------------

def cmd_list(args) -> int:
    root = _resolve_pr_review_root()
    if not root.exists():
        if args.names_only or args.paths:
            return 0
        print("(no task folders)")
        return 0
    folders = sorted(d for d in root.iterdir()
                     if d.is_dir() and not d.name.startswith("."))
    if args.names_only:
        for f in folders:
            print(f.name)
        return 0
    if args.paths:
        for f in folders:
            print(f)
        return 0
    if not folders:
        print("(no task folders)")
        return 0
    rows = []
    for f in folders:
        state = read_state(f) or {}
        phases = state.get("phases") or {}
        head = (phases.get("2a_fetch_pr") or {}).get("head_sha") or "-"
        idx_head = (phases.get("3_index") or {}).get("head_sha_at_index") or "-"
        has_findings = (f / "findings.json").exists()
        rows.append((f.name, head[:12], idx_head[:12], "✓" if has_findings else "-"))
    w_name = max(len(r[0]) for r in rows + [("task", "", "", "")])
    print(f"{'task'.ljust(w_name)}  {'head':<12}  {'index':<12}  findings")
    print(f"{'-' * w_name}  {'-' * 12}  {'-' * 12}  --------")
    for r in rows:
        print(f"{r[0].ljust(w_name)}  {r[1]:<12}  {r[2]:<12}  {r[3]}")
    return 0


# ----- entrypoint ----------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-task",
                                 description="Manage per-PR task folders "
                                             "under ~/.agents-devkit/skill-pr-review/")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to ~/.agents-devkit/logs/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_prep = sub.add_parser("prepare",
                             help="create / refresh the task folder for one PR "
                                  "(runs Phase 0-4a prep; no review, no posting). "
                                  "Use --all to prep every non-merged queue row.")
    sp_prep.add_argument("pr_url", nargs="?", default=None,
                         help="PR URL to prepare (omit when using --all)")
    sp_prep.add_argument("--all", action="store_true",
                         help="prepare task folders for every non-merged queue row; "
                              "continues past per-row failures and exits 1 if any failed")
    sp_prep.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sp_prep.add_argument("--rebuild", action="store_true",
                         help="force a full index rebuild even if head_sha is unchanged")
    sp_prep.add_argument("--detailed", action="store_true",
                         help="use the detailed embed model (bge-m3) for higher recall")
    sp_prep.add_argument("--embed-model", default=None,
                         help="override embed model (default from config)")
    sp_prep.add_argument("--jobs", type=int, default=None,
                         help="parallel workers for --all (default: from "
                              "core.yaml pr_sync.prepare_jobs, fallback 1). "
                              "Effective parallelism is capped by the per-repo "
                              "clone lock and OLLAMA_NUM_PARALLEL.")
    sp_prep.add_argument("-y", "--yes", action="store_true")
    sp_prep.set_defaults(func=cmd_prepare)

    sp_info = sub.add_parser("info",
                             help="show task-folder state as JSON")
    sp_info.add_argument("pr_url")
    sp_info.add_argument("-y", "--yes", action="store_true")
    sp_info.set_defaults(func=cmd_info)

    sp_list = sub.add_parser("list", help="list every task folder")
    sp_list.add_argument("--names-only", action="store_true",
                         help="one folder name per line")
    sp_list.add_argument("--paths", action="store_true",
                         help="one absolute path per line")
    sp_list.add_argument("-y", "--yes", action="store_true")
    sp_list.set_defaults(func=cmd_list)

    sp_val = sub.add_parser("validate",
                            help="Phase 3 gate: anchor + suggestion check on "
                                 "the agent's findings.json. Produces "
                                 "validated-findings.json + initial-findings.json.")
    sp_val.add_argument("pr_url")
    sp_val.add_argument("-y", "--yes", action="store_true")
    sp_val.set_defaults(func=cmd_validate)

    sp_orph = sub.add_parser("clean-orphans",
                             help="drop task folders that no longer have a "
                                  "matching queue row (or whose row is merged)")
    sp_orph.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sp_orph.add_argument("--dry-run", action="store_true",
                         help="show what would be removed without deleting")
    sp_orph.add_argument("-y", "--yes", action="store_true",
                         help="confirm deletion (required unless --dry-run)")
    sp_orph.set_defaults(func=cmd_clean_orphans)

    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-task", enabled=True, argv=argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
