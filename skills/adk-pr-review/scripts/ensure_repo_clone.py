#!/usr/bin/env python3
"""ensure_repo_clone.py — ensure ~/.agents-devkit/repos/<repo>/ exists and is at remote HEAD.

If absent: clone via `gh repo clone` (GitHub) or `git clone <ssh-url>` (Bitbucket).
If present: `git fetch --all --prune`, then check we're on the default branch at remote HEAD with no local changes.
Refuses to overwrite if the clone has unexpected local commits (not from this script's lineage).

Usage:
  python3 ensure_repo_clone.py --host github --owner acme --repo foo [--json]
  python3 ensure_repo_clone.py --host bitbucket --owner workspace --repo foo [--json]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    ensure_dirs, repo_clone_for, clone_lock_for, file_lock,
    run, run_ok, which, emit_json, die, get_logger
)


def clone_github(owner: str, repo: str, dest: Path, log) -> None:
    if not which("gh"):
        die("gh CLI not on PATH (needed for GitHub clones). Install: brew install gh")
    log.info("cloning github:%s/%s → %s", owner, repo, dest)
    run(["gh", "repo", "clone", f"{owner}/{repo}", str(dest)], cwd=dest.parent)


def clone_bitbucket(workspace: str, repo: str, dest: Path, log) -> None:
    ssh = f"git@bitbucket.org:{workspace}/{repo}.git"
    log.info("cloning bitbucket:%s/%s (%s) → %s", workspace, repo, ssh, dest)
    run(["git", "clone", ssh, str(dest)], cwd=dest.parent)


def default_branch(repo_path: Path) -> str:
    # Origin's default branch.
    try:
        cp = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo_path)
        ref = cp.stdout.strip()
        if ref.startswith("refs/remotes/origin/"):
            return ref.removeprefix("refs/remotes/origin/")
    except Exception:
        pass
    # Fallback heuristic.
    for cand in ("main", "master", "develop"):
        if run_ok(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{cand}"], cwd=repo_path):
            return cand
    raise RuntimeError(f"could not determine default branch in {repo_path}")


def reset_to_remote_default(repo_path: Path, log) -> str:
    # Refuse if there are uncommitted changes.
    cp = run(["git", "status", "--porcelain"], cwd=repo_path)
    if cp.stdout.strip():
        raise RuntimeError(
            f"adk-owned clone {repo_path} has uncommitted changes — inspect manually, do not let adk overwrite"
        )
    log.info("fetching origin")
    run(["git", "fetch", "--all", "--prune"], cwd=repo_path)
    branch = default_branch(repo_path)
    # Are we currently on a worktree? `git -C clone branch --show-current` returns empty in detached state.
    cp = run(["git", "branch", "--show-current"], cwd=repo_path, check=False)
    cur = cp.stdout.strip()
    if cur != branch:
        log.info("checking out default branch %s", branch)
        run(["git", "checkout", branch], cwd=repo_path)
    log.info("reset --hard origin/%s", branch)
    run(["git", "reset", "--hard", f"origin/{branch}"], cwd=repo_path)
    return branch


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, choices=("github", "bitbucket"))
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ensure_dirs()
    dest = repo_clone_for(args.repo)
    lock_path = clone_lock_for(args.repo)
    log = get_logger("ensure_repo_clone")

    # Per-repo clone-lock — serializes ONLY git operations against THIS repo's
    # adk-owned clone. Held briefly (clone or fetch+reset); released before the
    # caller proceeds to chunk/embed/AI/post. Different repos do not contend.
    with file_lock(lock_path, timeout_s=300.0):
        log.info("clone-lock acquired (%s)", lock_path)
        if dest.exists():
            if not (dest / ".git").exists():
                die(f"{dest} exists but is not a git repo. Inspect and remove manually.")
            branch = reset_to_remote_default(dest, log)
            status = "updated"
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if args.host == "github":
                clone_github(args.owner, args.repo, dest, log)
            else:
                clone_bitbucket(args.owner, args.repo, dest, log)
            branch = reset_to_remote_default(dest, log)
            status = "cloned"

    result = {"status": status, "repo_path": str(dest), "branch": branch}
    if args.json:
        return emit_json(result)
    print(result, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
