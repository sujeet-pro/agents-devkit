"""Comment activity snapshots for PR re-review eligibility.

The queue stores only a hash and small counters. The normalized items here are
host-neutral and intentionally omit bot-authored review text so posting a fresh
adk review does not immediately enqueue a comment-only re-review. Human replies,
comment edits, deletes, and resolve/reopen state changes still move the hash.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import parse_pr_url  # type: ignore  # noqa: E402


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _body_hash(body: str) -> str:
    return _sha(body)[:16] if body else ""


def _is_bot_comment(body: str, author: str | None = None) -> bool:
    text = (body or "").lower()
    who = (author or "").lower()
    return (
        "adk-pr-review" in text
        or "adk-pr-review" in who
        or "_— adk-pr-review" in text
    )


def _latest(values: list[str | None]) -> str | None:
    present = sorted(v for v in values if v)
    return present[-1] if present else None


def normalize_comment_activity(host: str, comments_blob: dict) -> dict:
    """Return a deterministic, small comment-activity summary."""
    items: list[dict[str, Any]] = []
    raw_comments: list[dict] = []
    if host == "github":
        raw_comments.extend(comments_blob.get("review_comments") or [])
        raw_comments.extend(comments_blob.get("issue_comments") or [])
    elif host == "bitbucket":
        raw_comments.extend(comments_blob.get("comments") or [])

    for c in raw_comments:
        if host == "github":
            body = c.get("body") or ""
            author = ((c.get("user") or {}).get("login") or "")
            parent_id = c.get("in_reply_to_id")
            updated = c.get("updated_at") or c.get("created_at")
            inline = {
                "path": c.get("path"),
                "line": c.get("line") or c.get("original_line"),
            }
            resolved = bool(c.get("resolved", False))
            deleted = bool(c.get("deleted", False))
        else:
            body = ((c.get("content") or {}).get("raw") or "")
            author = ((c.get("user") or {}).get("display_name") or "")
            parent_id = (c.get("parent") or {}).get("id")
            updated = c.get("updated_on") or c.get("created_on")
            inline_obj = c.get("inline") or {}
            inline = {
                "path": inline_obj.get("path"),
                "line": inline_obj.get("to") or inline_obj.get("from"),
            }
            resolved = bool(c.get("resolved", False))
            deleted = bool(c.get("deleted", False))

        is_bot = _is_bot_comment(body, author)
        # Ignore bot root creation/edit noise. Keep resolution/deletion state
        # so human resolve/reopen actions on bot comments still trigger review.
        if is_bot and not parent_id and not resolved and not deleted:
            continue

        item: dict[str, Any] = {
            "id": str(c.get("id")),
            "parent_id": str(parent_id) if parent_id else None,
            "updated": updated,
            "deleted": deleted,
            "resolved": resolved,
            "inline": inline,
        }
        if not is_bot:
            item["body_hash"] = _body_hash(body)
            item["author"] = author
        items.append(item)

    items.sort(key=lambda x: (str(x.get("parent_id") or ""), str(x.get("id") or "")))
    digest = _sha(json.dumps(items, sort_keys=True, separators=(",", ":")))
    return {
        "hash": digest,
        "count": len(items),
        "unresolved_count": sum(1 for i in items if not i.get("resolved") and not i.get("deleted")),
        "updated_at": _latest([i.get("updated") for i in items]),
        "items": items,
    }


def queue_fields_from_activity(activity: dict) -> dict:
    return {
        "comment_activity_hash": activity.get("hash"),
        "comment_count": activity.get("count", 0),
        "unresolved_comment_count": activity.get("unresolved_count", 0),
        "comment_activity_updated_at": activity.get("updated_at"),
        "comment_activity_error": None,
    }


def fetch_comment_activity(pr_url: str, log=None) -> dict:
    """Fetch and normalize comment activity for a GitHub or Bitbucket Cloud PR."""
    host = "unknown"
    try:
        parsed = parse_pr_url(pr_url)
        host = parsed["host"]
        owner = parsed["owner"]
        repo = parsed["repo"]
        number = parsed["pr_number"]
        if host == "github":
            comments_blob = _fetch_github_comments(owner, repo, number)
        elif host == "bitbucket":
            comments_blob = _fetch_bitbucket_comments(owner, repo, number)
        else:
            return {"error": f"unsupported host: {host}"}
        activity = normalize_comment_activity(host, comments_blob)
        return {"host": host, **queue_fields_from_activity(activity)}
    except Exception as e:
        if log:
            log.warning("comment-activity fetch failed for %s: %s", pr_url, e)
        return {"error": str(e), "host": host}


def _fetch_github_comments(owner: str, repo: str, number: int) -> dict:
    review = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/pulls/{number}/comments", "--paginate"],
        capture_output=True, text=True, check=True,
    )
    issue = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/issues/{number}/comments", "--paginate"],
        capture_output=True, text=True, check=True,
    )
    return {
        "review_comments": json.loads(review.stdout or "[]"),
        "issue_comments": json.loads(issue.stdout or "[]"),
    }


def fetch_unresolved_comments(pr_url: str, log=None) -> dict:
    """Fetch open (unresolved) comments with full text for human review.

    Unlike `fetch_comment_activity`, this returns actual body text rather than
    hashes, so the reviewer can read and act on them directly.

    Platform notes:
      GitHub   — REST API exposes all non-deleted review + issue comments.
                 Thread resolution is only available via GraphQL or the web
                 UI; this is noted in `resolve_support` and `resolve_note`.
      Bitbucket — `resolved` flag is available in the REST response.

    Returns:
      {pr_url, host, count, items: [{id, parent_id, author, body, path, line,
        updated}], resolve_support, resolve_note}
    or {error, host, pr_url} on failure.
    """
    host = "unknown"
    try:
        parsed = parse_pr_url(pr_url)
        host = parsed["host"]
        owner = parsed["owner"]
        repo = parsed["repo"]
        number = parsed["pr_number"]
        if host == "github":
            blob = _fetch_github_comments(owner, repo, number)
            items = _extract_unresolved_github(blob)
            resolve_support = "github_graphql_only"
            resolve_note = (
                "GitHub REST API does not expose resolve/unresolve for individual "
                "review threads. Use the GitHub web UI or `gh pr view --web` to "
                "resolve comments."
            )
        elif host == "bitbucket":
            blob = _fetch_bitbucket_comments(owner, repo, number)
            items = _extract_unresolved_bitbucket(blob)
            resolve_support = "bitbucket_api"
            resolve_note = (
                "Bitbucket comments can be resolved via the REST API. "
                "Resolution via `adk pr resolve-comment` is not yet implemented; "
                "use the Bitbucket web UI for now."
            )
        else:
            return {"error": f"unsupported host: {host}", "host": host, "pr_url": pr_url}
        return {
            "pr_url": pr_url,
            "host": host,
            "count": len(items),
            "items": items,
            "resolve_support": resolve_support,
            "resolve_note": resolve_note,
        }
    except Exception as e:
        if log:
            log.warning("fetch_unresolved_comments failed for %s: %s", pr_url, e)
        return {"error": str(e), "host": host, "pr_url": pr_url}


def _extract_unresolved_github(blob: dict) -> list[dict]:
    """Return open review + issue comments with full text for display.

    GitHub REST does not expose a per-comment resolved flag; all non-deleted
    comments are treated as open. Bot root comments are still excluded.
    """
    items: list[dict] = []
    for c in (blob.get("review_comments") or []):
        if c.get("deleted"):
            continue
        body = c.get("body") or ""
        author = (c.get("user") or {}).get("login") or ""
        if _is_bot_comment(body, author):
            continue
        items.append({
            "id": str(c.get("id") or ""),
            "parent_id": str(c["in_reply_to_id"]) if c.get("in_reply_to_id") else None,
            "author": author,
            "body": body,
            "path": c.get("path"),
            "line": c.get("line") or c.get("original_line"),
            "updated": c.get("updated_at") or c.get("created_at"),
        })
    for c in (blob.get("issue_comments") or []):
        body = c.get("body") or ""
        author = (c.get("user") or {}).get("login") or ""
        if _is_bot_comment(body, author):
            continue
        items.append({
            "id": str(c.get("id") or ""),
            "parent_id": None,
            "author": author,
            "body": body,
            "path": None,
            "line": None,
            "updated": c.get("updated_at") or c.get("created_at"),
        })
    return items


def _extract_unresolved_bitbucket(blob: dict) -> list[dict]:
    """Return non-deleted, non-resolved Bitbucket comments with full text."""
    items: list[dict] = []
    for c in (blob.get("comments") or []):
        if c.get("deleted") or c.get("resolved"):
            continue
        body = (c.get("content") or {}).get("raw") or ""
        author = (c.get("user") or {}).get("display_name") or ""
        if _is_bot_comment(body, author):
            continue
        inline = c.get("inline") or {}
        items.append({
            "id": str(c.get("id") or ""),
            "parent_id": str((c.get("parent") or {}).get("id")) if (c.get("parent") or {}).get("id") else None,
            "author": author,
            "body": body,
            "path": inline.get("path"),
            "line": inline.get("to") or inline.get("from"),
            "updated": c.get("updated_on") or c.get("created_on"),
        })
    return items


def _fetch_bitbucket_comments(workspace: str, repo: str, number: int) -> dict:
    try:
        import requests
    except ImportError as e:
        raise RuntimeError("requests not installed") from e

    tok = os.environ.get("BITBUCKET_TOKEN_CRED") or os.environ.get("BITBUCKET_TOKEN")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        raise RuntimeError("BITBUCKET_TOKEN_CRED not set")
    session = requests.Session()
    session.headers["Accept"] = "application/json"
    if user:
        session.auth = (user, tok)
    else:
        session.headers["Authorization"] = f"Bearer {tok}"
    url = (
        "https://api.bitbucket.org/2.0/repositories/"
        f"{workspace}/{repo}/pullrequests/{number}/comments?pagelen=100"
    )
    comments: list[dict] = []
    while url:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        comments.extend(data.get("values", []))
        url = data.get("next")
    return {"comments": comments}
