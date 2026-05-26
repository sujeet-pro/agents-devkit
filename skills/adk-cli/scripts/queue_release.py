"""queue_release.py — post-review queue + Slack update.

Called by /adk-pr-review's report.py at the tail of a review. Given the review
outcome (n_findings, host approval state, recommendation), it:

  1. Computes the new queue status:
        n_findings > 0                   → STATUS_COMMENTS
        elif approved (host OR rec)      → STATUS_APPROVED
        else                             → STATUS_REVIEWED
  2. Clears `taken_at` and writes status, head_sha, last_checked_at.
  3. If a slack config + slack_info are present, updates the message's
     reaction emoji to reflect the new status. Transitioning into approved
     or merged also sweeps every other configured status emoji off the
     message defensively.
  4. Returns the new status string.

No-ops cleanly when the PR isn't in the queue — /adk-pr-review can call this
unconditionally and the URL-only path still works.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH,
    find_row, update_pr_entry,
    merge_slack_threads, slack_threads_for,
    STATUS_APPROVED, STATUS_COMMENTS, STATUS_REVIEWED, STATUS_MERGED,
    TERMINAL_OR_POSITIVE, REVIEW_ATTEMPT_SUCCEEDED,
)

REQUEST_CHANGES_STATUS = "request_changes"


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compute_new_status(n_findings: int, approved_host: bool, recommendation: str | None) -> str:
    if n_findings > 0:
        return STATUS_COMMENTS
    if approved_host or (recommendation == "approve"):
        return STATUS_APPROVED
    return STATUS_REVIEWED


def _compute_slack_reaction_status(
    queue_status: str,
    *,
    approved_host: bool,
    recommendation: str | None,
    approve_ready: bool,
    host_requested_changes: bool,
) -> str:
    """Return the status emoji Slack should show.

    Queue status and Slack status are intentionally different: the queue keeps
    `comments` for "approved with non-blocking comments" bookkeeping, while
    Slack should show `approved` once the host approval was or will be applied.
    """
    if queue_status == STATUS_MERGED:
        return STATUS_MERGED
    if host_requested_changes:
        return REQUEST_CHANGES_STATUS
    if approved_host or (recommendation == "approve" and approve_ready):
        return STATUS_APPROVED
    return STATUS_COMMENTS


def _short_tldr(status: str, n_findings: int, recommendation: str | None) -> str:
    """Default one-liner TL;DR when the caller hasn't provided a summary."""
    if status == STATUS_APPROVED:
        return "no blocking findings; auto-approve gate passed."
    if status == STATUS_COMMENTS:
        return f"{n_findings} comment(s) posted; review the inline notes."
    return f"reviewed; recommendation: {recommendation or 'comment_only'}."


def update_slack_reaction(slack_info: dict, new_status: str, slack_cfg: dict, log=None) -> dict:
    """Record the new status in slack_info. Reaction side-effects are dropped.

    Returns the updated slack_info dict.
    """
    thread_pr_count = slack_info.get("thread_pr_count",
                                     slack_info.get("n_pr_links_in_message", 1))
    if thread_pr_count and thread_pr_count > 1:
        if log:
            log.info("slack: multi-PR thread (count=%d); reply-mode verdict only for %s",
                     thread_pr_count, new_status)
        slack_info["last_reaction_status"] = None
        return slack_info

    slack_info["last_reaction_status"] = new_status
    return slack_info


