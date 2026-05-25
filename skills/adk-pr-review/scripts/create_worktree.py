#!/usr/bin/env python3
"""create_worktree.py — serialized worktree creation at a PR's head SHA.

Acquires $ADK_DATA_HOME/repos/.worktree-lock before `git worktree add`, releases after.

Usage:
  python3 create_worktree.py --repo foo --pr-number 42 --head-sha abc123 \
                             [--host github|bitbucket] [--json]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    REPOS_ROOT, clone_lock_for, file_lock, repo_clone_for, task_dir_for,
    run, run_ok, emit_json, die, get_logger
)


def _pr_head_refspec(host: str | None, pr_number: int) -> str | None:
    """Return the platform-specific refspec for a PR head ref, or None.

    These refs are maintained server-side but are NOT in the default
    `+refs/heads/*:refs/heads/*` fetch refspec, so a plain `git fetch --all`
    misses them. Required when the PR's source branch has been deleted on
    origin (typical after merge) or never existed as a regular branch
    (fork PRs on GitHub).
    """
    if not host:
        return None
    if host == "github":
        return f"+refs/pull/{pr_number}/head:refs/pr/{pr_number}/head"
    if host == "bitbucket":
        return f"+refs/pull-requests/{pr_number}/from:refs/pr/{pr_number}/from"
    return None


def fetch_sha(repo_path: Path, sha: str, log, *, host: str | None = None,
              pr_number: int | None = None) -> None:
    # Make sure the SHA is reachable. If not, fetch it.
    if run_ok(["git", "cat-file", "-e", sha], cwd=repo_path):
        return
    log.info("sha %s not present locally; fetching", sha)
    # `git fetch origin <sha>` requires server-side allowReachableSHA1InWant or
    # uploadpack.allowAnySHA1InWant; otherwise we have to fetch refs and re-check.
    if run_ok(["git", "fetch", "origin", sha], cwd=repo_path):
        return
    # Try the platform-specific PR head ref BEFORE a full all-prune. PR refs
    # work when the source branch has been deleted (merged PRs) or never lived
    # under refs/heads (fork PRs on GitHub) — both cases where --all misses it.
    refspec = _pr_head_refspec(host, pr_number) if pr_number is not None else None
    if refspec:
        log.info("fetching PR head ref: %s", refspec)
        if run_ok(["git", "fetch", "origin", refspec], cwd=repo_path):
            if run_ok(["git", "cat-file", "-e", sha], cwd=repo_path):
                return
    # Fallback: fetch all refs (slower).
    log.info("direct sha fetch failed; doing full fetch")
    run(["git", "fetch", "--all", "--prune"], cwd=repo_path)
    if run_ok(["git", "cat-file", "-e", sha], cwd=repo_path):
        return
    # Last resort: PR ref AFTER the full fetch, in case mirroring is slow.
    if refspec:
        log.info("retrying PR head ref after full fetch: %s", refspec)
        if run_ok(["git", "fetch", "origin", refspec], cwd=repo_path):
            if run_ok(["git", "cat-file", "-e", sha], cwd=repo_path):
                return
    # Diagnostic-rich failure message — abbreviated SHAs (typical when the
    # PR was pulled from Bitbucket Cloud's pullrequests endpoint without
    # the /commit resolution step) cannot be fetched directly; a deleted
    # source branch on Bitbucket Cloud is unrecoverable without admin
    # access (Cloud does not expose `refs/pull-requests/{n}/from` over git).
    hints: list[str] = []
    if len(sha) < 40:
        hints.append(
            f"head_sha looks abbreviated ({len(sha)} chars) — Bitbucket Cloud's "
            "pullrequests endpoint returns a 12-char hash. Re-run `adk pr-queue update "
            "--all` after upgrading: the queue should now resolve the full SHA via "
            "/commit/{short}."
        )
    if host == "bitbucket":
        hints.append(
            "Bitbucket Cloud does NOT expose `refs/pull-requests/{n}/from` to git "
            "clients — if the source branch was deleted upstream, the commit may "
            "be unrecoverable without admin access."
        )
    hint_block = ("\n  hint: " + "\n  hint: ".join(hints)) if hints else ""
    raise RuntimeError(
        f"sha {sha} not reachable from origin after full fetch (host={host or 'unknown'}, "
        f"pr={pr_number}){hint_block}"
    )


def worktree_exists_at(repo_path: Path, target: Path) -> bool:
    cp = run(["git", "worktree", "list", "--porcelain"], cwd=repo_path)
    return f"worktree {target}" in cp.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr-number", required=True, type=int)
    ap.add_argument("--head-sha", required=True)
    ap.add_argument("--host", choices=("github", "bitbucket"),
                    help="Enables PR-ref fetch fallback when the SHA isn't on a "
                         "regular branch (deleted source branch, fork PRs).")
    ap.add_argument("--rebuild", action="store_true", help="remove existing worktree before recreating")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log = get_logger("create_worktree")
    repo_path = repo_clone_for(args.repo)  # bare clone (HEAD lives at top level)
    if not (repo_path / "HEAD").exists():
        die(f"bare clone {repo_path} not present — run ensure_repo_clone.py first")

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
        fetch_sha(repo_path, args.head_sha, log,
                  host=args.host, pr_number=args.pr_number)

        if worktree_exists_at(repo_path, target) and args.rebuild:
            log.info("removing existing worktree at %s", target)
            run(["git", "worktree", "remove", "--force", str(target)], cwd=repo_path)

        # Stale-leftover guard: directory exists on disk but git has no record
        # of it (typical when a previous run crashed mid-`worktree add`, or the
        # admin ran `git worktree prune` without removing the dir). `git
        # worktree add` would refuse with rc=128 ("already exists"), so clear it
        # under the same lock before the add path runs.
        if target.exists() and not worktree_exists_at(repo_path, target):
            log.info("removing stale (unregistered) worktree dir at %s", target)
            shutil.rmtree(target)
            run(["git", "worktree", "prune"], cwd=repo_path)

        if not worktree_exists_at(repo_path, target):
            log.info("git worktree add --detach %s %s", target, args.head_sha)
            run(["git", "worktree", "add", "--detach", str(target), args.head_sha], cwd=repo_path)
        else:
            # Update the existing worktree to the new SHA.
            log.info("worktree exists; checking out %s", args.head_sha)
            run(["git", "checkout", "--detach", args.head_sha], cwd=target)

    head = run(["git", "rev-parse", "HEAD"], cwd=target).stdout.strip()
    if not head.startswith(args.head_sha):
        die(f"worktree HEAD {head} != requested {args.head_sha}")

    result = {
        "worktree_path": str(target),
        "head_sha": head,
        "repo_clone": str(repo_path),
    }
    if args.json:
        return emit_json(result)
    print(result, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
