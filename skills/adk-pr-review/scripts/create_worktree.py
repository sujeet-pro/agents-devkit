#!/usr/bin/env python3
"""create_worktree.py — serialized worktree creation at a PR's head OID.

Acquires ~/.agents-devkit/repos/.worktree-lock before `git worktree add`, releases after.

Usage:
  python3 create_worktree.py --repo foo --pr-number 42 --head-oid abc123 [--json]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    REPOS_ROOT, clone_lock_for, file_lock, repo_clone_for, task_dir_for,
    run, run_ok, emit_json, die, get_logger
)


def fetch_oid(repo_path: Path, oid: str, log) -> None:
    # Make sure the OID is reachable. If not, fetch it.
    if run_ok(["git", "cat-file", "-e", oid], cwd=repo_path):
        return
    log.info("oid %s not present locally; fetching", oid)
    # `git fetch origin <sha>` requires server-side allowReachableSHA1InWant or
    # uploadpack.allowAnySHA1InWant; otherwise we have to fetch refs and re-check.
    if run_ok(["git", "fetch", "origin", oid], cwd=repo_path):
        return
    # Fallback: fetch all refs (slower).
    log.info("direct sha fetch failed; doing full fetch")
    run(["git", "fetch", "--all", "--prune"], cwd=repo_path)
    if not run_ok(["git", "cat-file", "-e", oid], cwd=repo_path):
        raise RuntimeError(f"oid {oid} not reachable from origin after full fetch")


def worktree_exists_at(repo_path: Path, target: Path) -> bool:
    cp = run(["git", "worktree", "list", "--porcelain"], cwd=repo_path)
    return f"worktree {target}" in cp.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr-number", required=True, type=int)
    ap.add_argument("--head-oid", required=True)
    ap.add_argument("--rebuild", action="store_true", help="remove existing worktree before recreating")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log = get_logger("create_worktree")
    repo_path = repo_clone_for(args.repo)
    if not (repo_path / ".git").exists():
        die(f"clone {repo_path} not present — run ensure_repo_clone.py first")

    task_dir = task_dir_for(args.repo, args.pr_number)
    target = task_dir / "code"
    task_dir.mkdir(parents=True, exist_ok=True)

    REPOS_ROOT.mkdir(parents=True, exist_ok=True)
    # Per-repo clone-lock — only serializes git operations against THIS repo.
    # Parallel reviews of different PRs of the SAME repo briefly contend here
    # (fetch + `git worktree add`); parallel reviews of DIFFERENT repos do not.
    # The `git checkout --detach` on the worktree itself is against the
    # worktree's own .git dir, so it stays inside this critical section only
    # for symmetry / log clarity.
    lock_path = clone_lock_for(args.repo)
    with file_lock(lock_path, timeout_s=300.0):
        log.info("clone-lock acquired (%s)", lock_path)
        fetch_oid(repo_path, args.head_oid, log)

        if worktree_exists_at(repo_path, target) and args.rebuild:
            log.info("removing existing worktree at %s", target)
            run(["git", "worktree", "remove", "--force", str(target)], cwd=repo_path)

        if not worktree_exists_at(repo_path, target):
            log.info("git worktree add --detach %s %s", target, args.head_oid)
            run(["git", "worktree", "add", "--detach", str(target), args.head_oid], cwd=repo_path)
        else:
            # Update the existing worktree to the new OID.
            log.info("worktree exists; checking out %s", args.head_oid)
            run(["git", "checkout", "--detach", args.head_oid], cwd=target)

    head = run(["git", "rev-parse", "HEAD"], cwd=target).stdout.strip()
    if not head.startswith(args.head_oid):
        die(f"worktree HEAD {head} != requested {args.head_oid}")

    result = {
        "worktree_path": str(target),
        "head_oid": head,
        "repo_clone": str(repo_path),
    }
    if args.json:
        return emit_json(result)
    print(result, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