def release_after_review(
    *,
    queue_path: Path,
    pr_url: str,
    head_sha: str | None,
    n_findings: int,
    approved_host: bool,
    recommendation: str | None,
    approve_ready: bool = False,
    host_requested_changes: bool = False,
    slack_cfg: dict | None = None,
    slack_info: dict | None = None,
    pr: dict | None = None,
    bullets: list[str] | None = None,
    summary_tldr: str | None = None,
    no_slack_reply: bool = False,
    log=None,
) -> str | None:
    """Update the queue + slack reaction after a review completes. Returns
    the new status, or None if the PR wasn't in the queue.

    When `pr` is provided (the pr.json dict), and the queue row has a Slack
    thread, ALSO post the §6.y.1 3-section review reply into the thread.
    Pass `no_slack_reply=True` to suppress the reply (the reaction flip
    still happens).
    """
    entry = find_row(queue_path, pr_url)
    if entry is None:
        return None

    new_status = _compute_new_status(n_findings, approved_host, recommendation)

    # Don't downgrade a merged row (queue_io._apply_updates already enforces this,
    # but bail out early so we don't waste a Slack call).
    if entry.get("status") == STATUS_MERGED:
        return STATUS_MERGED

    merged_slack_threads: list[dict] = []
    incoming_threads = slack_threads_for(slack_info)
    if slack_info and not incoming_threads:
        incoming_threads = [dict(slack_info)]
    slack_targets = merge_slack_threads(
        slack_threads_for(entry), incoming_threads, prefer_incoming=True
    )
    if slack_cfg and slack_targets:
        try:
            slack_status = _compute_slack_reaction_status(
                new_status,
                approved_host=approved_host,
                recommendation=recommendation,
                approve_ready=approve_ready,
                host_requested_changes=host_requested_changes,
            )
        except Exception:
            slack_status = new_status

        rendered_reply: str | None = None
        reply_client = None
        for target in slack_targets:
            si = dict(target)
            try:
                si = update_slack_reaction(si, slack_status, slack_cfg, log=log)
            except Exception as e:
                if log:
                    log.warning("slack reaction update failed for %s/%s: %s",
                                si.get("channel_id"), si.get("thread_ts"), e)

            # v4 §6.y.1: post the 3-section review reply to every Slack origin.
            if (pr is not None and not no_slack_reply
                    and si.get("channel_id") and si.get("thread_ts")
                    and not si.get("slack_reply_ts")):
                try:
                    from slack_helpers import (  # noqa: WPS433 — lazy
                        SlackClient, render_review_reply, post_review_slack_reply,
                    )
                    if reply_client is None:
                        reply_client = SlackClient()
                    if rendered_reply is None:
                        rendered_reply = render_review_reply(
                            host=pr.get("host") or "github",
                            owner=pr.get("owner") or "",
                            repo=pr.get("repo") or "",
                            pr_number=int(pr.get("pr_number") or 0),
                            pr_url=pr.get("url") or pr_url,
                            head_sha=pr.get("head_sha") or head_sha,
                            author_login=(pr.get("author") or {}).get("login")
                                          if isinstance(pr.get("author"), dict)
                                          else pr.get("author"),
                            status=new_status,
                            summary_tldr=summary_tldr or _short_tldr(
                                new_status, n_findings, recommendation
                            ),
                            bullets=bullets or [],
                        )
                    reply_ts = post_review_slack_reply(
                        reply_client,
                        channel_id=si["channel_id"],
                        thread_ts=si["thread_ts"],
                        text=rendered_reply,
                        log=log,
                    )
                    if reply_ts:
                        si["slack_reply_ts"] = reply_ts
                except Exception as e:
                    if log:
                        log.warning("slack review reply failed for %s/%s (non-fatal): %s",
                                    si.get("channel_id"), si.get("thread_ts"), e)
            merged_slack_threads.append(si)

    # Persist approved_host + recommendation alongside status so the
    # ready-to-merge summary can distinguish "approved with open comments"
    # from "reviewed (commented but not approved)". Without these the bucket
    # collapses and we mislabel `status=comments` rows as "approved".
    #
    # `last_reviewed_head_sha` + `last_reviewed_at` let `acquire_next_row`
    # skip rows whose head hasn't moved since the previous review — so the
    # queue-mode drain doesn't re-review the same commit twice. Explicit
    # URL invocations bypass this filter and re-review anyway.
    now = _now_iso()
    updates = {
        "status": new_status,
        "last_checked_at": now,
        "taken_at": None,
        "taken_by": None,
        "approved_host": bool(approved_host),
        "recommendation": recommendation,
        "approve_ready": bool(approve_ready),
        "last_reviewed_at": now,
        "last_successful_review_at": now,
        "last_review_attempt_at": now,
        "last_review_attempt_status": REVIEW_ATTEMPT_SUCCEEDED,
        "last_review_attempt_error": None,
    }
    if head_sha:
        updates["head_sha"] = head_sha
        updates["last_reviewed_head_sha"] = head_sha
        updates["last_review_attempt_head_sha"] = head_sha
    if entry.get("comment_activity_hash"):
        updates["last_reviewed_comment_activity_hash"] = entry.get("comment_activity_hash")
        updates["last_review_attempt_comment_activity_hash"] = entry.get("comment_activity_hash")
    if merged_slack_threads:
        updates["slack_threads"] = merged_slack_threads
        updates["slack"] = merged_slack_threads[0]
    update_pr_entry(queue_path, pr_url, updates)
    return new_status
