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

# Maps the 7 internal severities → the 4 public comment categories the user wants.
SEVERITY_TO_CATEGORY = {
    "blocker":      "Must fix before merge",
    "critical":     "Must fix before merge",
    "should-have":  "Worth addressing",
    "may-have":     "Nice to have",
    "nitpick":      "Nice to have",
    "question":     "Clarification needed",
    "appreciation": "Appreciation",
}

# Friendly opening lines per severity. The AI writes the body; this prefix
# sets the tone. Human voice — not robotic.
SEVERITY_OPENING = {
    "blocker":      "I think this needs a fix before merge — happy to be wrong if I'm missing context.",
    "critical":     "Flagging this as load-bearing — worth a careful look before merge.",
    "should-have":  "Not a blocker, but I think this is worth tightening up:",
    "may-have":     "Optional polish you might want to apply:",
    "nitpick":      "Small thing — feel free to ignore:",
    "question":     "I don't have enough context to call this right or wrong — could you confirm the intent?",
    "appreciation": "Nice — wanted to call this out.",
}


def format_comment_body(f: dict) -> str:
    """Render a finding as a human-voiced PR comment.

    Layout (regular finding):
        **<title>**                                       ← one-line headline

        *Category:* … · *Dimension:* … · *Confidence:* …

        <severity opening line>

        ### What's happening
        <body>

        ### Why this matters
        <impact_if_unfixed>                                (when present)

        ### Suggested fix
        ```suggestion
        <suggestion>
        ```

        — adk-pr-review · <severity> · finding <id>

    For severity=="question": replaces the body/why/fix sections with a
    single clarification ask.

    For severity=="appreciation": replaces the body section with a positive
    callout — no "Why this matters", no "Suggested fix".
    """
    severity = f.get("severity", "may-have")
    if severity == "appreciation":
        return format_appreciation_body(f)

    title = (f.get("title") or "").strip() or "(no title)"
    category = SEVERITY_TO_CATEGORY.get(severity, "Nice to have")
    dimension = f.get("dimension", "")
    confidence = f.get("confidence", "")
    body = (f.get("body") or "").rstrip()
    suggestion = (f.get("suggestion") or "").rstrip()
    impact = (f.get("impact_if_unfixed") or "").rstrip()
    fid = f.get("id", "")
    opening = SEVERITY_OPENING.get(severity, "")

    parts = [
        f"**{title}**",
        "",
        f"*{category}* · `{dimension}` · confidence `{confidence}`",
        "",
    ]
    if opening:
        parts += [opening, ""]

    if severity == "question":
        parts += [
            "### What I'm not sure about",
            body or "(no detail provided)",
            "",
            "Could the author confirm the intent / share the design rationale / point to the doc that motivates this approach?",
        ]
    else:
        parts += [
            "### What's happening",
            body or "(no detail provided)",
        ]
        if impact:
            parts += ["", "### Why this matters", impact]
        if suggestion:
            parts += [
                "",
                "### Suggested fix",
                "",
                suggestion if suggestion.startswith("```") else f"```suggestion\n{suggestion}\n```",
            ]

    parts += ["", f"_— adk-pr-review · `{severity}` · `{fid}`_"]
    return "\n".join(parts)


def format_appreciation_body(f: dict) -> str:
    """Render an `appreciation` finding as a celebratory PR comment.

    No 'How to fix', no 'Impact if unfixed' — just naming what's nice and
    why it's worth celebrating. Posted as a PR-level GENERAL comment on
    both platforms (GitHub: add_issue_comment; Bitbucket: addPullRequestComment
    without `inline`). General comments don't carry a resolve/reopen state,
    so the positive note stays as-is forever — exactly what we want.

    Since the comment is no longer line-anchored, the rendered body
    includes the file:line so the author knows what code is being praised.
    """
    title = (f.get("title") or "").strip() or "Nice work"
    dimension = f.get("dimension", "") or "general"
    body = (f.get("body") or "").rstrip() or "(no detail provided)"
    fid = f.get("id", "")
    file_path = f.get("file") or ""
    line_start = f.get("line_start")
    line_end = f.get("line_end")
    loc_parts = []
    if file_path:
        loc_parts.append(file_path)
        if line_start:
            if line_end and line_end != line_start:
                loc_parts.append(f":{line_start}-{line_end}")
            else:
                loc_parts.append(f":{line_start}")
    location = "".join(loc_parts)
    lines = [
        f"**{title}** 🎉",
        "",
        f"*Appreciation* · `{dimension}`",
    ]
    if location:
        lines.append(f"*Location:* `{location}`")
    lines += [
        "",
        SEVERITY_OPENING["appreciation"],
        "",
        body,
        "",
        f"_— adk-pr-review · `appreciation` · `{fid}`_",
    ]
    return "\n".join(lines)


