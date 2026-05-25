#!/usr/bin/env python3
"""ensure_repo_clone.py — ensure the bare clone at
$ADK_DATA_HOME/repos/<repo>/original-clone/ exists and is at the latest
remote refs.

If absent: clone via `gh repo clone --bare` (GitHub) or
`git clone --bare <ssh-url>` (Bitbucket).
If present: `git fetch --all --prune`.

The clone is bare (`.git` only, no working tree). Worktrees are created
from it as needed — `branch-<slug>/code/` per tracked branch, and
`skill-pr-review/<repo>_pr-<n>/code/` per PR review.

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
    log.info("bare-cloning github:%s/%s → %s", owner, repo, dest)
    run(["gh", "repo", "clone", f"{owner}/{repo}", str(dest), "--", "--bare"],
        cwd=dest.parent)


def clone_bitbucket(workspace: str, repo: str, dest: Path, log) -> None:
    ssh = f"git@bitbucket.org:{workspace}/{repo}.git"
    log.info("bare-cloning bitbucket:%s/%s (%s) → %s", workspace, repo, ssh, dest)
    run(["git", "clone", "--bare", ssh, str(dest)], cwd=dest.parent)


def default_branch(bare_path: Path) -> str:
    # HEAD on a bare clone is a symref to the default branch (e.g. refs/heads/master).
    try:
        cp = run(["git", "symbolic-ref", "HEAD"], cwd=bare_path)
        ref = cp.stdout.strip()
        if ref.startswith("refs/heads/"):
            return ref.removeprefix("refs/heads/")
    except Exception:
        pass
    # Fallback heuristic.
    for cand in ("main", "master", "develop"):
        if run_ok(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{cand}"],
                  cwd=bare_path):
            return cand
    raise RuntimeError(f"could not determine default branch in {bare_path}")


def refresh_bare(bare_path: Path, log) -> str:
    """Fetch all remotes into the bare clone. Returns the default branch name."""
    log.info("fetching origin")
    run(["git", "fetch", "--all", "--prune"], cwd=bare_path)
    return default_branch(bare_path)


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
            # Bare clones have HEAD at the top level (no .git/ subdir).
            if not (dest / "HEAD").exists():
                die(f"{dest} exists but is not a bare git clone. Inspect and remove manually.")
            branch = refresh_bare(dest, log)
            status = "updated"
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if args.host == "github":
                clone_github(args.owner, args.repo, dest, log)
            else:
                clone_bitbucket(args.owner, args.repo, dest, log)
            branch = refresh_bare(dest, log)
            status = "cloned"

    result = {"status": status, "repo_path": str(dest), "branch": branch}
    if args.json:
        return emit_json(result)
    print(result, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
