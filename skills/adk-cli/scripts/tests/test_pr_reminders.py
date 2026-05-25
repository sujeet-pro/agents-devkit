"""Tests for `pr_reminders.send_reminders` — the Slack-thread nudge for PRs
that were reviewed >=24h ago and haven't moved since.

The qualifying predicate is pure (`_is_stale_review`); the side-effecting
send is mocked so tests don't touch real Slack.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import pr_reminders
from queue_io import STATUS_PENDING, STATUS_MERGED, STATUS_CLOSED


NOW = datetime(2026, 5, 21, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _row(**overrides) -> dict:
    base = {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": STATUS_PENDING,
        "head_sha": "abc",
        "last_reviewed_head_sha": "abc",
        "last_reviewed_at": _iso(NOW - timedelta(hours=26)),
        "slack": {"channel_id": "C123", "thread_ts": "1700000000.000123"},
    }
    base.update(overrides)
    return base


# ----- _is_stale_review --------------------------------------------------

def test_qualifying_row_is_stale():
    assert pr_reminders._is_stale_review(_row(), now=NOW, threshold_hours=24) is True


def test_not_yet_stale_within_threshold():
    row = _row(last_reviewed_at=_iso(NOW - timedelta(hours=12)))
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


def test_new_commits_disqualify():
    """Author pushed new commits since the review → no nudge (it's their
    turn anyway, and the review is stale for a different reason)."""
    row = _row(head_sha="newhead", last_reviewed_head_sha="oldhead")
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


def test_merged_or_closed_row_skipped():
    for status in (STATUS_MERGED, STATUS_CLOSED):
        row = _row(status=status)
        assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


def test_already_reminded_within_window_skipped():
    """Don't spam: if we sent a reminder <24h ago, hold off until the next window."""
    row = _row(last_reminded_at=_iso(NOW - timedelta(hours=6)))
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


def test_stale_reminder_can_re_fire():
    """If the last reminder was >24h ago and the PR still hasn't moved, fire again."""
    row = _row(last_reminded_at=_iso(NOW - timedelta(hours=48)))
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is True


def test_no_slack_info_skipped():
    """Without channel_id + thread_ts we have nowhere to post."""
    row = _row(slack={})
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False
    row = _row(slack={"channel_id": "C123"})  # missing thread_ts
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


def test_no_review_yet_skipped():
    row = _row(last_reviewed_at=None, last_reviewed_head_sha=None)
    assert pr_reminders._is_stale_review(row, now=NOW, threshold_hours=24) is False


# ----- send_reminders ----------------------------------------------------

def _write(tmp_path: Path, prs: list[dict]) -> Path:
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


def test_send_reminders_no_qualifying_rows(tmp_path):
    q = _write(tmp_path, [_row(last_reviewed_at=_iso(NOW - timedelta(hours=6)))])
    out = pr_reminders.send_reminders(q, threshold_hours=24, now=NOW)
    assert out["sent"] == []
    assert "no qualifying" in out["reason"]


def test_send_reminders_dry_run_reports_targets(tmp_path):
    q = _write(tmp_path, [_row(pr_url="u1"), _row(pr_url="u2")])
    out = pr_reminders.send_reminders(q, threshold_hours=24, dry_run=True, now=NOW)
    assert out["dry_run"] is True
    assert set(out["would_remind"]) == {"u1", "u2"}
    # Dry-run must not stamp last_reminded_at.
    persisted = json.loads(q.read_text())["prs"]
    assert all("last_reminded_at" not in r for r in persisted)


def test_send_reminders_posts_and_stamps(tmp_path, monkeypatch):
    """The end-to-end happy path: send + stamp `last_reminded_at`."""
    q = _write(tmp_path, [_row(pr_url="u1")])

    posted: list[tuple[str, str, str]] = []

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def post_thread_reply(self, channel_id, thread_ts, text):
            posted.append((channel_id, thread_ts, text))
            return "1700000999.000001"

    monkeypatch.setattr(pr_reminders, "load_slack_config", lambda: {})
    import slack_helpers
    monkeypatch.setattr(slack_helpers, "SlackClient", FakeClient)

    out = pr_reminders.send_reminders(q, threshold_hours=24, now=NOW)
    assert len(out["sent"]) == 1
    assert posted[0][0] == "C123"
    assert "1700000000.000123" == posted[0][1]
    assert "u1" in posted[0][2]  # the URL is in the reminder body

    persisted = json.loads(q.read_text())["prs"][0]
    assert persisted["last_reminded_at"]


def test_send_reminders_posts_to_every_slack_thread(tmp_path, monkeypatch):
    q = _write(tmp_path, [_row(
        pr_url="u1",
        slack={"channel_id": "C123", "thread_ts": "1700000000.000123"},
        slack_threads=[
            {"channel_id": "C123", "thread_ts": "1700000000.000123"},
            {"channel_id": "C456", "thread_ts": "1800000000.000456"},
        ],
    )])

    posted: list[tuple[str, str, str]] = []

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def post_thread_reply(self, channel_id, thread_ts, text):
            posted.append((channel_id, thread_ts, text))
            return f"{channel_id}-{thread_ts}-reply"

    monkeypatch.setattr(pr_reminders, "load_slack_config", lambda: {})
    import slack_helpers
    monkeypatch.setattr(slack_helpers, "SlackClient", FakeClient)

    out = pr_reminders.send_reminders(q, threshold_hours=24, now=NOW)

    assert len(out["sent"]) == 1
    assert [(c, t) for c, t, _ in posted] == [
        ("C123", "1700000000.000123"),
        ("C456", "1800000000.000456"),
    ]
    assert [r["reply_ts"] for r in out["sent"][0]["replies"]] == [
        "C123-1700000000.000123-reply",
        "C456-1800000000.000456-reply",
    ]


def test_send_reminders_collects_failures(tmp_path, monkeypatch):
    """One row fails to post → recorded in `failed`, others continue."""
    q = _write(tmp_path, [_row(pr_url="u1"), _row(pr_url="u2")])

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def post_thread_reply(self, channel_id, thread_ts, text):
            if "u1" in text:
                raise RuntimeError("network blip")
            return "ok-ts"

    monkeypatch.setattr(pr_reminders, "load_slack_config", lambda: {})
    import slack_helpers
    monkeypatch.setattr(slack_helpers, "SlackClient", FakeClient)

    out = pr_reminders.send_reminders(q, threshold_hours=24, now=NOW)
    assert len(out["sent"]) == 1
    assert len(out["failed"]) == 1
    assert out["failed"][0]["pr_url"] == "u1"


def test_send_reminders_handles_missing_slack_config(tmp_path, monkeypatch):
    """No slack config on disk → report cleanly without crashing the sync pipeline."""
    q = _write(tmp_path, [_row(pr_url="u1")])

    def _raise(*a, **kw):
        raise FileNotFoundError("slack config not present")

    monkeypatch.setattr(pr_reminders, "load_slack_config", _raise)
    out = pr_reminders.send_reminders(q, threshold_hours=24, now=NOW)
    assert out["sent"] == []
    assert out["failed"]
    assert "slack config" in out["failed"][0]["error"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
