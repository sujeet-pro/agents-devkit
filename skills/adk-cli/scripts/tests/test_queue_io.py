"""Tests for queue_io.acquire_next_row / release_row + the 30-min auto-expire."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import queue_io


def _write_queue(path: Path, prs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"filters": None, "prs": prs}, indent=2), encoding="utf-8")


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_acquire_next_row_picks_oldest_first(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    old_ts = _iso(datetime.now(tz=timezone.utc) - timedelta(hours=5))
    newer_ts = _iso(datetime.now(tz=timezone.utc) - timedelta(hours=1))
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "pending",
         "last_checked_at": newer_ts, "taken_at": None},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": old_ts, "taken_at": None},
    ])

    row = queue_io.acquire_next_row(qp)
    assert row is not None
    assert row["pr_url"].endswith("/pull/2"), "oldest last_checked_at should win"
    # The persisted row should have taken_at set.
    persisted = json.loads(qp.read_text())["prs"]
    pr2 = next(e for e in persisted if e["pr_url"].endswith("/pull/2"))
    assert pr2["taken_at"] is not None


def test_acquire_next_row_prefers_never_reviewed(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    old_ts = _iso(datetime.now(tz=timezone.utc) - timedelta(days=30))
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "pending",
         "last_checked_at": old_ts, "taken_at": None},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": None, "taken_at": None},
    ])

    row = queue_io.acquire_next_row(qp)
    assert row is not None
    assert row["pr_url"].endswith("/pull/2"), "null last_checked_at sorts before any timestamp"


def test_acquire_next_row_skips_locked_rows(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    recent_lock = _iso(datetime.now(tz=timezone.utc) - timedelta(minutes=5))  # < 30 min
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "pending",
         "last_checked_at": None, "taken_at": recent_lock},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": None, "taken_at": None},
    ])

    row = queue_io.acquire_next_row(qp)
    assert row is not None
    assert row["pr_url"].endswith("/pull/2"), "the locked row #1 must be skipped"


def test_acquire_next_row_treats_expired_lock_as_free(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    # v4 §6.v raised TAKEN_LOCK_MAX_AGE_SECONDS from 30 min to 2 h to cover
    # long-running reviews; the test now uses a 3-hour-old lock.
    expired = _iso(datetime.now(tz=timezone.utc) - timedelta(hours=3))  # > 2 h
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "pending",
         "last_checked_at": None, "taken_at": expired},
    ])

    row = queue_io.acquire_next_row(qp)
    assert row is not None
    assert row["pr_url"].endswith("/pull/1"), "expired taken_at must auto-release"
    # New taken_at should differ from the expired one.
    persisted = json.loads(qp.read_text())["prs"][0]
    assert persisted["taken_at"] != expired


def test_acquire_next_row_skips_merged(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "merged",
         "last_checked_at": None, "taken_at": None},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": None, "taken_at": None},
    ])

    row = queue_io.acquire_next_row(qp)
    assert row is not None
    assert row["pr_url"].endswith("/pull/2")


def test_acquire_next_row_returns_none_when_nothing_eligible(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    recent_lock = _iso(datetime.now(tz=timezone.utc) - timedelta(minutes=5))
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "merged",
         "last_checked_at": None, "taken_at": None},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": None, "taken_at": recent_lock},
    ])

    assert queue_io.acquire_next_row(qp) is None


def test_release_row_clears_taken_at_and_updates_status(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "in_review",
         "last_checked_at": None, "taken_at": _iso(datetime.now(tz=timezone.utc))},
    ])

    ok = queue_io.release_row(qp, "https://github.com/acme/foo/pull/1",
                              status="approved", head_sha="deadbeef",
                              last_checked_at=_iso(datetime.now(tz=timezone.utc)))
    assert ok
    persisted = json.loads(qp.read_text())["prs"][0]
    assert persisted["taken_at"] is None
    assert persisted["status"] == "approved"
    assert persisted["head_sha"] == "deadbeef"


def test_release_after_review_persists_approved_host_and_recommendation(tmp_path):
    """The ready-to-merge bucket logic depends on approved_host being persisted
    on the row. release_after_review must write it.
    """
    import sys
    sys.path.insert(0, "skills/adk-cli/scripts")
    from queue_release import release_after_review

    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/7",
         "status": "in_review",
         "last_checked_at": None,
         "taken_at": _iso(datetime.now(tz=timezone.utc))},
    ])
    status = release_after_review(
        queue_path=qp,
        pr_url="https://github.com/acme/foo/pull/7",
        head_sha="cafebabe",
        n_findings=2, approved_host=True, recommendation="approve",
        slack_cfg=None, slack_info=None,
    )
    assert status == "comments"  # n_findings>0 → comments regardless of approval
    row = json.loads(qp.read_text())["prs"][0]
    assert row["approved_host"] is True
    assert row["recommendation"] == "approve"
    assert row["taken_at"] is None


def test_release_row_cannot_downgrade_merged(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "merged",
         "last_checked_at": None, "taken_at": _iso(datetime.now(tz=timezone.utc))},
    ])

    ok = queue_io.release_row(qp, "https://github.com/acme/foo/pull/1",
                              status="approved")
    assert ok
    persisted = json.loads(qp.read_text())["prs"][0]
    # taken_at still gets cleared (it's not the status field) but status stays merged.
    assert persisted["taken_at"] is None
    assert persisted["status"] == "merged"


def test_two_consecutive_acquires_get_different_rows(tmp_path):
    """Simulates two terminals back-to-back: each gets a distinct PR."""
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": "pending",
         "last_checked_at": None, "taken_at": None},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": "pending",
         "last_checked_at": None, "taken_at": None},
    ])

    a = queue_io.acquire_next_row(qp)
    b = queue_io.acquire_next_row(qp)
    assert a is not None and b is not None
    assert a["pr_url"] != b["pr_url"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
