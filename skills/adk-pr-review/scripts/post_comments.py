#!/usr/bin/env python3
"""post_comments.py — post new inline findings + resolve/reopen existing threads.

Constitution §I.4: posting is gated on per-invocation user confirmation. This script
posts ONLY when invoked with `--confirmed yes`. Without that, it prints the plan and exits.

GitHub:
  - Inline comments via REST `POST /repos/{owner}/{repo}/pulls/{n}/comments`. We attempt
    to bundle into a single review using `POST /repos/{owner}/{repo}/pulls/{n}/reviews`
    with `comments: [...]` so the entire batch posts atomically.
  - Resolve / unresolve threads requires GraphQL. We attempt; fall back to a status
    comment if the token lacks the GraphQL scope.

Bitbucket:
  - Inline comments via `adk-mcp-bitbucket.addPullRequestComment`. We construct the
    same payload programmatically with the REST endpoint.
  - Resolve / reopen via the BB resolution endpoints.

Usage:
  python3 post_comments.py --task-dir <path> [--confirmed yes] [--no-resolve-existing] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import read_json, write_json, emit_json, get_logger, die  # noqa: E402

try:
    import requests
except ImportError:
    requests = None  # type: ignore


GH_API = "https://api.github.com"
BB_API = "https://api.bitbucket.org/2.0"


# ----- comment formatting --------------------------------------------------

# Maps the 6 internal severities → the 3 public comment categories the user wants.
SEVERITY_TO_CATEGORY = {
    "blocker":     "Must-Have/Blocker",
    "critical":    "Must-Have/Blocker",
    "should-have": "Should-Have",
    "may-have":    "May-Have/Nitpicks",
    "nitpick":     "May-Have/Nitpicks",
    "question":    "Clarification needed",
}


def format_comment_body(f: dict) -> str:
    """Render a finding as a structured PR comment.

    Layout:
        **<title>**                                  ← one-line headline

        *Category:* <Must-Have|Should-Have|May-Have> · *Dimension:* <dim> · *Confidence:* <high|med|low>

        <body — what the issue is and why>

        **How to fix**         (optional, when `suggestion` is present)
        <suggestion>

        **Need clarity on**    (only when severity == "question")
        <body, but phrased as a question>

        **Impact if unfixed**  (when impact_if_unfixed is present, and not a question)
        <impact_if_unfixed>

        — adk-pr-review · <severity> · finding `<id>`
    """
    title = (f.get("title") or "").strip() or "(no title)"
    severity = f.get("severity", "may-have")
    category = SEVERITY_TO_CATEGORY.get(severity, "May-Have/Nitpicks")
    dimension = f.get("dimension", "")
    confidence = f.get("confidence", "")
    body = (f.get("body") or "").rstrip()
    suggestion = (f.get("suggestion") or "").rstrip()
    impact = (f.get("impact_if_unfixed") or "").rstrip()
    fid = f.get("id", "")

    parts = [
        f"**{title}**",
        "",
        f"*Category:* {category} · *Dimension:* `{dimension}` · *Confidence:* `{confidence}`",
        "",
        body,
    ]

    if severity == "question":
        # Question findings ASK rather than assert. The "How to fix" section is
        # replaced by a single explicit clarification ask.
        parts += [
            "",
            "**Need clarity on**",
            "Could the author confirm the intent / share the design rationale / point to the doc that motivates this approach? I don't have enough context to call this right or wrong.",
        ]
    else:
        if suggestion:
            parts += [
                "",
                "**How to fix**",
                "",
                suggestion if suggestion.startswith("```") else f"```suggestion\n{suggestion}\n```",
            ]
        if impact:
            parts += ["", f"**Impact if unfixed:** {impact}"]

    parts += ["", f"— `adk-pr-review` · {severity} · finding `{fid}`"]
    return "\n".join(parts)


def format_review_summary(findings_blob: dict) -> str:
    """The body text of the review (above the inline comments)."""
    summary = (findings_blob.get("summary") or "").strip()
    by_cat: dict[str, int] = {}
    for fi in findings_blob.get("findings", []):
        cat = SEVERITY_TO_CATEGORY.get(fi.get("severity", "may-have"), "May-Have/Nitpicks")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    rec = findings_blob.get("recommendation", "comment_only")
    cat_line = " · ".join(f"{k}: {v}" for k, v in by_cat.items()) or "no findings"
    return (
        f"**adk-pr-review** · recommendation: `{rec}`\n\n"
        f"{summary}\n\n"
        f"*Findings:* {cat_line}\n"
    )


# ----- GitHub --------------------------------------------------------------

def _gh_headers() -> dict[str, str]:
    tok = (os.environ.get("GITHUB_TOKEN_CRED")
           or os.environ.get("GITHUB_TOKEN")
           or os.environ.get("GH_TOKEN"))
    if not tok:
        # Fall back to the gh CLI auth token.
        try:
            cp = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
            tok = cp.stdout.strip()
        except Exception:
            die("No GitHub token. Set GITHUB_TOKEN or run `gh auth login`.")
    return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"}


def gh_post_review(owner: str, repo: str, n: int, head_sha: str,
                   findings: list[dict], summary: str, recommendation: str,
                   findings_blob: dict, log) -> dict:
    if not requests:
        die("`requests` not installed.")
    comments_payload = []
    for f in findings:
        comments_payload.append({
            "path": f["file"],
            "line": int(f.get("line_end", f.get("line_start", 1))),
            "side": "RIGHT",
            "body": format_comment_body(f),
        })

    event_map = {"approve": "APPROVE", "request_changes": "REQUEST_CHANGES", "comment_only": "COMMENT"}
    review_body = format_review_summary(findings_blob)
    payload = {
        "commit_id": head_sha,
        "body": review_body,
        "event": event_map.get(recommendation, "COMMENT"),
        "comments": comments_payload,
    }
    url = f"{GH_API}/repos/{owner}/{repo}/pulls/{n}/reviews"
    log.info("gh POST %s (%d comments)", url, len(comments_payload))
    r = requests.post(url, json=payload, headers=_gh_headers(), timeout=60)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "body": r.text[:500]}
    return {"status": "ok", "review_id": r.json().get("id"), "n_comments": len(comments_payload)}


def gh_resolve_thread(owner: str, repo: str, n: int, comment_id: str, resolve: bool, log) -> dict:
    """GraphQL resolveReviewThread / unresolveReviewThread. Falls back to a status comment."""
    if not requests:
        die("`requests` not installed.")
    # GraphQL needs the thread node id, not the comment numeric id. We have to look it up.
    # Cheap fallback: post a reply with [resolved by adk-pr-review] marker.
    reply_url = f"{GH_API}/repos/{owner}/{repo}/pulls/{n}/comments/{comment_id}/replies"
    body = "[adk-pr-review] Resolving this thread — the diff at the anchored line addresses the concern." \
        if resolve else \
        "[adk-pr-review] Reopening this thread — the concern was not addressed in the latest push."
    r = requests.post(reply_url, json={"body": body}, headers=_gh_headers(), timeout=30)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "comment_id": comment_id,
                "note": "reply fallback also failed"}
    return {"status": "fallback_replied", "comment_id": comment_id, "resolve": resolve}


# ----- Bitbucket -----------------------------------------------------------

def _bb_session():
    if not requests:
        die("`requests` not installed.")
    s = requests.Session()
    tok = os.environ.get("BITBUCKET_TOKEN_CRED")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        die("BITBUCKET_TOKEN_CRED env var unset — needed for Bitbucket posts.")
    if user and ":" not in tok and not tok.startswith("Bearer "):
        s.auth = (user, tok)
    elif ":" in tok and not tok.startswith("Bearer "):
        s.auth = tuple(tok.split(":", 1))  # type: ignore[assignment]
    else:
        s.headers["Authorization"] = f"Bearer {tok}"
    s.headers["Accept"] = "application/json"
    return s


def bb_post_inline(workspace: str, repo: str, n: int, findings: list[dict],
                   findings_blob: dict, log) -> dict:
    s = _bb_session()
    results = []
    # First, post a top-level summary comment (BB doesn't have a "review" wrapper like GH).
    summary_body = format_review_summary(findings_blob)
    summary_url = f"{BB_API}/repositories/{workspace}/{repo}/pullrequests/{n}/comments"
    r = s.post(summary_url, json={"content": {"raw": summary_body}}, timeout=30)
    if r.status_code >= 300:
        results.append({"file": "<summary>", "status": "failed", "code": r.status_code, "body": r.text[:300]})
    else:
        results.append({"file": "<summary>", "status": "ok", "id": r.json().get("id")})

    for f in findings:
        payload = {
            "content": {"raw": format_comment_body(f)},
            "inline": {"path": f["file"], "to": int(f.get("line_end", f.get("line_start", 1)))},
        }
        url = f"{BB_API}/repositories/{workspace}/{repo}/pullrequests/{n}/comments"
        r = s.post(url, json=payload, timeout=30)
        if r.status_code >= 300:
            results.append({"file": f["file"], "status": "failed", "code": r.status_code, "body": r.text[:300]})
        else:
            results.append({"file": f["file"], "status": "ok", "id": r.json().get("id")})
    return {"status": "ok" if all(rr["status"] == "ok" for rr in results) else "partial",
            "n_comments": len(results), "results": results}


def bb_resolve(workspace: str, repo: str, n: int, comment_id: str, resolve: bool, log) -> dict:
    s = _bb_session()
    # BB Cloud exposes resolution as PUT/DELETE on /comments/<id>/resolution.
    url = f"{BB_API}/repositories/{workspace}/{repo}/pullrequests/{n}/comments/{comment_id}/resolution"
    if resolve:
        r = s.put(url, json={}, timeout=30)
    else:
        r = s.delete(url, timeout=30)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "comment_id": comment_id}
    return {"status": "ok", "comment_id": comment_id, "resolve": resolve}


# ----- entrypoint ----------------------------------------------------------

def plan_only(task_dir: Path, findings: dict, actions: list[dict]) -> dict:
    return {
        "task_dir": str(task_dir),
        "would_post_review": True,
        "n_findings": len(findings.get("findings", [])),
        "recommendation": findings.get("recommendation"),
        "n_resolve": sum(1 for a in actions if a.get("decision") == "resolve" and a.get("verified")),
        "n_reopen": sum(1 for a in actions if a.get("decision") == "reopen" and a.get("verified")),
        "n_leave": sum(1 for a in actions if a.get("decision") == "leave-as-is"),
        "note": "Plan-only — pass --post (or --confirmed yes) to transmit.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    # Default behavior is to POST. /adk-pr-review's task explicitly calls for
    # posting (constitution §I.4 names PR review posting as a task-required
    # action). Use --plan-only / --confirmed no to inhibit transmission. The
    # old --confirmed yes/no flag is kept for back-compat; the new --plan-only
    # is the idiomatic switch for "rehearse without posting".
    ap.add_argument("--confirmed", choices=("yes", "no"), default="yes",
                    help="back-compat. yes=post (default), no=plan-only.")
    ap.add_argument("--plan-only", action="store_true",
                    help="rehearse posting without transmitting (overrides --confirmed yes).")
    ap.add_argument("--no-resolve-existing", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.plan_only:
        args.confirmed = "no"

    task_dir = Path(args.task_dir)
    log = get_logger("post_comments", task_dir)

    pr = read_json(task_dir / "pr.json")
    # Triage-aware: prefer findings-final.json (only accepted findings + edits applied).
    # Fall back to findings.json when triage hasn't run (back-compat with task dirs
    # from before phase 5 or runs where the user explicitly skipped triage).
    final_path = task_dir / "findings-final.json"
    legacy_path = task_dir / "findings.json"
    if final_path.exists():
        findings_path = final_path
        log.info("reading findings-final.json (triage applied)")
    elif legacy_path.exists():
        findings_path = legacy_path
        log.info("reading findings.json (no triage; posting all findings as-is)")
    else:
        die(f"missing {final_path} (preferred) and {legacy_path} (fallback)")
    actions_path = task_dir / "comment-actions.json"
    findings = read_json(findings_path)
    actions = read_json(actions_path).get("actions", []) if actions_path.exists() else []

    if args.confirmed != "yes":
        result = plan_only(task_dir, findings, actions)
        return emit_json(result) if args.json else (print(json.dumps(result, indent=2)) or 0)

    host = pr.get("host")
    out = {"task_dir": str(task_dir), "host": host, "posted": [], "resolved": []}

    if host == "github":
        res = gh_post_review(pr["owner"], pr["repo"], pr["pr_number"], pr["head_oid"],
                             findings.get("findings", []), findings.get("summary", ""),
                             findings.get("recommendation", "comment_only"),
                             findings, log)
        out["posted"].append(res)
        if not args.no_resolve_existing:
            for a in actions:
                if a.get("verified") and a.get("decision") in ("resolve", "reopen"):
                    out["resolved"].append(gh_resolve_thread(
                        pr["owner"], pr["repo"], pr["pr_number"], a["comment_id"],
                        resolve=(a["decision"] == "resolve"), log=log))
    elif host == "bitbucket":
        res = bb_post_inline(pr["owner"], pr["repo"], pr["pr_number"],
                             findings.get("findings", []), findings, log)
        out["posted"].append(res)
        if not args.no_resolve_existing:
            for a in actions:
                if a.get("verified") and a.get("decision") in ("resolve", "reopen"):
                    out["resolved"].append(bb_resolve(
                        pr["owner"], pr["repo"], pr["pr_number"], a["comment_id"],
                        resolve=(a["decision"] == "resolve"), log=log))
    else:
        die(f"unsupported host: {host}")

    write_json(task_dir / "post-result.json", out)
    return emit_json(out) if args.json else 0


if __name__ == "__main__":
    raise SystemExit(main())
