"""pr_reminders.py — Slack reminder ping for stalled PRs.

A row qualifies for a reminder when ALL of:
  - the row has Slack thread metadata (channel_id + thread_ts),
  - a review has completed (`last_reviewed_at` and `last_reviewed_head_sha` set),
  - the head_sha hasn't moved since that review (no new commits to re-review),
  - >= 24h has elapsed since the review,
  - we haven't reminded in the last 24h (no spam),
  - the row is NOT in a terminal state (merged/declined).

Sends one reply per qualifying row into the original Slack thread, then
stamps `last_reminded_at` on the row so the next pass doesn't re-fire.

Wired into `adk pr-sync` as a pipeline step and exposed standalone as
`adk pr-queue remind`.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import get_logger  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, TERMINAL_STATUSES,
    read_queue, update_pr_entry, _parse_iso, _now_iso, load_slack_config,
    slack_threads_for,
)


DEFAULT_THRESHOLD_HOURS = 24.0


def _threshold_hours_from_config(slack_cfg: dict) -> float:
    """Read pr_reviews.reminder.hours from a loaded slack config dict."""
    return float(
        slack_cfg.get("pr_reviews", {}).get("reminder", {}).get("hours", DEFAULT_THRESHOLD_HOURS)
    )


def _is_stale_review(entry: dict, *, now: datetime, threshold_hours: float) -> bool:
    """Pure-function predicate: should this row get a nudge?"""
    if (entry.get("status") or "") in TERMINAL_STATUSES:
        return False
    last_reviewed_at = _parse_iso(entry.get("last_reviewed_at"))
    if last_reviewed_at is None:
        return False
    head = entry.get("head_sha")
    last_reviewed_head = entry.get("last_reviewed_head_sha")
    if not head or not last_reviewed_head or head != last_reviewed_head:
        return False  # new commits since review → author already acted
    if (now - last_reviewed_at) < timedelta(hours=threshold_hours):
        return False
    last_reminded_at = _parse_iso(entry.get("last_reminded_at"))
    if last_reminded_at is not None:
        if (now - last_reminded_at) < timedelta(hours=threshold_hours):
            return False
    threads = slack_threads_for(entry)
    if not any(t.get("channel_id") and (t.get("thread_ts") or t.get("message_ts"))
               for t in threads):
        return False
    return True


def _reminder_text(entry: dict, *, now: datetime) -> str:
    """The actual message body. Reader-first: who, what's pending, since when."""
    pr_url = entry.get("pr_url", "the PR")
    last_reviewed_at = _parse_iso(entry.get("last_reviewed_at"))
    hours = "?"
    if last_reviewed_at is not None:
        hours = f"{(now - last_reviewed_at).total_seconds() / 3600:.0f}"
    return (f":alarm_clock: Friendly reminder: {pr_url} was reviewed {hours}h ago "
            "and has no new commits since. Please address comments or merge.")


def send_reminders(queue_path: Path, *, threshold_hours: float | None = None,
                   dry_run: bool = False, log=None,
                   now: datetime | None = None) -> dict:
    """Walk the queue and post a reminder reply for every row that qualifies.

    Returns {sent, skipped, failed} — counts + per-row details. Never raises
    for per-row errors; aggregates them into `failed` so the sync pipeline
    can keep moving.

    `threshold_hours` defaults to None; when None the value is read from
    slack.md (pr_reviews.reminder.hours), falling back to DEFAULT_THRESHOLD_HOURS.

    `now` defaults to the real wall clock; pass an explicit value from
    tests so the staleness predicate is deterministic.
    """
    if log is None:
        log = get_logger("pr-reminders")
    if now is None:
        now = datetime.now(tz=timezone.utc)
    if threshold_hours is None:
        try:
            slack_cfg = load_slack_config()
            threshold_hours = _threshold_hours_from_config(slack_cfg)
        except Exception:
            threshold_hours = DEFAULT_THRESHOLD_HOURS
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []

    qualifying = [e for e in prs
                  if _is_stale_review(e, now=now, threshold_hours=threshold_hours)]
    if not qualifying:
        return {"sent": [], "skipped": 0, "failed": [],
                "reason": "no qualifying rows"}

    if dry_run:
        return {"sent": [], "skipped": 0, "failed": [],
                "would_remind": [e.get("pr_url") for e in qualifying],
                "count": len(qualifying),
                "dry_run": True}

    # Lazy: only construct the Slack client if we have something to send.
    try:
        from slack_helpers import SlackClient  # type: ignore[import-not-found]
        load_slack_config()  # raises FileNotFoundError when config is missing
        client = SlackClient()
    except FileNotFoundError as e:
        return {"sent": [], "skipped": 0,
                "failed": [{"error": f"slack config missing: {e}"}],
                "count": len(qualifying)}
    except Exception as e:
        return {"sent": [], "skipped": 0,
                "failed": [{"error": f"slack client init failed: {e}"}],
                "count": len(qualifying)}

    sent: list[dict] = []
    failed: list[dict] = []
    for entry in qualifying:
        pr_url = entry.get("pr_url")
        threads = slack_threads_for(entry)
        text = _reminder_text(entry, now=now)
        thread_replies: list[dict] = []
        thread_failed = False
        if not threads:
            failed.append({"pr_url": pr_url, "error": "no slack threads"})
            continue
        for slack in threads:
            channel_id = slack.get("channel_id")
            thread_ts = slack.get("thread_ts") or slack.get("message_ts")
            if not channel_id or not thread_ts:
                continue
            try:
                reply_ts = client.post_thread_reply(channel_id, thread_ts, text)
            except Exception as e:
                failed.append({"pr_url": pr_url, "channel_id": channel_id,
                               "thread_ts": thread_ts, "error": str(e)})
                thread_failed = True
                continue
            if reply_ts is None:
                failed.append({"pr_url": pr_url, "channel_id": channel_id,
                               "thread_ts": thread_ts,
                               "error": "post_thread_reply returned None"})
                thread_failed = True
                continue
            thread_replies.append({"channel_id": channel_id, "thread_ts": thread_ts,
                                   "reply_ts": reply_ts})
        if thread_failed:
            continue
        update_pr_entry(queue_path, pr_url,
                        {"last_reminded_at": _now_iso(),
                         "last_checked_at": _now_iso()})
        sent.append({"pr_url": pr_url,
                     "reply_ts": thread_replies[0]["reply_ts"] if thread_replies else None,
                     "replies": thread_replies})

    return {"sent": sent, "failed": failed, "count": len(qualifying)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="adk pr-queue remind",
        description="Reply in the Slack thread for any PR reviewed >=24h ago "
                    "that has no new commits since. One reminder per 24h window.",
    )
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    ap.add_argument("--threshold-hours", type=float, default=None,
                    help="hours since review to qualify; defaults to "
                         "slack.md::pr_reviews.reminder.hours (24)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be reminded; don't post or stamp")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="non-interactive; equivalent to not asking for confirmation")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to $ADK_DATA_HOME/logs/")
    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-queue-remind", enabled=True, argv=argv)

    log = get_logger("pr-queue-remind")
    out = send_reminders(Path(args.queue).expanduser(),
                         threshold_hours=args.threshold_hours,
                         dry_run=args.dry_run, log=log)
    print(json.dumps(out, indent=2, default=str))
    return 1 if out.get("failed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
