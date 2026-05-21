"""queue_release.py — post-review queue + Slack update.

Called by /adk-pr-review's report.py at the tail of a review. Given the review
outcome (n_findings, host approval state, recommendation), it:

  1. Computes the new queue status using the same mapping the legacy batch
     driver used:
        n_findings > 0                   → STATUS_COMMENTS
        elif approved (host OR rec)      → STATUS_APPROVED
        else                             → STATUS_REVIEWED
  2. Clears `taken_at` and writes status, head_oid, last_checked_at.
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
    pr_link: str,
    head_oid: str | None,
    n_findings: int,
    approved_host: bool,
    recommendation: str | None,
    slack_cfg: dict | None = None,
    slack_info: dict | None = None,
    log=None,
) -> str | None:
    """Update the queue + slack reaction after a review completes. Returns
    the new status, or None if the PR wasn't in the queue.
    """
    entry = find_row(queue_path, pr_link)
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

    # Persist approved_host + recommendation alongside status so the
    # ready-to-merge summary can distinguish "approved with open comments"
    # from "reviewed (commented but not approved)". Without these the bucket
    # collapses and we mislabel `status=comments` rows as "approved".
    #
    # `last_reviewed_head_oid` + `last_reviewed_at` let `acquire_next_row`
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
    if head_oid:
        updates["head_oid"] = head_oid
        updates["last_reviewed_head_oid"] = head_oid
    if merged_slack is not None:
        updates["slack"] = merged_slack
    update_pr_entry(queue_path, pr_link, updates)
    return new_status
