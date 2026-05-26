#!/usr/bin/env python3
"""do_import.py — Import stage: fetch lightweight PR metadata and enrich the queue row.

Calls fetch_pr.py --metadata-only (no diff, no comments) and writes
title/author/head_sha/target_branch/is_draft/additions/deletions/changed_files
plus last_imported_at back to the queue row.

Idempotent: re-running on a PR that already has a title re-fetches (cheap) and
updates last_imported_at.

Usage:
  python3 do_import.py <pr-url> [--queue <path>] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import parse_pr_url, task_dir_for, get_logger, pr_review_file  # noqa: E402

# CLI helpers — queue_io lives in skills/adk-cli/scripts/.
ADK_CLI_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))
from queue_io import DEFAULT_QUEUE_PATH, update_pr_entry, _now_iso  # noqa: E402

# Decision-log helper — same pattern as prepare_task.py:81-88.
ADK_SCRIPTS = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(ADK_SCRIPTS))
try:
    from decision_logger import append_decision  # noqa: E402
except Exception:
    def append_decision(*_a, **_kw):  # type: ignore[misc]
        pass  # fail-open: never block a run on the log


_FETCH_PR = Path(__file__).resolve().parent / "fetch_pr.py"


def _emit(obj: dict) -> int:
    print(json.dumps(obj, ensure_ascii=False))
    return 0 if obj.get("status") == "ok" else 1


def do_import(pr_url: str, queue_path: Path, log) -> int:
    # Parse URL.
    try:
        parsed = parse_pr_url(pr_url)
    except ValueError as exc:
        return _emit({"stage": "import", "pr_url": pr_url, "status": "failed",
                      "error": str(exc)})

    host = parsed["host"]
    owner = parsed["owner"]
    repo = parsed["repo"]
    pr_number = parsed["pr_number"]
    task_slug = f"{repo}_pr-{pr_number}"

    # Resolve and create task_dir.
    task_dir = task_dir_for(repo, pr_number)
    task_dir.mkdir(parents=True, exist_ok=True)
    log.info("import: task_dir=%s", task_dir)

    # Call fetch_pr.py --metadata-only.
    cmd = [
        sys.executable, str(_FETCH_PR),
        "--host", host,
        "--owner", owner,
        "--repo", repo,
        "--pr-number", str(pr_number),
        "--task-dir", str(task_dir),
        "--metadata-only",
        "--json",
    ]
    log.info("import: running fetch_pr --metadata-only for %s", pr_url)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return _emit({"stage": "import", "pr_url": pr_url, "status": "failed",
                      "error": f"subprocess launch failed: {exc}"})

    if result.returncode != 0:
        stderr_tail = (result.stderr or "").strip()[-400:]
        return _emit({"stage": "import", "pr_url": pr_url, "status": "failed",
                      "error": f"fetch_pr exited {result.returncode}: {stderr_tail}"})

    # Parse the small pr.json written by fetch_pr --metadata-only.
    pr_json_path = pr_review_file(task_dir, "pr.json")
    try:
        pr_data = json.loads(pr_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _emit({"stage": "import", "pr_url": pr_url, "status": "failed",
                      "error": f"could not read pr.json: {exc}"})

    title = pr_data.get("title")
    author = pr_data.get("author")
    head_sha = pr_data.get("head_sha")
    target_branch = pr_data.get("target_branch") or pr_data.get("baseRefName")
    is_draft = pr_data.get("is_draft") or pr_data.get("isDraft") or False
    additions = pr_data.get("additions")
    deletions = pr_data.get("deletions")
    changed_files = pr_data.get("changed_files") or pr_data.get("changedFiles")

    # Write fields back to the queue row.
    updates: dict = {
        "last_imported_at": _now_iso(),
    }
    if title is not None:
        updates["title"] = title
    if author is not None:
        updates["author"] = author
    if head_sha is not None:
        updates["head_sha"] = head_sha
    if target_branch is not None:
        updates["target_branch"] = target_branch
    updates["is_draft"] = is_draft
    if additions is not None:
        updates["additions"] = additions
    if deletions is not None:
        updates["deletions"] = deletions
    if changed_files is not None:
        updates["changed_files"] = changed_files

    matched = update_pr_entry(queue_path, pr_url, updates)
    if not matched:
        log.warning("import: pr_url %s not found in queue — skipping queue update", pr_url)

    # Decision log.
    append_decision(
        skill="adk-pr-review",
        sub_flow="import",
        fork_id="import-source",
        fork_type="inferred",
        default_offered="origin-api",
        user_chose="origin-api",
        repo=repo,
        task_slug=task_slug,
        evidence="metadata-only fetch via origin API (no diff, no comments)",
    )

    log.info("import: ok title=%r head_sha=%s", title, head_sha)
    return _emit({
        "stage": "import",
        "pr_url": pr_url,
        "status": "ok",
        "title": title,
        "author": author,
        "head_sha": head_sha,
        "target_branch": target_branch,
        "is_draft": is_draft,
        "additions": additions,
        "deletions": deletions,
        "changed_files": changed_files,
        "queue_updated": matched,
    })


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Import stage: fetch lightweight PR metadata and enrich the queue row. "
            "No diff, no comments — designed to run in <2 s per PR."
        ),
    )
    ap.add_argument("pr_url", help="Full PR URL (github.com or bitbucket.org)")
    ap.add_argument(
        "--queue",
        default=None,
        metavar="PATH",
        help="Path to pr-queue.json5 (defaults to $ADK_CONFIG_HOME/pr-queue.json5)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Emit JSON to stdout (always on; kept for forward-compat)",
    )
    args = ap.parse_args()

    queue_path = Path(args.queue) if args.queue else DEFAULT_QUEUE_PATH
    log = get_logger("do_import", None)

    return do_import(args.pr_url, queue_path, log)


if __name__ == "__main__":
    raise SystemExit(main())
