#!/usr/bin/env python3
"""fetch_pr.py — fetch PR metadata + existing review comments + diff.patch.

GitHub path: `gh` CLI (must be on PATH). One call for the PR fields, one for review comments,
one for the diff.

Bitbucket path: BITBUCKET_TOKEN_CRED + BITBUCKET_USERNAME required. Uses the REST 2.0 API directly.

Usage:
  python3 fetch_pr.py --host github --owner acme --repo foo --pr-number 42 --task-dir <path> [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import which, write_json, emit_json, die, get_logger, run, pr_review_file, _narrate_write  # noqa: E402

try:
    import requests
except ImportError:
    print("adk-pr-review: `requests` not installed. pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(1)


# ----- GitHub via gh CLI ---------------------------------------------------

GH_FIELDS = (
    "number,title,body,state,isDraft,createdAt,updatedAt,mergeable,mergedAt,"
    "headRefName,headRefOid,baseRefName,baseRefOid,headRepository,"
    "author,reviewDecision,labels,additions,deletions,changedFiles,url,statusCheckRollup"
)


def _normalize_check_rollup(items: list[dict]) -> dict:
    failing_states = {"FAILURE", "FAILED", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}
    pending_states = {"PENDING", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
    failing: list[str] = []
    pending: list[str] = []
    passed = 0
    for item in items or []:
        name = item.get("name") or item.get("workflowName") or item.get("context") or "check"
        state = (item.get("conclusion") or item.get("status") or item.get("state") or "").upper()
        if state in failing_states:
            failing.append(name)
        elif state in pending_states:
            pending.append(name)
        elif state in {"SUCCESS", "SUCCESSFUL", "COMPLETED", "NEUTRAL", "SKIPPED"}:
            passed += 1
    overall = "failing" if failing else ("pending" if pending else ("passed" if passed else "unknown"))
    return {"state": overall, "failing": failing, "pending": pending, "passed": passed}


def fetch_github(owner: str, repo: str, n: int, task_dir: Path, log) -> dict:
    if not which("gh"):
        die("gh CLI not on PATH. brew install gh.")
    log.info("gh pr view --json (%s/%s#%d)", owner, repo, n)
    cp = run(["gh", "pr", "view", str(n), "--repo", f"{owner}/{repo}",
              "--json", GH_FIELDS])
    pr = json.loads(cp.stdout)
    pr["host"] = "github"
    pr["owner"] = owner
    pr["repo"] = repo
    pr["pr_number"] = n
    pr["head_sha"] = pr.get("headRefOid")
    pr["base_oid"] = pr.get("baseRefOid")
    pr["checks"] = _normalize_check_rollup(pr.get("statusCheckRollup") or [])
    write_json(pr_review_file(task_dir, "pr.json"), pr)

    log.info("gh api repos/%s/%s/pulls/%d/comments", owner, repo, n)
    cp = run(["gh", "api", f"repos/{owner}/{repo}/pulls/{n}/comments", "--paginate"])
    comments = json.loads(cp.stdout)
    # Also issue comments on the PR (not file-anchored), useful for "agreed offline" markers.
    cp2 = run(["gh", "api", f"repos/{owner}/{repo}/issues/{n}/comments", "--paginate"])
    issue_comments = json.loads(cp2.stdout)
    write_json(pr_review_file(task_dir, "pr-comments.json"), {
        "review_comments": comments,
        "issue_comments": issue_comments,
    })

    log.info("gh pr diff (writing diff.patch)")
    cp = run(["gh", "pr", "diff", str(n), "--repo", f"{owner}/{repo}", "--patch"])
    (pr_review_file(task_dir, "diff.patch")).write_text(cp.stdout, encoding="utf-8")

    return pr


# ----- Bitbucket via REST --------------------------------------------------

BB_BASE = "https://api.bitbucket.org/2.0"


def _bb_session() -> requests.Session:
    s = requests.Session()
    tok = os.environ.get("BITBUCKET_TOKEN_CRED")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        die(
            "BITBUCKET_TOKEN_CRED env var unset — needed for Bitbucket PRs. "
            "Per constitution §VII the script never echoes the value; export it before running."
        )
    if user and ":" not in tok and not tok.startswith("Bearer "):
        # Atlassian unified API token format: username + token via HTTP Basic.
        s.auth = (user, tok)
        s.headers["Accept"] = "application/json"
        return s
    # The token can be either an app password (basic auth as user:pass) or a workspace
    # access token (Bearer). We try Bearer first; the API returns 401 for Basic-style
    # tokens, and the user can prefix with "user:" to force Basic.
    if ":" in tok and not tok.startswith("Bearer "):
        s.auth = tuple(tok.split(":", 1))  # type: ignore[assignment]
    else:
        s.headers["Authorization"] = f"Bearer {tok}"
    s.headers["Accept"] = "application/json"
    return s


def _bb_paginate(session: requests.Session, url: str) -> list[dict]:
    out: list[dict] = []
    while url:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        out.extend(data.get("values", []))
        url = data.get("next")
    return out


def _bb_resolve_full_sha(s: requests.Session, workspace: str, repo: str,
                         short: str, log) -> str:
    """Resolve a Bitbucket Cloud abbreviated commit hash to its full 40-char
    SHA via `/repositories/{ws}/{repo}/commit/{short}`. Returns the input
    unchanged on failure — callers downstream can still try to fetch by
    branch ref. Bitbucket Cloud's pullrequests endpoint returns 12-char
    abbreviations, and `git fetch origin <short>` fails with
    "couldn't find remote ref" over the wire.
    """
    if not short or len(short) >= 40:
        return short
    try:
        r = s.get(f"{BB_BASE}/repositories/{workspace}/{repo}/commit/{short}",
                  timeout=20)
        r.raise_for_status()
        full = r.json().get("hash")
        if full and len(full) >= 40 and full.startswith(short):
            return full
        log.warning("bb: commit endpoint returned unexpected hash %r for short %s; "
                    "keeping abbreviated value", full, short)
    except Exception as e:
        log.warning("bb: failed to resolve abbreviated head_sha %s (%s); "
                    "git fetch may fail downstream", short, e)
    return short


def _fetch_bb_checks(s: requests.Session, workspace: str, repo: str,
                     head_sha: str | None, log, task_dir: Path | None = None) -> dict:
    if not head_sha:
        return {"state": "unknown", "failing": [], "pending": [], "passed": 0}
    try:
        statuses = _bb_paginate(
            s,
            f"{BB_BASE}/repositories/{workspace}/{repo}/commit/{head_sha}/statuses/build?pagelen=100",
        )
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            msg = ("build_status: not available "
                   "(403 — bitbucket token lacks repository:read scope or commit not visible)")
            log.warning("bb: %s", msg)
            _narrate_write(task_dir, f"[narrate] {msg}")
            return {"state": "unavailable", "failing": [], "pending": [], "passed": 0}
        log.warning("bb: failed to fetch build statuses for %s (%s)", head_sha, e)
        return {"state": "unknown", "failing": [], "pending": [], "passed": 0}
    except Exception as e:
        log.warning("bb: failed to fetch build statuses for %s (%s)", head_sha, e)
        return {"state": "unknown", "failing": [], "pending": [], "passed": 0}
    failing: list[str] = []
    pending: list[str] = []
    passed = 0
    for status in statuses:
        name = status.get("name") or status.get("key") or "build"
        state = (status.get("state") or "").upper()
        if state in {"FAILED", "STOPPED", "ERROR"}:
            failing.append(name)
        elif state in {"INPROGRESS", "PENDING"}:
            pending.append(name)
        elif state == "SUCCESSFUL":
            passed += 1
    overall = "failing" if failing else ("pending" if pending else ("passed" if passed else "unknown"))
    return {"state": overall, "failing": failing, "pending": pending, "passed": passed}


def fetch_bitbucket(workspace: str, repo: str, n: int, task_dir: Path, log) -> dict:
    s = _bb_session()
    log.info("bb GET /pullrequests/%d", n)
    r = s.get(f"{BB_BASE}/repositories/{workspace}/{repo}/pullrequests/{n}", timeout=30)
    r.raise_for_status()
    pr = r.json()

    head = pr.get("source", {}).get("commit", {}).get("hash")
    base = pr.get("destination", {}).get("commit", {}).get("hash")
    # Bitbucket Cloud abbreviates both source.commit.hash and destination.commit.hash
    # to 12 chars in the pullrequests endpoint. Resolve to full 40-char SHAs so
    # create_worktree.py can `git fetch origin <full-sha>` cleanly.
    head = _bb_resolve_full_sha(s, workspace, repo, head, log)
    base = _bb_resolve_full_sha(s, workspace, repo, base, log)
    out = {
        "host": "bitbucket",
        "owner": workspace,
        "repo": repo,
        "pr_number": n,
        "title": pr.get("title"),
        "body": (pr.get("rendered", {}).get("description", {}).get("raw")
                 or pr.get("description")),
        "state": pr.get("state"),
        "author": pr.get("author"),
        "headRefName": pr.get("source", {}).get("branch", {}).get("name"),
        "baseRefName": pr.get("destination", {}).get("branch", {}).get("name"),
        "head_sha": head,
        "base_oid": base,
        "mergeable": pr.get("mergeable"),
        "merge_status": pr.get("merge_status"),
        "checks": _fetch_bb_checks(s, workspace, repo, head, log, task_dir),
        "url": pr.get("links", {}).get("html", {}).get("href"),
        "raw": pr,
    }
    write_json(pr_review_file(task_dir, "pr.json"), out)

    log.info("bb GET comments (paginated)")
    comments = _bb_paginate(s, f"{BB_BASE}/repositories/{workspace}/{repo}/pullrequests/{n}/comments?pagelen=100")
    write_json(pr_review_file(task_dir, "pr-comments.json"), {"comments": comments})

    log.info("bb GET diff")
    r = s.get(
        f"{BB_BASE}/repositories/{workspace}/{repo}/pullrequests/{n}/diff",
        timeout=120,
    )
    r.raise_for_status()
    (pr_review_file(task_dir, "diff.patch")).write_text(r.text, encoding="utf-8")

    return out


# ----- entrypoint ----------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True, choices=("github", "bitbucket"))
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr-number", required=True, type=int)
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    task_dir.mkdir(parents=True, exist_ok=True)
    log = get_logger("fetch_pr", task_dir)

    if args.host == "github":
        pr = fetch_github(args.owner, args.repo, args.pr_number, task_dir, log)
    else:
        pr = fetch_bitbucket(args.owner, args.repo, args.pr_number, task_dir, log)

    diff_bytes = (pr_review_file(task_dir, "diff.patch")).stat().st_size
    result = {
        "task_dir": str(task_dir),
        "pr_json": str(pr_review_file(task_dir, "pr.json")),
        "pr_comments_json": str(pr_review_file(task_dir, "pr-comments.json")),
        "diff_patch": str(pr_review_file(task_dir, "diff.patch")),
        "diff_bytes": diff_bytes,
        "head_sha": pr.get("head_sha"),
        "base_oid": pr.get("base_oid"),
        "title": pr.get("title"),
        "url": pr.get("url"),
    }
    if args.json:
        return emit_json(result)
    print(result, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
