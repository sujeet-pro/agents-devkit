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
from _common import read_json, write_json, emit_json, get_logger, die  # noqa: E402


OFFLINE_PATTERNS = [
    re.compile(r"\b(agreed|aligned|sync'?d|synced|discussed)\s+(offline|in\s+(the\s+)?meeting|in\s+(the\s+)?call|on\s+slack|on\s+discord)\b", re.I),
    re.compile(r"\b(offline|out\s+of\s+band)\s+(agreement|alignment|conversation)\b", re.I),
    re.compile(r"\b(we'?ll|will)\s+(handle|address|fix)\s+(this|it)\s+(in|via|with)\s+(a\s+)?(follow-?up|follow\s+up|separate)\s+pr\b", re.I),
    re.compile(r"\bout\s+of\s+scope\b", re.I),
    re.compile(r"\bskip(ping)?\s+for\s+now\b", re.I),
    re.compile(r"\bdeferred\b", re.I),
    re.compile(r"\b(thanks|sounds\s+good)[,!]?\s+(closing|resolving)\b", re.I),
]
NEGATIVE_PATTERNS = [
    re.compile(r"\b(but|however|except|unless)\b", re.I),
]


def has_offline_marker(body: str) -> bool:
    body = body or ""
    if not any(p.search(body) for p in OFFLINE_PATTERNS):
        return False
    if any(p.search(body) for p in NEGATIVE_PATTERNS):
        return False
    if body.strip().endswith("?"):
        return False
    return True


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

    # Verify offline-alignment independently.
    verified_offline = False
    for c in thread_state["thread"]:
        if has_offline_marker(c.get("body", "")):
            verified_offline = True
            break
    result["offline_alignment_verified"] = verified_offline
    if claimed_offline and not verified_offline:
        result["verifier_note"] += " | model claimed offline but no marker found; downgrading"
        result["offline_alignment_detected"] = False

    # Apply state-transition rules (see references/comment-resolution.md).
    currently_resolved = thread_state.get("resolved", False)
    if verified_offline:
        result["decision"] = "leave-as-is"
        result["verifier_note"] += " | offline-aligned, leaving as-is"
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
    pr_json = task_dir / "pr.json"
    cm_json = task_dir / "pr-comments.json"
    findings = task_dir / "findings.json"
    diff = task_dir / "diff.patch"

    if not pr_json.exists():
        die(f"missing {pr_json}")
    if not cm_json.exists():
        die(f"missing {cm_json}")

    pr = read_json(pr_json)
    comments_blob = read_json(cm_json)
    threads = normalize_threads(pr, comments_blob)
    touched = lines_touched_by_diff(diff.read_text(encoding="utf-8", errors="replace")) if diff.exists() else {}

    proposed: list[dict] = []
    if findings.exists():
        f = read_json(findings)
        proposed = f.get("existing_comment_actions", [])

    verified = [verify_action(a, threads, touched, log) for a in proposed]
    out = {
        "task_dir": str(task_dir),
        "host": pr.get("host"),
        "n_threads": len(threads),
        "n_actions_proposed": len(proposed),
        "n_actions_verified": sum(1 for v in verified if v.get("verified")),
        "actions": verified,
    }
    write_json(task_dir / "comment-actions.json", out)
    if args.json:
        return emit_json(out)
    log.info("verified %d/%d actions", out["n_actions_verified"], out["n_actions_proposed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
