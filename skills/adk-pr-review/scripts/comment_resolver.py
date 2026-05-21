#!/usr/bin/env python3
"""comment_resolver.py — verify each `existing_comment_actions[]` entry from the model.

Inputs:
  - <task-dir>/pr-comments.json (existing comments fetched in Phase 2)
  - <task-dir>/diff.patch
  - <task-dir>/findings.json (proposed by the model, includes existing_comment_actions[])

Process:
  - For each model-proposed action, run the verifier:
    - resolve: ensure the anchored lines were touched by the diff OR the surrounding code now addresses the concern (heuristic — needs evidence_ref).
    - reopen: ensure the thread is currently RESOLVED on host AND the diff did not address it AND no offline-alignment marker in replies.
    - leave-as-is: always allowed.
  - Re-run the offline-alignment heuristic on every thread independently; if the model claimed offline_alignment_detected without an obvious marker, drop confidence.

Outputs:
  - <task-dir>/comment-actions.json (verified, with statuses)

See references/comment-resolution.md for the rules this implements.

Usage:
  python3 comment_resolver.py --task-dir <path> [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import read_json, write_json, emit_json, get_logger, die, pr_review_file  # noqa: E402


OFFLINE_PATTERNS = [
    re.compile(r"\b(agreed|aligned|sync'?d|synced|discussed)\s+(offline|in\s+(the\s+)?meeting|in\s+(the\s+)?call|on\s+slack|on\s+discord)\b", re.I),
    re.compile(r"\b(offline|out\s+of\s+band)\s+(agreement|alignment|conversation)\b", re.I),
    re.compile(r"\b(we'?ll|will)\s+(handle|address|fix)\s+(this|it)\s+(in|via|with)\s+(a\s+)?(follow-?up|follow\s+up|separate)\s+pr\b", re.I),
    re.compile(r"\bout\s+of\s+scope\b", re.I),
    re.compile(r"\bskip(ping)?\s+for\s+now\b", re.I),
    re.compile(r"\bdeferred\b", re.I),
    re.compile(r"\b(thanks|sounds\s+good)[,!]?\s+(closing|resolving)\b", re.I),
]

# A Jira-style reply IS an acceptable disposition — "tracked in PROJ-1234",
# "moved to JIRA-5678", "filed as INFRA-42 for next sprint". The ticket
# becomes the new owner of the concern, so the comment thread is no longer
# the right place to re-litigate it.
JIRA_REPLY_PATTERNS = [
    # Phrases that signal "we tracked this elsewhere": tracked / filed /
    # logged / opened / created — followed by a Jira-style key within ~40
    # chars. The first capture in each pattern is the key.
    re.compile(r"\b(?:tracked|filed|logged|opened|created|moved|migrated)\b[^.\n]{0,40}\b([A-Z][A-Z0-9]{1,9}-\d+)\b", re.I),
    re.compile(r"\b(?:see|ref(?:erence)?|follow(?:-?up)?(?:\s+in)?|will\s+(?:do|handle|address|fix)\s+(?:in|via))\b[^.\n]{0,30}\b([A-Z][A-Z0-9]{1,9}-\d+)\b", re.I),
    # Bare key adjacent to a "follow-up" keyword — looser fallback.
    re.compile(r"\bfollow[- ]?up\b[^.\n]{0,20}\b([A-Z][A-Z0-9]{1,9}-\d+)\b", re.I),
]

# "Synced with @person" / "spoke to @person" — explicit human alignment.
# @ is required: "synced with the team" is too generic; we want a specific
# accountable handle so the report can name who took the decision.
SYNCED_WITH_PATTERNS = [
    re.compile(r"\b(?:synced|sync'?d|spoke|spoken|talked|aligned|discussed)\s+(?:with|to)\s+@([A-Za-z][\w.-]{1,40})\b", re.I),
    re.compile(r"\b(?:per|as\s+per|per\s+chat\s+with)\s+@([A-Za-z][\w.-]{1,40})\b", re.I),
]

NEGATIVE_PATTERNS = [
    re.compile(r"\b(but|however|except|unless)\b", re.I),
]


def _passes_negatives(body: str) -> bool:
    """The body must not contain negation/qualifier and must not end with ?."""
    if any(p.search(body) for p in NEGATIVE_PATTERNS):
        return False
    if body.strip().endswith("?"):
        return False
    return True


def has_offline_marker(body: str) -> bool:
    body = body or ""
    if not any(p.search(body) for p in OFFLINE_PATTERNS):
        return False
    return _passes_negatives(body)


def extract_jira_reply_ref(body: str) -> str | None:
    """Return the Jira key if the reply tracks this in another ticket."""
    body = body or ""
    if not _passes_negatives(body):
        return None
    for p in JIRA_REPLY_PATTERNS:
        m = p.search(body)
        if m:
            return m.group(1)
    return None


def extract_synced_with(body: str) -> str | None:
    """Return the @person handle if the reply names a sync partner."""
    body = body or ""
    if not _passes_negatives(body):
        return None
    for p in SYNCED_WITH_PATTERNS:
        m = p.search(body)
        if m:
            return m.group(1)
    return None


def classify_reply(body: str) -> tuple[str | None, str | None]:
    """Return (kind, detail) for an acceptable-reply reading.

    kind ∈ {"offline", "jira", "synced", None}.
    detail is the ticket key / @handle / the matching phrase, used downstream
    when surfacing why a thread was left alone.
    """
    if has_offline_marker(body):
        return ("offline", body.strip().split("\n", 1)[0][:120])
    jira = extract_jira_reply_ref(body)
    if jira:
        return ("jira", jira)
    handle = extract_synced_with(body)
    if handle:
        return ("synced", handle)
    return (None, None)


def host_of(pr: dict) -> str:
    return pr.get("host", "unknown")


def _gh_thread_state(c: dict) -> dict:
    # GitHub review-comments are individual; threads are grouped by `in_reply_to_id`.
    return {
        "id": str(c.get("id")),
        "path": c.get("path"),
        "line": c.get("line") or c.get("original_line"),
        "body": c.get("body") or "",
        "user": (c.get("user") or {}).get("login"),
        "resolved": False,  # REST doesn't expose; GraphQL does. Assume open.
        "in_reply_to_id": str(c.get("in_reply_to_id")) if c.get("in_reply_to_id") else None,
    }


def _bb_thread_state(c: dict) -> dict:
    inline = c.get("inline") or {}
    return {
        "id": str(c.get("id")),
        "path": inline.get("path"),
        "line": inline.get("to") or inline.get("from"),
        "body": (c.get("content") or {}).get("raw") or "",
        "user": (c.get("user") or {}).get("display_name"),
        "resolved": bool(c.get("resolved", False)),  # BB exposes a 'resolution' object when resolved
        "parent_id": str((c.get("parent") or {}).get("id")) if c.get("parent") else None,
    }


def normalize_threads(pr: dict, comments_blob: dict) -> dict[str, dict]:
    """Group host comments by thread root id; collect all replies."""
    host = host_of(pr)
    threads: dict[str, dict] = {}
    if host == "github":
        review = comments_blob.get("review_comments", [])
        for c in review:
            t = _gh_thread_state(c)
            root = t["in_reply_to_id"] or t["id"]
            threads.setdefault(root, {"root_id": root, "thread": [], "resolved": False})["thread"].append(t)
    elif host == "bitbucket":
        all_comments = comments_blob.get("comments", [])
        for c in all_comments:
            t = _bb_thread_state(c)
            root = t["parent_id"] or t["id"]
            threads.setdefault(root, {"root_id": root, "thread": [], "resolved": False})["thread"].append(t)
            if t["resolved"]:
                threads[root]["resolved"] = True
    return threads


def lines_touched_by_diff(diff_text: str) -> dict[str, list[tuple[int, int]]]:
    """Map file → list of (added_line_start, added_line_end) ranges."""
    out: dict[str, list[tuple[int, int]]] = {}
    cur = None
    a_start = 0
    a_count = 0
    in_hunk = False
    last_added_start = 0
    last_added_end = 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            cur = line[4:].strip()
            if cur.startswith("b/"):
                cur = cur[2:]
            continue
        if line.startswith("@@") and cur:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                a_start = int(m.group(1))
                a_count = int(m.group(2) or "1")
                if a_count > 0:
                    out.setdefault(cur, []).append((a_start, a_start + a_count - 1))
            in_hunk = True
    return out


def verify_action(action: dict, threads: dict, touched: dict, log) -> dict:
    cid = str(action.get("comment_id"))
    decision = action.get("decision", "leave-as-is")
    reason = action.get("reason", "")
    claimed_offline = bool(action.get("offline_alignment_detected", False))

    # Find the thread containing this comment id (could be root or reply).
    thread_root = None
    thread_state = None
    for root_id, t in threads.items():
        if any(c["id"] == cid for c in t["thread"]):
            thread_root = root_id
            thread_state = t
            break

    result = {
        "comment_id": cid,
        "decision": decision,
        "reason": reason,
        "offline_alignment_detected": claimed_offline,
        "verified": False,
        "verifier_note": "",
    }
    if thread_state is None:
        result["verifier_note"] = "thread not found in pr-comments.json — leave-as-is"
        result["decision"] = "leave-as-is"
        return result

    result["thread_root"] = thread_root
    result["thread_currently_resolved"] = thread_state.get("resolved", False)

    # Verify acceptable-reply independently — broader than the original
    # offline-only check. Acceptable replies (any kind) mean "leave alone":
    #   offline: agreed in standup / out-of-band / followup-PR
    #   jira:    "tracked in PROJ-1234" / "moved to INFRA-42"
    #   synced:  "synced with @alice" / "per chat with @bob"
    valid_reply_kind: str | None = None
    valid_reply_detail: str | None = None
    for c in thread_state["thread"]:
        kind, detail = classify_reply(c.get("body", ""))
        if kind:
            valid_reply_kind = kind
            valid_reply_detail = detail
            break
    verified_offline = (valid_reply_kind == "offline")
    result["offline_alignment_verified"] = verified_offline
    result["valid_reply"] = {
        "kind": valid_reply_kind,
        "detail": valid_reply_detail,
    } if valid_reply_kind else None
    if claimed_offline and not verified_offline:
        result["verifier_note"] += " | model claimed offline but no marker found; downgrading"
        result["offline_alignment_detected"] = False

    # Apply state-transition rules (see references/comment-resolution.md).
    currently_resolved = thread_state.get("resolved", False)
    if valid_reply_kind:
        result["decision"] = "leave-as-is"
        result["verifier_note"] += f" | acceptable-reply ({valid_reply_kind}), leaving as-is"
        result["verified"] = True
        return result

    if decision == "resolve":
        if currently_resolved:
            result["verifier_note"] += " | already resolved, leaving as-is"
            result["decision"] = "leave-as-is"
            result["verified"] = True
            return result
        # Verify diff touched the anchored line.
        first = thread_state["thread"][0]
        path = first.get("path")
        line = first.get("line")
        touched_ranges = touched.get(path, []) if path else []
        line_touched = any(a <= (line or 0) <= b for (a, b) in touched_ranges)
        if not line_touched:
            result["verifier_note"] += " | claimed fixed but diff did not touch anchored line; downgrading to leave-as-is"
            result["decision"] = "leave-as-is"
            return result
        result["verified"] = True
        return result

    if decision == "reopen":
        if not currently_resolved:
            result["verifier_note"] += " | thread already open, reopen is a no-op"
            result["decision"] = "leave-as-is"
            result["verified"] = True
            return result
        # If diff touched the anchored line, the resolution might be justified — downgrade.
        first = thread_state["thread"][0]
        path = first.get("path")
        line = first.get("line")
        touched_ranges = touched.get(path, []) if path else []
        line_touched = any(a <= (line or 0) <= b for (a, b) in touched_ranges)
        if line_touched:
            result["verifier_note"] += " | diff touched anchored line; reopen is questionable"
            # Still allow if the model claims confidently AND not offline-aligned.
        result["verified"] = True
        return result

    # leave-as-is — always allowed.
    result["verified"] = True
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    log = get_logger("comment_resolver", task_dir)
    pr_json = pr_review_file(task_dir, "pr.json")
    cm_json = pr_review_file(task_dir, "pr-comments.json")
    findings = pr_review_file(task_dir, "findings.json")
    diff = pr_review_file(task_dir, "diff.patch")

    if not pr_json.exists():
        die(f"missing {pr_json}")
    if not cm_json.exists():
        die(f"missing {cm_json}")

    pr = read_json(pr_json)
    comments_blob = read_json(cm_json)
    threads = normalize_threads(pr, comments_blob)
    touched = lines_touched_by_diff(diff.read_text(encoding="utf-8", errors="replace")) if diff.exists() else {}

    proposed: list[dict] = []
    findings_blob: dict = {}
    if findings.exists():
        findings_blob = read_json(findings)
        proposed = findings_blob.get("existing_comment_actions", [])

    verified = [verify_action(a, threads, touched, log) for a in proposed]

    # Auto-classify orphan threads — every thread the model did NOT name in
    # existing_comment_actions[] still needs a decision (user requirement:
    # every comment must be reviewed). The auto-classification follows the
    # same rules as verify_action; it lands with `auto_classified: true`
    # so the report can surface "the AI didn't propose anything for these".
    addressed_ids = {str(a.get("comment_id")) for a in proposed if a.get("comment_id")}
    for root_id, t in threads.items():
        thread_ids = {c["id"] for c in t["thread"]}
        if thread_ids & addressed_ids:
            continue  # at least one comment in this thread already addressed
        auto = _auto_classify_thread(t, touched)
        auto["auto_classified"] = True
        verified.append(auto)

    # Approve-readiness. The PR is "approve-ready" when:
    #   (a) the AI's findings carry no blocker/critical severity, and
    #   (b) no thread is left UNRESOLVED-and-unfixed (no open finding-equivalent).
    findings_list = findings_blob.get("findings", []) or []
    blocking_severities = {"blocker", "critical"}
    has_blocker = any((f.get("severity") in blocking_severities) for f in findings_list)
    unresolved_blocking_threads = [
        v for v in verified
        if v.get("decision") == "reopen" and v.get("verified")
    ]
    approve_ready = (not has_blocker) and (not unresolved_blocking_threads)

    out = {
        "task_dir": str(task_dir),
        "host": pr.get("host"),
        "n_threads": len(threads),
        "n_actions_proposed": len(proposed),
        "n_actions_auto_classified": sum(1 for v in verified if v.get("auto_classified")),
        "n_actions_verified": sum(1 for v in verified if v.get("verified")),
        "approve_ready": approve_ready,
        "approve_ready_reason": (
            "no blocker/critical findings AND no thread requires reopen"
            if approve_ready
            else f"has_blocker={has_blocker}, threads_to_reopen={len(unresolved_blocking_threads)}"
        ),
        "actions": verified,
    }
    write_json(pr_review_file(task_dir, "comment-actions.json"), out)
    if args.json:
        return emit_json(out)
    log.info("verified %d/%d actions (%d auto-classified) · approve_ready=%s",
             out["n_actions_verified"], out["n_actions_proposed"],
             out["n_actions_auto_classified"], approve_ready)
    return 0


def _auto_classify_thread(thread_state: dict, touched: dict) -> dict:
    """Classify an orphan thread (no model action) using the same rules.

    Same shape as verify_action's return, but with a leading auto-pass:
    - acceptable reply present → leave-as-is
    - currently OPEN + diff touched anchored line → resolve
    - currently RESOLVED + diff did not touch + no acceptable reply → reopen
    - everything else → leave-as-is (ambiguous)
    """
    root_id = thread_state.get("root_id")
    root = thread_state["thread"][0] if thread_state["thread"] else {}
    cid = str(root.get("id") or root_id or "")
    currently_resolved = bool(thread_state.get("resolved", False))
    path = root.get("path")
    line = root.get("line")
    touched_ranges = touched.get(path, []) if path else []
    line_touched = any(a <= (line or 0) <= b for (a, b) in touched_ranges)

    # Check every reply for an acceptable disposition.
    valid_reply_kind: str | None = None
    valid_reply_detail: str | None = None
    for c in thread_state["thread"]:
        kind, detail = classify_reply(c.get("body", ""))
        if kind:
            valid_reply_kind = kind
            valid_reply_detail = detail
            break

    result: dict = {
        "comment_id": cid,
        "thread_root": root_id,
        "thread_currently_resolved": currently_resolved,
        "verified": True,
        "valid_reply": ({"kind": valid_reply_kind, "detail": valid_reply_detail}
                         if valid_reply_kind else None),
    }
    if valid_reply_kind:
        result["decision"] = "leave-as-is"
        result["reason"] = f"acceptable reply ({valid_reply_kind}): {valid_reply_detail or '-'}"
        return result
    if not currently_resolved and line_touched:
        result["decision"] = "resolve"
        result["reason"] = f"diff touched anchored line {path}:{line}"
        return result
    if currently_resolved and not line_touched:
        result["decision"] = "reopen"
        result["reason"] = "thread is RESOLVED but the diff did not touch the anchored line and no acceptable reply"
        return result
    result["decision"] = "leave-as-is"
    result["reason"] = "ambiguous — no clear signal from diff or replies"
    return result


if __name__ == "__main__":
    raise SystemExit(main())
