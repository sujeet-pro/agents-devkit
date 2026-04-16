#!/usr/bin/env python3
"""Capture current git state for session handoff.

Gathers branch, status, recent commits, and diff summary, then outputs
a structured markdown section or JSON blob that can be embedded in a
handoff document.

Usage:
    python3 handoff.py [--output <path>] [--format md|json]

Options:
    --output <path>   Write output to a file instead of stdout.
    --format md|json  Output format (default: md).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git(*args: str) -> str:
    """Run a git command and return stripped stdout. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def get_branch() -> str:
    """Get the current branch name."""
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
    return branch or "(unknown)"


def get_status_lines() -> list[str]:
    """Get git status as a list of status lines."""
    raw = run_git("status", "--porcelain")
    if not raw:
        return []
    return [line for line in raw.splitlines() if line.strip()]


def parse_status(lines: list[str]) -> dict[str, list[str]]:
    """Parse porcelain status into categorized file lists."""
    staged: list[str] = []
    modified: list[str] = []
    untracked: list[str] = []

    for line in lines:
        if len(line) < 4:
            continue
        index_status = line[0]
        worktree_status = line[1]
        filepath = line[3:]

        if index_status == "?":
            untracked.append(filepath)
        elif index_status != " ":
            staged.append(filepath)
        if worktree_status not in (" ", "?"):
            modified.append(filepath)

    return {
        "staged": staged,
        "modified": modified,
        "untracked": untracked,
    }


def get_recent_commits(count: int = 10) -> list[dict[str, str]]:
    """Get recent commits as a list of {hash, message} dicts."""
    raw = run_git("log", f"-{count}", "--oneline", "--no-decorate")
    if not raw:
        return []
    commits = []
    for line in raw.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            commits.append({"hash": parts[0], "message": parts[1]})
        elif parts:
            commits.append({"hash": parts[0], "message": ""})
    return commits


def get_diff_summary() -> dict[str, int]:
    """Get a summary of changes: files changed, insertions, deletions."""
    raw = run_git("diff", "--stat")
    if not raw:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}

    lines = raw.strip().splitlines()
    if not lines:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}

    # The last line of git diff --stat looks like:
    #  3 files changed, 10 insertions(+), 2 deletions(-)
    summary_line = lines[-1]
    files_changed = 0
    insertions = 0
    deletions = 0

    import re

    m = re.search(r"(\d+) files? changed", summary_line)
    if m:
        files_changed = int(m.group(1))
    m = re.search(r"(\d+) insertions?", summary_line)
    if m:
        insertions = int(m.group(1))
    m = re.search(r"(\d+) deletions?", summary_line)
    if m:
        deletions = int(m.group(1))

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
    }


def get_staged_diff_summary() -> dict[str, int]:
    """Get a summary of staged changes."""
    raw = run_git("diff", "--cached", "--stat")
    if not raw:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}

    lines = raw.strip().splitlines()
    if not lines:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}

    summary_line = lines[-1]
    files_changed = 0
    insertions = 0
    deletions = 0

    import re

    m = re.search(r"(\d+) files? changed", summary_line)
    if m:
        files_changed = int(m.group(1))
    m = re.search(r"(\d+) insertions?", summary_line)
    if m:
        insertions = int(m.group(1))
    m = re.search(r"(\d+) deletions?", summary_line)
    if m:
        deletions = int(m.group(1))

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
    }


def gather_state() -> dict:
    """Gather all git state into a single dict."""
    status_lines = get_status_lines()
    status = parse_status(status_lines)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": get_branch(),
        "status": status,
        "has_uncommitted_changes": bool(status_lines),
        "diff_summary": get_diff_summary(),
        "staged_diff_summary": get_staged_diff_summary(),
        "recent_commits": get_recent_commits(),
    }


def format_md(state: dict) -> str:
    """Format git state as a markdown section."""
    lines: list[str] = []
    lines.append("## Git State")
    lines.append("")
    lines.append(f"*Captured at {state['timestamp']}*")
    lines.append("")
    lines.append(f"- **Branch:** `{state['branch']}`")

    has_changes = state["has_uncommitted_changes"]
    lines.append(f"- **Uncommitted changes:** {'yes' if has_changes else 'no'}")

    # Staged files
    staged = state["status"]["staged"]
    if staged:
        lines.append(f"- **Staged files:** {len(staged)}")
        for f in staged:
            lines.append(f"  - `{f}`")
    else:
        lines.append("- **Staged files:** none")

    # Modified (unstaged)
    modified = state["status"]["modified"]
    if modified:
        lines.append(f"- **Modified (unstaged):** {len(modified)}")
        for f in modified:
            lines.append(f"  - `{f}`")

    # Untracked
    untracked = state["status"]["untracked"]
    if untracked:
        lines.append(f"- **Untracked:** {len(untracked)}")
        for f in untracked:
            lines.append(f"  - `{f}`")

    # Diff summary
    diff = state["diff_summary"]
    if diff["files_changed"] > 0:
        lines.append(
            f"- **Unstaged diff:** {diff['files_changed']} file(s), "
            f"+{diff['insertions']} -{diff['deletions']}"
        )

    staged_diff = state["staged_diff_summary"]
    if staged_diff["files_changed"] > 0:
        lines.append(
            f"- **Staged diff:** {staged_diff['files_changed']} file(s), "
            f"+{staged_diff['insertions']} -{staged_diff['deletions']}"
        )

    # Recent commits
    commits = state["recent_commits"]
    if commits:
        lines.append("- **Recent commits:**")
        for c in commits:
            lines.append(f"  - `{c['hash']}` {c['message']}")

    lines.append("")
    return "\n".join(lines)


def format_json(state: dict) -> str:
    """Format git state as indented JSON."""
    return json.dumps(state, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture current git state for session handoff.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write output to a file instead of stdout.",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["md", "json"],
        default="md",
        dest="fmt",
        help="Output format (default: md).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = gather_state()

    if args.fmt == "json":
        output = format_json(state)
    else:
        output = format_md(state)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Git state written to {out_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
