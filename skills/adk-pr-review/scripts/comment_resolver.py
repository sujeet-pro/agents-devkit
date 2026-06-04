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

ADK_CLI_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))
from queue_io import update_pr_entry, _now_iso as _queue_now_iso  # noqa: E402


OFFLINE_PATTERNS = [
    re.compile(r"\b(agreed|aligned|sync'?d|synced|discussed)\s+(offline|in\s+(the\s+)?meeting|in\s+(the\s+)?call|on\s+slack|on\s+discord)\b", re.I),
    re.compile(r"\b(offline|out\s+of\s+band)\s+(agreement|alignment|conversation)\b", re.I),
    re.compile(r"\b(we'?ll|will)\s+(handle|address|fix)\s+(this|it)\s+(in|via|with)\s+(a\s+)?(follow-?up|follow\s+up|separate)\s+pr\b", re.I),
    # Deferral to a DIFFERENT changeset — verb-agnostic. "done in next PR",
    # "in a follow-up PR", "to a separate patch", "via a later diff". Note the
    # adjective list deliberately omits "this" (staying in this PR, not
    # deferring) and the noun list omits "commit" (a "next commit" usually
    # means a fix is incoming to THIS PR, so the thread should stay open).
    re.compile(r"\b(?:in|via|with|to)\s+(?:a\s+|an\s+|the\s+)?(?:follow-?up|follow\s+up|separate|next|later|subsequent|future|another)\s+(?:prs?|mrs?|patch(?:es)?|change(?:set)?s?|diffs?)\b", re.I),
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

# "Synced with @person" / "spoke to @person" / "as discussed with Sujeet" —
# explicit human alignment. We accept an @-handle OR a capitalised proper name
# (see extract_synced_with). A bare lowercase word ("with the team", "with
# care") is rejected: we want a specific accountable human so the report can
# name who took the decision.
SYNCED_WITH_PATTERNS = [
    re.compile(r"\b(?:synced|sync'?d|spoke|spoken|talked|aligned|discussed)\s+(?:with|to)\s+(@?[A-Za-z][\w.'-]{1,40})\b", re.I),
    re.compile(r"\b(?:per|as\s+per|per\s+chat\s+with)\s+(@?[A-Za-z][\w.'-]{1,40})\b", re.I),
]

# Generic group words that are NOT specific accountable people. Even when
# capitalised ("the Team"), these don't name an individual, so a "discussed
# with <these>" reply is not a "synced" disposition.
_SYNC_STOPWORDS = {
    "team", "teams", "everyone", "everybody", "group", "folks", "all",
    "you", "him", "her", "them", "us", "someone", "people", "others",
    "ourselves", "myself", "yourself", "the", "a", "an",
}

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
    """Return the person (handle or name) if the reply names a sync partner.

    Accepts either an @-handle ("synced with @alice") or a capitalised proper
    name ("as discussed with Sujeet"). A bare lowercase word after "with"/"to"
    is rejected — "discussed with care" / "talked with the team" must not count
    — because we need a specific accountable human for the report to name.
    """
    body = body or ""
    if not _passes_negatives(body):
        return None
    for p in SYNCED_WITH_PATTERNS:
        m = p.search(body)
        if not m:
            continue
        raw = m.group(1)
        if raw.startswith("@"):
            return raw.lstrip("@") or None
        # No @ — require a capitalised proper name, and reject generic groups.
        if raw[:1].isupper() and raw.lower() not in _SYNC_STOPWORDS:
            return raw
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


def _extract_general_comments(comments_blob: dict, host: str) -> list[dict]:
    """Extract non-inline (PR-level general) comments from the comments blob.

    GitHub  → ``issue_comments`` list (no path/line anchors).
    Bitbucket → items in ``comments`` whose ``inline.path`` is absent/empty.
    Each returned item is normalised to ``{id, body, user, parent_id|None}``.
    """
    out: list[dict] = []
    if host == "github":
        for c in (comments_blob.get("issue_comments") or []):
            out.append({
                "id": str(c.get("id")),
                "body": c.get("body") or "",
                "user": (c.get("user") or {}).get("login"),
                "parent_id": None,
            })
    elif host == "bitbucket":
        for c in (comments_blob.get("comments") or []):
            inline = c.get("inline") or {}
            if not inline.get("path"):
                parent = c.get("parent") or {}
                out.append({
                    "id": str(c.get("id")),
                    "body": ((c.get("content") or {}).get("raw") or ""),
                    "user": (c.get("user") or {}).get("display_name"),
                    "parent_id": str(parent["id"]) if parent.get("id") else None,
                })
    return out


def scan_general_comments_for_signals(general_comments: list[dict]) -> list[dict]:
    """Scan general (non-inline) PR comments for acceptable-reply patterns.

    Returns a list of signal dicts for any comment that carries a recognised
    disposition marker::

        {id, user, body_snippet, kind, detail}

    ``kind`` is one of ``"offline"``, ``"jira"``, ``"synced"`` — the same values
    ``classify_reply`` returns for thread replies.

    General-comment signals are treated as lower-confidence than a direct reply
    to the thread, but they are still actionable: a PR-level "agreed offline,
    we'll fix in a follow-up" from the author is a valid disposition for ALL
    open inline threads.
    """
    signals: list[dict] = []
    for c in general_comments:
        body = c.get("body") or ""
        if not body.strip():
            continue
        kind, detail = classify_reply(body)
        if kind:
            signals.append({
                "id": c.get("id"),
                "user": c.get("user"),
                "body_snippet": body.strip().split("\n", 1)[0][:160],
                "kind": kind,
                "detail": detail,
            })
    return signals


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


def parse_diff_changes(diff_text: str) -> tuple[dict[str, list[tuple[int, int]]], set[str]]:
    """Return (touched, deleted).

    touched: map of file path (new side) → list of (added_line_start, added_line_end) ranges.
    deleted: set of file paths (old side) that were removed entirely (`+++ /dev/null`).

    Deletion is a stronger signal of resolution than a line-level touch — the
    file is gone, so any anchored concern on it is moot. The previous parser
    keyed only by the new side and silently dropped deletions, which caused
    legitimate resolve decisions to be downgraded to leave-as-is.
    """
    touched: dict[str, list[tuple[int, int]]] = {}
    deleted: set[str] = set()
    old_path: str | None = None
    new_path: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("--- "):
            old_path = line[4:].strip()
            if old_path.startswith("a/"):
                old_path = old_path[2:]
            if old_path == "/dev/null":
                old_path = None
            continue
        if line.startswith("+++ "):
            new_path = line[4:].strip()
            if new_path.startswith("b/"):
                new_path = new_path[2:]
            if new_path == "/dev/null":
                # File deleted — the OLD path is gone.
                if old_path:
                    deleted.add(old_path)
                new_path = None
            continue
        if line.startswith("@@") and new_path:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                a_start = int(m.group(1))
                a_count = int(m.group(2) or "1")
                if a_count > 0:
                    touched.setdefault(new_path, []).append((a_start, a_start + a_count - 1))
    return touched, deleted

# When the diff doesn't touch the exact anchored line, but touches a nearby
# line, treat that as evidence of resolution with a low-confidence note.
# 5 lines accommodates refactors that shift line numbers by a small amount.
_RESOLVE_PROXIMITY_LINES = 5


def _line_touch_evidence(path: str | None, line: int | None,
                          touched: dict, deleted: set[str]) -> tuple[bool, str]:
    """Return (verified, note) describing how the diff addresses this anchor.

    Tiered:
      file deleted     → strongest; the concern is moot.
      exact line       → strong; verified.
      ±N lines         → medium; verified with proximity note.
      otherwise        → not verified.
    """
    if not path:
        return False, "no file path on the anchored comment"
    if path in deleted:
        return True, f"file `{path}` deleted in the diff"
    if not line:
        return False, "no line number on the anchored comment"
    ranges = touched.get(path, [])
    if not ranges:
        return False, "diff did not touch this file"
    if any(a <= line <= b for (a, b) in ranges):
        return True, f"diff touched anchored line {path}:{line}"
    # Proximity check — the line number may have shifted due to a refactor.
    for a, b in ranges:
        if (a - _RESOLVE_PROXIMITY_LINES) <= line <= (b + _RESOLVE_PROXIMITY_LINES):
            return True, (f"diff touched {path}:{a}-{b} (within "
                          f"{_RESOLVE_PROXIMITY_LINES} lines of anchor {line})")
    return False, "diff did not touch anchored line or its vicinity"


def verify_action(action: dict, threads: dict, touched: dict, log,
                  deleted: set[str] | None = None,
                  general_signals: list[dict] | None = None) -> dict:
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
    first_comment = thread_state["thread"][0] if thread_state.get("thread") else {}
    result["actionable"] = bool(first_comment.get("path"))

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
        if currently_resolved:
            result["decision"] = "leave-as-is"
            result["verifier_note"] += f" | acceptable-reply ({valid_reply_kind}), already resolved"
        else:
            result["decision"] = "resolve"
            result["verifier_note"] += f" | acceptable-reply ({valid_reply_kind}), resolving thread"
        result["verified"] = True
        return result

    # No direct-reply signal — check if any general PR comment carries an
    # acceptable-reply marker that applies to this inline thread.
    if general_signals and not currently_resolved:
        gen_sig = general_signals[0]  # use the first (most recent scan order) signal
        result["verifier_note"] += (
            f" | general-comment signal ({gen_sig['kind']})"
            f" from comment {gen_sig['id']}"
        )
        result["decision"] = "resolve"
        result["resolved_via_general_comment"] = True
        result["general_comment_id"] = gen_sig["id"]
        result["general_comment_user"] = gen_sig.get("user")
        result["general_comment_snippet"] = gen_sig["body_snippet"]
        result["general_comment_signal_kind"] = gen_sig["kind"]
        result["verified"] = True
        return result

    deleted_files: set[str] = deleted or set()
    if decision == "resolve":
        if currently_resolved:
            result["verifier_note"] += " | already resolved, leaving as-is"
            result["decision"] = "leave-as-is"
            result["verified"] = True
            return result
        first = thread_state["thread"][0]
        ok, evidence = _line_touch_evidence(first.get("path"), first.get("line"),
                                             touched, deleted_files)
        result["verifier_evidence"] = evidence
        if not ok:
            result["verifier_note"] += f" | resolve claim not supported ({evidence}); downgrading to leave-as-is"
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
        first = thread_state["thread"][0]
        ok, evidence = _line_touch_evidence(first.get("path"), first.get("line"),
                                             touched, deleted_files)
        result["verifier_evidence"] = evidence
        if ok:
            # Diff addresses the concern; the resolution is justified, reopen
            # is questionable. Log but allow if the model insists.
            result["verifier_note"] += f" | diff addresses concern ({evidence}); reopen is questionable"
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
    if diff.exists():
        touched, deleted = parse_diff_changes(diff.read_text(encoding="utf-8", errors="replace"))
    else:
        touched, deleted = {}, set()

    # Extract PR-level general comments (GitHub issue_comments / Bitbucket
    # non-inline comments) and scan them for acceptable-reply patterns.
    # These are passed to verify_action and _auto_classify_thread as an
    # additional signal source so that a PR-level "agreed offline, handling
    # in a follow-up" can drive resolution of all open inline threads.
    host = host_of(pr)
    general_comments = _extract_general_comments(comments_blob, host)
    general_signals = scan_general_comments_for_signals(general_comments)

    proposed: list[dict] = []
    findings_blob: dict = {}
    if findings.exists():
        findings_blob = read_json(findings)
        proposed = findings_blob.get("existing_comment_actions", [])

    verified = [
        verify_action(a, threads, touched, log, deleted=deleted,
                      general_signals=general_signals or None)
        for a in proposed
    ]

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
        auto = _auto_classify_thread(t, touched, deleted=deleted,
                                     general_signals=general_signals or None)
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
    unresolved_ambiguous_threads = [
        v for v in verified
        if v.get("decision") == "leave-as-is"
        and v.get("verified")
        and v.get("actionable")
        and not v.get("thread_currently_resolved")
        and not v.get("valid_reply")
    ]
    approve_ready = (
        (not has_blocker)
        and (not unresolved_blocking_threads)
        and (not unresolved_ambiguous_threads)
    )

    n_resolved_via_general = sum(
        1 for v in verified if v.get("resolved_via_general_comment")
    )
    out = {
        "task_dir": str(task_dir),
        "host": pr.get("host"),
        "n_threads": len(threads),
        "n_general_comments": len(general_comments),
        "n_general_signals": len(general_signals),
        "n_resolved_via_general_comment": n_resolved_via_general,
        "general_signals": general_signals,
        "n_actions_proposed": len(proposed),
        "n_actions_auto_classified": sum(1 for v in verified if v.get("auto_classified")),
        "n_actions_verified": sum(1 for v in verified if v.get("verified")),
        "approve_ready": approve_ready,
        "approve_ready_reason": (
            "no blocker/critical findings AND no thread requires reopen"
            if approve_ready
            else (
                f"has_blocker={has_blocker}, "
                f"threads_to_reopen={len(unresolved_blocking_threads)}, "
                f"ambiguous_open_threads={len(unresolved_ambiguous_threads)}"
            )
        ),
        "actions": verified,
    }
    write_json(pr_review_file(task_dir, "comment-actions.json"), out)

    # Stamp the queue row with validation completion time + head_sha.
    head_sha = pr.get("head_sha")
    pr_url = pr.get("url")
    queue_ctx_path = pr_review_file(task_dir, "queue-context.json")
    if pr_url and queue_ctx_path.exists():
        try:
            queue_ctx = read_json(queue_ctx_path)
            queue_path_str = queue_ctx.get("queue_path")
            if queue_path_str:
                _stamp: dict = {"last_validated_at": _queue_now_iso()}
                if head_sha:
                    _stamp["last_validated_head_sha"] = head_sha
                update_pr_entry(Path(queue_path_str), pr_url, _stamp)
        except Exception:
            pass  # stamping is best-effort; never block the resolver

    if args.json:
        return emit_json(out)
    log.info("verified %d/%d actions (%d auto-classified, %d via general-comment) · "
             "approve_ready=%s · general_signals=%d",
             out["n_actions_verified"], out["n_actions_proposed"],
             out["n_actions_auto_classified"], n_resolved_via_general,
             approve_ready, len(general_signals))
    return 0


def _auto_classify_thread(thread_state: dict, touched: dict,
                            deleted: set[str] | None = None,
                            general_signals: list[dict] | None = None) -> dict:
    """Classify an orphan thread (no model action) using the same rules.

    Same shape as verify_action's return, but with a leading auto-pass:
    - acceptable reply present → leave-as-is
    - currently OPEN + diff addresses anchor (touched, near anchor, or
      file deleted) → resolve
    - currently OPEN + general-comment signal present → resolve (with
      ``resolved_via_general_comment`` flag so the posting plan prepends a
      reply before marking the thread resolved)
    - currently RESOLVED + diff did not address anchor + no acceptable reply
      → reopen
    - everything else → leave-as-is (ambiguous)
    """
    deleted_files: set[str] = deleted or set()
    root_id = thread_state.get("root_id")
    root = thread_state["thread"][0] if thread_state["thread"] else {}
    cid = str(root.get("id") or root_id or "")
    currently_resolved = bool(thread_state.get("resolved", False))
    path = root.get("path")
    line = root.get("line")
    diff_addresses, evidence = _line_touch_evidence(path, line, touched, deleted_files)

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
        "actionable": bool(path),
        "verified": True,
        "verifier_evidence": evidence,
        "valid_reply": ({"kind": valid_reply_kind, "detail": valid_reply_detail}
                         if valid_reply_kind else None),
    }
    if valid_reply_kind:
        if currently_resolved:
            result["decision"] = "leave-as-is"
            result["reason"] = f"acceptable reply ({valid_reply_kind}): {valid_reply_detail or '-'}"
        else:
            result["decision"] = "resolve"
            result["reason"] = f"acceptable reply ({valid_reply_kind}): {valid_reply_detail or '-'}"
        return result
    if not currently_resolved and diff_addresses:
        result["decision"] = "resolve"
        result["reason"] = evidence
        return result
    # No direct-reply signal and diff didn't touch the anchor — check if a
    # general PR comment carries a resolution marker applicable to this thread.
    if not currently_resolved and general_signals:
        gen_sig = general_signals[0]
        result["decision"] = "resolve"
        result["reason"] = (
            f"general-comment signal ({gen_sig['kind']})"
            f" from comment {gen_sig['id']}: {gen_sig['body_snippet']}"
        )
        result["resolved_via_general_comment"] = True
        result["general_comment_id"] = gen_sig["id"]
        result["general_comment_user"] = gen_sig.get("user")
        result["general_comment_snippet"] = gen_sig["body_snippet"]
        result["general_comment_signal_kind"] = gen_sig["kind"]
        return result
    if currently_resolved and not diff_addresses:
        result["decision"] = "reopen"
        result["reason"] = "thread is RESOLVED but the diff did not address the anchor and no acceptable reply"
        return result
    result["decision"] = "leave-as-is"
    result["reason"] = "ambiguous — no clear signal from diff or replies"
    return result


if __name__ == "__main__":
    raise SystemExit(main())