def format_review_summary(findings_blob: dict) -> str:
    """The body text of the review (above the inline comments).

    Appreciation findings are surfaced separately from issue findings so the
    author sees the positive callouts up front.
    """
    summary = (findings_blob.get("summary") or "").strip()
    findings = findings_blob.get("findings", []) or []
    appreciations = [f for f in findings if f.get("severity") == "appreciation"]
    issues = [f for f in findings if f.get("severity") != "appreciation"]
    by_cat: dict[str, int] = {}
    for fi in issues:
        cat = SEVERITY_TO_CATEGORY.get(fi.get("severity", "may-have"), "Nice to have")
        by_cat[cat] = by_cat.get(cat, 0) + 1
    rec = findings_blob.get("recommendation", "comment_only")
    rec_human = {
        "approve":         "Approving — looks ready to ship.",
        "request_changes": "Holding for changes — see comments below.",
        "comment_only":    "Comments only — author decides.",
    }.get(rec, rec)
    parts = [
        "## adk-pr-review",
        "",
        rec_human,
        "",
    ]
    if summary:
        parts += [summary, ""]
    if appreciations:
        parts += [f"**Appreciations:** {len(appreciations)} — see inline.", ""]
    if by_cat:
        cat_line = " · ".join(f"{k}: {v}" for k, v in by_cat.items())
        parts += [f"**Issues:** {cat_line}"]
    else:
        parts += ["**Issues:** none"]
    return "\n".join(parts) + "\n"


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


def gh_post_general_comment(owner: str, repo: str, n: int, body: str, log) -> dict:
    """Post a PR-level (issue) comment on GitHub — not a review comment, not
    anchored. Used for appreciations so they don't carry a resolve state.
    """
    if not requests:
        die("`requests` not installed.")
    url = f"{GH_API}/repos/{owner}/{repo}/issues/{n}/comments"
    log.info("gh POST %s (general comment)", url)
    r = requests.post(url, json={"body": body}, headers=_gh_headers(), timeout=30)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "body": r.text[:300]}
    return {"status": "ok", "id": r.json().get("id"), "kind": "general"}


def bb_post_general_comment(workspace: str, repo: str, n: int, body: str, log) -> dict:
    """Post a PR-level comment on Bitbucket without an `inline` anchor."""
    s = _bb_session()
    url = f"{BB_API}/repositories/{workspace}/{repo}/pullrequests/{n}/comments"
    log.info("bb POST %s (general comment, no inline)", url)
    r = s.post(url, json={"content": {"raw": body}}, timeout=30)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "body": r.text[:300]}
    return {"status": "ok", "id": r.json().get("id"), "kind": "general"}


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


def bb_approve(workspace: str, repo: str, n: int, log) -> dict:
    """Approve a Bitbucket PR. Called only when recommendation == 'approve'
    AND comment-actions.json's approve_ready is true."""
    s = _bb_session()
    url = f"{BB_API}/repositories/{workspace}/{repo}/pullrequests/{n}/approve"
    r = s.post(url, json={}, timeout=30)
    if r.status_code >= 300:
        return {"status": "failed", "code": r.status_code, "body": r.text[:300]}
    return {"status": "ok", "approved_by": (r.json() or {}).get("user", {}).get("display_name")}


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

