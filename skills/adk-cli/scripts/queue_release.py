"""queue_release.py — post-review queue + Slack update.

Called by /adk-pr-review's report.py at the tail of a review. Given the review
outcome (n_findings, host approval state, recommendation), it:

  1. Computes the new queue status using the same mapping the legacy batch
     driver used:
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
    STATUS_APPROVED, STATUS_COMMENTS, STATUS_REVIEWED, STATUS_MERGED,
    TERMINAL_OR_POSITIVE,
)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _compute_new_status(n_findings: int, approved_host: bool, recommendation: str | None) -> str:
    if n_findings > 0:
        return STATUS_COMMENTS
    if approved_host or (recommendation == "approve"):
        return STATUS_APPROVED
    return STATUS_REVIEWED


def _short_tldr(status: str, n_findings: int, recommendation: str | None) -> str:
    """Default one-liner TL;DR when the caller hasn't provided a summary."""
    if status == STATUS_APPROVED:
        return "no blocking findings; auto-approve gate passed."
    if status == STATUS_COMMENTS:
        return f"{n_findings} comment(s) posted; review the inline notes."
    return f"reviewed; recommendation: {recommendation or 'comment_only'}."


def update_slack_reaction(slack_info: dict, new_status: str, slack_cfg: dict, log=None) -> dict:
    """Reconcile slack reactions to reflect `new_status`.

    Normal transitions: remove `last_reaction_status` emoji, add the new one.
    Transitions to a terminal-positive status (approved/merged): sweep every OTHER
    configured status emoji off the message defensively, in case a prior reaction
    wasn't tracked in `last_reaction_status`. The new status's emoji is the only
    one left.

    Returns the updated slack_info dict.
    """
    status_emoji = (slack_cfg or {}).get("status_emoji") or {}
    new_emoji = status_emoji.get(new_status)
    last_status = slack_info.get("last_reaction_status")
    last_emoji = status_emoji.get(last_status) if last_status else None

    channel_id = slack_info.get("channel_id")
    message_ts = slack_info.get("message_ts")
    if not channel_id or not message_ts:
        return slack_info

    is_terminal_positive = new_status in TERMINAL_OR_POSITIVE
    if not new_emoji and not is_terminal_positive:
        if log:
            log.info("slack: no emoji configured for status=%s; skipping reaction update", new_status)
        slack_info["last_reaction_status"] = new_status
        return slack_info

    # Lazy import — slack-sdk only needed when we actually post.
    from slack_helpers import SlackClient  # type: ignore
    client = SlackClient()

    if is_terminal_positive:
        for st, em in status_emoji.items():
            if not em:
                continue
            if em == new_emoji:
                continue
            client.remove_reaction(channel_id, message_ts, em)
        if log:
            log.info("slack: terminal transition to %s — swept other status emojis", new_status)
    elif last_emoji and last_emoji != new_emoji:
        client.remove_reaction(channel_id, message_ts, last_emoji)

    if new_emoji:
        client.add_reaction(channel_id, message_ts, new_emoji)

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

    merged_slack: dict | None = None
    if slack_cfg and (slack_info or entry.get("slack")):
        si = dict(entry.get("slack") or {})
        if slack_info:
            si.update(slack_info)
        try:
            merged_slack = update_slack_reaction(si, new_status, slack_cfg, log=log)
        except Exception as e:
            if log:
                log.warning("slack reaction update failed: %s", e)
            merged_slack = si

        # v4 §6.y.1: post the 3-section review reply.
        if (pr is not None and not no_slack_reply
                and si.get("channel_id") and si.get("thread_ts")
                and not si.get("slack_reply_ts")):
            try:
                from slack_helpers import (  # noqa: WPS433 — lazy
                    SlackClient, render_review_reply, post_review_slack_reply,
                )
                client = SlackClient()
                text = render_review_reply(
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
                    summary_tldr=summary_tldr or _short_tldr(new_status, n_findings,
                                                             recommendation),
                    bullets=bullets or [],
                )
                reply_ts = post_review_slack_reply(
                    client,
                    channel_id=si["channel_id"],
                    thread_ts=si["thread_ts"],
                    text=text,
                    log=log,
                )
                if reply_ts:
                    if merged_slack is None:
                        merged_slack = si
                    merged_slack["slack_reply_ts"] = reply_ts
            except Exception as e:
                if log:
                    log.warning("slack review reply failed (non-fatal): %s", e)

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
        "approved_host": bool(approved_host),
        "recommendation": recommendation,
        "last_reviewed_at": now,
    }
    if head_sha:
        updates["head_sha"] = head_sha
        updates["last_reviewed_head_sha"] = head_sha
    if merged_slack is not None:
        updates["slack"] = merged_slack
    update_pr_entry(queue_path, pr_url, updates)
    return new_status
