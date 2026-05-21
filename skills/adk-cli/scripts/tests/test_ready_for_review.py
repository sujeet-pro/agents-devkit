"""v4 §6.u eligibility predicate — single source of truth for which PR is
ready to review. P5 ships this; the picker + claim verbs consult it.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

from queue_io import (
    ready_for_review, PREP_READY, PREP_PREPARING, PREP_FAILED, PREP_PENDING,
    STATUS_PENDING, STATUS_REVIEWED, STATUS_MERGED, STATUS_CLOSED,
)


def _now():
    return datetime.now(tz=timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_minimal_pending_row_is_ready():
    """Back-compat: a row without prep_status fields is treated as ready."""
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc"}
    assert ready_for_review(e) is True


def test_merged_row_is_not_ready():
    e = {"pr_url": "x", "status": STATUS_MERGED, "head_sha": "abc",
         "prep_status": PREP_READY, "prep_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_closed_row_is_not_ready():
    e = {"pr_url": "x", "status": STATUS_CLOSED, "head_sha": "abc",
         "prep_status": PREP_READY, "prep_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_locked_row_is_not_ready():
    """Fresh taken_at (within 2-hour ceiling) blocks the row."""
    fresh = _iso(_now() - timedelta(minutes=30))
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc",
         "taken_at": fresh, "prep_status": PREP_READY, "prep_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_expired_lock_does_not_block():
    """Lock older than 2 hours is treated as released."""
    stale = _iso(_now() - timedelta(hours=3))
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc",
         "taken_at": stale, "prep_status": PREP_READY, "prep_head_sha": "abc"}
    assert ready_for_review(e) is True


def test_preparing_prep_status_is_not_ready():
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc",
         "prep_status": PREP_PREPARING, "prep_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_failed_prep_status_is_not_ready():
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc",
         "prep_status": PREP_FAILED, "prep_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_stale_prep_head_sha_is_not_ready():
    """prep is for an OLD commit; new commits arrived → not ready."""
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "new",
         "prep_status": PREP_READY, "prep_head_sha": "old"}
    assert ready_for_review(e) is False


def test_already_reviewed_at_head_is_not_ready():
    """head_sha == last_reviewed_head_sha → already reviewed."""
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "abc",
         "prep_status": PREP_READY, "prep_head_sha": "abc",
         "last_reviewed_head_sha": "abc"}
    assert ready_for_review(e) is False


def test_new_commits_after_review_make_row_ready_again():
    e = {"pr_url": "x", "status": STATUS_PENDING, "head_sha": "new",
         "prep_status": PREP_READY, "prep_head_sha": "new",
         "last_reviewed_head_sha": "old"}
    assert ready_for_review(e) is True


def test_reviewed_status_with_new_commits_is_ready():
    """STATUS_REVIEWED is NOT terminal — a new commit pushes it back into the queue."""
    e = {"pr_url": "x", "status": STATUS_REVIEWED, "head_sha": "new",
         "prep_status": PREP_READY, "prep_head_sha": "new",
         "last_reviewed_head_sha": "old"}
    assert ready_for_review(e) is True