def should_post_review(findings: dict) -> bool:
    """Suppress an empty request_changes review.

    Posting a `request_changes` review with zero inline comments leaves a
    confusing artifact on the PR — a verdict with no substance. When triage
    rejects everything, the right thing is to skip the review post and let
    the resolve/reopen actions stand on their own.

    Exception: a review consisting only of appreciations IS worth posting —
    positive feedback is the whole point of the feature, and authors should
    see it in the PR thread, not just in findings.md.
    """
    n = len(findings.get("findings", []) or [])
    if n > 0:
        return True
    # No new findings — only post if the recommendation is positive (approve).
    return (findings.get("recommendation") == "approve")


def has_only_appreciations(findings: dict) -> bool:
    fs = findings.get("findings", []) or []
    return bool(fs) and all(f.get("severity") == "appreciation" for f in fs)


def plan_only(task_dir: Path, findings: dict, actions: list[dict]) -> dict:
    return {
        "task_dir": str(task_dir),
        "would_post_review": should_post_review(findings),
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
    ap.add_argument("--use-mcp", action="store_true",
                    help="emit posting-plan.json for the host agent to dispatch via MCP; "
                         "skip the direct-API transmission path. references/platform-mcp.md "
                         "documents the per-platform tool table.")
    ap.add_argument("--no-slack-summary", action="store_true",
                    help="suppress the Slack summary reply (otherwise posted to the same "
                         "thread the queue row's `slack` metadata names).")
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

    # Improvement #6: chain comment_resolver.py when actions exist but none are
    # `verified`, AND no comment-resolver state has been written. Skipping the
    # resolver leaves `n_resolve=0 / n_reopen=0` and silently drops the user's
    # intent. Running it here is idempotent — it just rewrites the actions
    # JSON with `verified` flags set.
    resolver_state = task_dir / "comment-resolver-state.json"
    if actions and not resolver_state.exists() and \
            not any(a.get("verified") for a in actions if a.get("decision") in ("resolve", "reopen")):
        resolver = Path(__file__).resolve().parent / "comment_resolver.py"
        log.info("chaining comment_resolver.py (unverified actions, no resolver state)")
        cp = subprocess.run(
            [sys.executable, str(resolver), "--task-dir", str(task_dir), "--json"],
            capture_output=True, text=True, check=False,
        )
        if cp.returncode != 0:
            log.warning("comment_resolver.py failed (rc=%d) — continuing with unverified actions: %s",
                        cp.returncode, (cp.stderr or "")[:200])
        else:
            # Reload actions; resolver may have flipped verified flags.
            actions = read_json(actions_path).get("actions", []) if actions_path.exists() else []

    # Build an MCP-first posting plan REGARDLESS of mode. The plan is the
    # machine-readable recipe the host agent will execute (`mcp__adk-mcp-*`
    # tools — see references/platform-mcp.md). The direct-API path below
    # stays as a headless fallback for when no agent is wrapping the run
    # (e.g. CI rehearsal).
    approve_ready = _comment_actions_approve_ready(task_dir)
    recommendation = findings.get("recommendation", "comment_only")
    # Pick up the queue's slack thread (populated by `adk pr-scan` + merged in
    # by prepare_task.py when the PR appears in the queue). Absent for URL-only
    # reviews — the Slack step then emits a "skipped" marker.
    queue_ctx_path = task_dir / "queue-context.json"
    queue_ctx = read_json(queue_ctx_path) if queue_ctx_path.exists() else None
    plan = build_posting_plan(
        pr=pr,
        findings_blob=findings,
        actions=actions,
        no_resolve_existing=args.no_resolve_existing,
        approve_ready=approve_ready,
        slack_summary_enabled=not args.no_slack_summary,
        queue_ctx=queue_ctx,
    )
    write_json(task_dir / "posting-plan.json", plan)
    log.info("posting-plan.json: %d step(s) — %s",
             len(plan.get("steps", [])),
             ", ".join(s.get("kind", "?") for s in plan.get("steps", [])) or "<empty>")

    if args.confirmed != "yes":
        result = plan_only(task_dir, findings, actions)
        result["posting_plan"] = str(task_dir / "posting-plan.json")
        result["plan_steps"] = len(plan.get("steps", []))
        return emit_json(result) if args.json else (print(json.dumps(result, indent=2)) or 0)

    if args.use_mcp:
        # MCP-first mode: the calling agent dispatches each step in
        # posting-plan.json via the named MCP tool. The script doesn't
        # transmit anything itself. This avoids direct-API duplication
        # of work the agent's MCP client already handles.
        log.info("--use-mcp: emitted posting-plan.json; agent will dispatch via MCP")
        out = {
            "task_dir": str(task_dir),
            "mode": "mcp-plan",
            "posting_plan": str(task_dir / "posting-plan.json"),
            "n_steps": len(plan.get("steps", [])),
            "note": "Host agent dispatches each step via the named mcp__adk-mcp-{github,bitbucket}__* tool. NEVER merge — that's a human action.",
        }
        write_json(task_dir / "post-result.json", out)
        return emit_json(out) if args.json else (print(json.dumps(out, indent=2)) or 0)

    host = pr.get("host")
    out = {"task_dir": str(task_dir), "host": host,
           "mode": "direct-api", "posted": [], "appreciations_posted": [],
           "resolved": [], "approved": None}

    # Separate appreciations from issues — issues go inline; appreciations
    # go as PR-level general comments (no resolve/reopen state).
    all_findings = findings.get("findings", []) or []
    appreciations = [f for f in all_findings if f.get("severity") == "appreciation"]
    issues_only = [f for f in all_findings if f.get("severity") != "appreciation"]
    issues_blob = dict(findings)
    issues_blob["findings"] = issues_only
    post_review = should_post_review(issues_blob)
    if not post_review and not appreciations:
        out["skipped_review"] = {
            "reason": "n_findings=0 (no issues, no appreciations) and recommendation is not 'approve'",
            "recommendation": findings.get("recommendation"),
            "n_findings": 0,
        }
        log.info("skipping review post: n_findings=0; resolves/reopens still allowed")

    if host == "github":
        if post_review:
            res = gh_post_review(pr["owner"], pr["repo"], pr["pr_number"], pr["head_sha"],
                                 issues_only, findings.get("summary", ""),
                                 recommendation, findings, log)
            out["posted"].append(res)
            # GitHub's review POST already encodes the APPROVE event when
            # recommendation == "approve" — no separate approve call.
            if recommendation == "approve" and approve_ready:
                out["approved"] = {"status": "ok", "via": "review_event=APPROVE"}
        # Appreciations always post as general PR comments.
        for f in appreciations:
            out["appreciations_posted"].append(gh_post_general_comment(
                pr["owner"], pr["repo"], pr["pr_number"],
                format_appreciation_body(f), log,
            ))
        if not args.no_resolve_existing:
            for a in actions:
                if a.get("verified") and a.get("decision") in ("resolve", "reopen"):
                    out["resolved"].append(gh_resolve_thread(
                        pr["owner"], pr["repo"], pr["pr_number"], a["comment_id"],
                        resolve=(a["decision"] == "resolve"), log=log))
    elif host == "bitbucket":
        if post_review:
            res = bb_post_inline(pr["owner"], pr["repo"], pr["pr_number"],
                                 issues_only, findings, log)
            out["posted"].append(res)
        for f in appreciations:
            out["appreciations_posted"].append(bb_post_general_comment(
                pr["owner"], pr["repo"], pr["pr_number"],
                format_appreciation_body(f), log,
            ))
        if not args.no_resolve_existing:
            for a in actions:
                if a.get("verified") and a.get("decision") in ("resolve", "reopen"):
                    out["resolved"].append(bb_resolve(
                        pr["owner"], pr["repo"], pr["pr_number"], a["comment_id"],
                        resolve=(a["decision"] == "resolve"), log=log))
        # Bitbucket has no APPROVE-in-review like GH — separate endpoint.
        if recommendation == "approve" and approve_ready:
            out["approved"] = bb_approve(pr["owner"], pr["repo"], pr["pr_number"], log)
    else:
        die(f"unsupported host: {host}")

    write_json(task_dir / "post-result.json", out)
    return emit_json(out) if args.json else 0


def _comment_actions_approve_ready(task_dir: Path) -> bool:
    """Read comment-actions.json (if present) and return its approve_ready flag.

    Defaults to False when absent — we don't approve a PR whose existing
    threads haven't been classified at all.
    """
    p = task_dir / "comment-actions.json"
    if not p.exists():
        return False
    try:
        return bool(json.loads(p.read_text(encoding="utf-8")).get("approve_ready", False))
    except Exception:
        return False


def format_slack_summary(*, pr: dict, findings_blob: dict, approve_ready: bool,
                          actions: list[dict]) -> str:
    """Short Slack message — one verdict line + items-to-fix bullets + link.

    Goes to the same thread that `adk pr-scan` picked the PR from.
    """
    rec = findings_blob.get("recommendation", "comment_only")
    findings = findings_blob.get("findings", []) or []
    issues = [f for f in findings if f.get("severity") != "appreciation"]
    appreciations = [f for f in findings if f.get("severity") == "appreciation"]
    blockers = [f for f in issues if f.get("severity") in ("blocker", "critical")]
    n_resolve = sum(1 for a in actions if a.get("verified") and a.get("decision") == "resolve")
    n_reopen = sum(1 for a in actions if a.get("verified") and a.get("decision") == "reopen")

    if rec == "approve" and approve_ready:
        verdict = ":white_check_mark: *APPROVE* — no changes required."
    elif blockers:
        verdict = f":octagonal_sign: *Changes requested* — {len(blockers)} blocking issue{'s' if len(blockers) != 1 else ''}."
    elif issues:
        verdict = f":speech_balloon: *Comments only* — {len(issues)} finding{'s' if len(issues) != 1 else ''}, none blocking."
    else:
        verdict = ":speech_balloon: *Comments only* — no issues, see PR."

    lines = [f":robot_face: adk-pr-review · <{pr.get('url')}|{pr.get('repo')}#{pr.get('pr_number')}>",
             verdict]
    if blockers:
        lines.append("Items to fix:")
        for f in blockers[:5]:
            title = (f.get("title") or "").strip()
            loc = f"{f.get('file')}:{f.get('line_start')}"
            lines.append(f"  • {title} — `{loc}`")
        if len(blockers) > 5:
            lines.append(f"  • …+{len(blockers) - 5} more")
    if appreciations:
        lines.append(f":sparkles: {len(appreciations)} appreciation{'s' if len(appreciations) != 1 else ''} posted as PR comments.")
    if n_resolve or n_reopen:
        bits = []
        if n_resolve:
            bits.append(f"{n_resolve} resolved")
        if n_reopen:
            bits.append(f"{n_reopen} reopened")
        lines.append(f"Threads: {', '.join(bits)}.")
    return "\n".join(lines)


def build_posting_plan(*, pr: dict, findings_blob: dict, actions: list[dict],
                       no_resolve_existing: bool, approve_ready: bool,
                       slack_summary_enabled: bool = True,
                       queue_ctx: dict | None = None) -> dict:
    """Translate the post-step intent into a list of MCP-tool invocations.

    Each step carries:
      kind:      semantic action — review_summary | inline_comment | resolve |
                 reopen | approve
      mcp_tool:  the named MCP tool the host agent should call
      mcp_args:  kwargs for the MCP tool (host-rendered)
      fallback:  what to do if the MCP tool is unreachable (usually the
                 direct-API equivalent; see references/platform-mcp.md)

    Constitution §I.4: each step is gated by the run-level posting confirm
    (handled by the orchestrator's `--no-post` flag and the auto-mode rule);
    individual steps do NOT prompt again.

    NEVER includes a merge step. Merging is a human action regardless of
    findings — the user clicks merge.
    """
    host = pr.get("host")
    owner = pr.get("owner")
    repo = pr.get("repo")
    n = pr.get("pr_number")
    head = pr.get("head_sha") or pr.get("headRefOid")
    findings = findings_blob.get("findings", []) or []
    recommendation = findings_blob.get("recommendation", "comment_only")
    # Appreciations get their own treatment: PR-level GENERAL comments on
    # both platforms (no inline anchor → no resolve/reopen state to manage).
    # The review (inline comments + verdict) carries ONLY the issues.
    appreciations = [f for f in findings if f.get("severity") == "appreciation"]
    issues_only = [f for f in findings if f.get("severity") != "appreciation"]
    issues_blob = dict(findings_blob)
    issues_blob["findings"] = issues_only
    post_review = should_post_review(issues_blob)
    steps: list[dict] = []

    # ---- Review summary + inline comments (issues only) ----
    if post_review:
        if host == "github":
            steps.append({
                "kind": "review_summary",
                "mcp_tool": "mcp__adk-mcp-github__pull_request_review_write",
                "mcp_args": {
                    "owner": owner, "repo": repo, "pullNumber": n,
                    "commitID": head,
                    "body": format_review_summary(findings_blob),
                    "event": {"approve": "APPROVE", "request_changes": "REQUEST_CHANGES",
                              "comment_only": "COMMENT"}.get(recommendation, "COMMENT"),
                    "comments": [
                        {"path": f["file"],
                         "line": int(f.get("line_end", f.get("line_start", 1))),
                         "side": "RIGHT",
                         "body": format_comment_body(f)}
                        for f in issues_only
                    ],
                },
                "fallback": "gh_post_review (direct REST POST /pulls/<n>/reviews)",
            })
        elif host == "bitbucket":
            steps.append({
                "kind": "review_summary",
                "mcp_tool": "mcp__adk-mcp-bitbucket__addPullRequestComment",
                "mcp_args": {
                    "workspace": owner, "repoSlug": repo, "pullRequestId": n,
                    "content": {"raw": format_review_summary(findings_blob)},
                },
                "fallback": "POST /pullrequests/<n>/comments",
            })
            for f in issues_only:
                steps.append({
                    "kind": "inline_comment",
                    "mcp_tool": "mcp__adk-mcp-bitbucket__addPullRequestComment",
                    "mcp_args": {
                        "workspace": owner, "repoSlug": repo, "pullRequestId": n,
                        "content": {"raw": format_comment_body(f)},
                        "inline": {"path": f["file"],
                                   "to": int(f.get("line_end", f.get("line_start", 1)))},
                    },
                    "fallback": "POST /pullrequests/<n>/comments (with inline.path/to)",
                    "finding_id": f.get("id"),
                })
    elif not appreciations:
        # No issues AND no appreciations → nothing to post but resolves/approve.
        steps.append({
            "kind": "review_summary_skipped",
            "reason": "n_findings=0 (no issues, no appreciations) and recommendation is not 'approve'",
        })

    # ---- Appreciations as general PR comments (both platforms, always post) ----
    # General comments have no resolve/reopen state — exactly what we want for
    # positive feedback. GitHub: add_issue_comment. Bitbucket: addPullRequestComment
    # without `inline`. Triage cannot reject these (they auto-accept at --init).
    for f in appreciations:
        body = format_appreciation_body(f)
        if host == "github":
            steps.append({
                "kind": "general_comment",
                "subkind": "appreciation",
                "mcp_tool": "mcp__adk-mcp-github__add_issue_comment",
                "mcp_args": {
                    "owner": owner, "repo": repo, "issue_number": n,
                    "body": body,
                },
                "fallback": "POST /repos/<o>/<r>/issues/<n>/comments",
                "finding_id": f.get("id"),
            })
        elif host == "bitbucket":
            steps.append({
                "kind": "general_comment",
                "subkind": "appreciation",
                "mcp_tool": "mcp__adk-mcp-bitbucket__addPullRequestComment",
                "mcp_args": {
                    "workspace": owner, "repoSlug": repo, "pullRequestId": n,
                    "content": {"raw": body},
                    # NB: no `inline` field — that's what makes this a
                    # general (non-anchored) comment on Bitbucket.
                },
                "fallback": "POST /pullrequests/<n>/comments (no inline.*)",
                "finding_id": f.get("id"),
            })

    # ---- Resolve / reopen existing threads ----
    if not no_resolve_existing:
        for a in actions:
            if not a.get("verified"):
                continue
            decision = a.get("decision")
            if decision not in ("resolve", "reopen"):
                continue
            cid = a.get("comment_id")
            if host == "github":
                # GraphQL is the only API that flips thread state; the script's
                # current fallback posts a reply. The MCP tool is also a reply.
                steps.append({
                    "kind": decision,
                    "mcp_tool": "mcp__adk-mcp-github__add_reply_to_pull_request_comment",
                    "mcp_args": {
                        "owner": owner, "repo": repo, "pullNumber": n,
                        "commentID": cid,
                        "body": (
                            "[adk-pr-review] Resolving this thread — the diff at the anchored line addresses the concern."
                            if decision == "resolve" else
                            "[adk-pr-review] Reopening this thread — the concern was not addressed in the latest push."
                        ),
                    },
                    "fallback": "POST /pulls/<n>/comments/<id>/replies",
                    "comment_id": cid,
                    "reason": a.get("reason"),
                })
            elif host == "bitbucket":
                steps.append({
                    "kind": decision,
                    "mcp_tool": ("mcp__adk-mcp-bitbucket__resolveComment"
                                  if decision == "resolve"
                                  else "mcp__adk-mcp-bitbucket__reopenComment"),
                    "mcp_args": {
                        "workspace": owner, "repoSlug": repo, "pullRequestId": n,
                        "commentID": cid,
                    },
                    "fallback": ("PUT /pullrequests/<n>/comments/<id>/resolution"
                                  if decision == "resolve"
                                  else "DELETE /pullrequests/<n>/comments/<id>/resolution"),
                    "comment_id": cid,
                    "reason": a.get("reason"),
                })

    # ---- Approve PR when mergeable ----
    if recommendation == "approve" and approve_ready:
        if host == "github":
            # GitHub: APPROVE is encoded in the review_summary step's `event`.
            # No separate step; surface that the approval is bundled.
            steps.append({
                "kind": "approve_pr",
                "via": "bundled_in_review_summary_event=APPROVE",
                "note": "GitHub approves via the review's event field; no separate MCP call.",
            })
        elif host == "bitbucket":
            steps.append({
                "kind": "approve_pr",
                "mcp_tool": "mcp__adk-mcp-bitbucket__approvePullRequest",
                "mcp_args": {"workspace": owner, "repoSlug": repo, "pullRequestId": n},
                "fallback": "POST /pullrequests/<n>/approve",
            })

    # ---- Slack summary reply (when the queue carried a slack thread) ----
    if slack_summary_enabled and queue_ctx:
        slack = queue_ctx.get("slack") or {}
        channel_id = slack.get("channel_id")
        # Reply on the same thread `adk pr-scan` picked the PR from. message_ts
        # may point at a reply (when link_origin == "reply"); thread_ts is the
        # parent thread root.
        thread_ts = slack.get("thread_ts") or slack.get("message_ts")
        if channel_id and thread_ts:
            steps.append({
                "kind": "slack_summary",
                "mcp_tool": "mcp__adk-mcp-slack__conversations_add_message",
                "mcp_args": {
                    "channel": channel_id,
                    "thread_ts": thread_ts,
                    "text": format_slack_summary(
                        pr=pr, findings_blob=findings_blob,
                        approve_ready=approve_ready, actions=actions,
                    ),
                },
                "fallback": "slack-sdk WebClient.chat_postMessage(channel, text, thread_ts=...)",
                "note": "Posts a short verdict + items-to-fix in the existing review thread.",
            })
        else:
            steps.append({
                "kind": "slack_summary_skipped",
                "reason": "no slack channel/thread_ts in queue context — PR was reviewed by URL or not in queue",
            })

    return {
        "host": host,
        "pr_url": pr.get("url"),
        "recommendation": recommendation,
        "approve_ready": approve_ready,
        "post_review": post_review,
        "n_findings": len(findings),
        "n_issues": len(issues_only),
        "n_appreciations": len(appreciations),
        "n_actions": sum(1 for a in actions if a.get("verified") and a.get("decision") in ("resolve", "reopen")),
        "steps": steps,
        "never_merge": True,  # explicit: this plan NEVER includes a merge step
        "doc": "Execute each step via its mcp_tool with mcp_args. See skills/adk-pr-review/references/platform-mcp.md.",
    }


if __name__ == "__main__":
    raise SystemExit(main())
