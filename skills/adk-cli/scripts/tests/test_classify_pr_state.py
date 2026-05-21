"""Tests for `classify_pr_state` — the central origin-API state interpreter
that turns host-specific meta into one of {open, merged, declined, unknown}.

Why this matters: the queue picker, sync cleanup, and reminder logic all
depend on a consistent verdict. A GitHub `CLOSED + not merged` PR and a
Bitbucket `DECLINED` PR are semantically the same; without this classifier
the queue would treat them differently.
"""
from __future__ import annotations

import pytest

from queue_io import classify_pr_state


def test_merged_at_set_wins():
    assert classify_pr_state({"merged_at": "2026-05-21T10:00:00Z", "state": "MERGED"}) == "merged"
    # merged_at trumps a stale state field
    assert classify_pr_state({"merged_at": "2026-05-21T10:00:00Z", "state": "OPEN"}) == "merged"


def test_github_state_merged_without_merged_at():
    """GitHub's `state==MERGED` should also be honoured even if merged_at
    didn't come through (belt + suspenders)."""
    assert classify_pr_state({"merged_at": None, "state": "MERGED"}) == "merged"


def test_github_closed_without_merge_is_declined():
    assert classify_pr_state({"merged_at": None, "state": "CLOSED"}) == "declined"


def test_bitbucket_declined_is_declined():
    assert classify_pr_state({"merged_at": None, "state": "DECLINED"}) == "declined"


def test_bitbucket_superseded_is_declined():
    """SUPERSEDED PRs have been replaced by a newer PR — same outcome for us:
    don't keep reviewing them."""
    assert classify_pr_state({"merged_at": None, "state": "SUPERSEDED"}) == "declined"


def test_open_state():
    assert classify_pr_state({"merged_at": None, "state": "OPEN"}) == "open"


def test_lowercase_state_handled():
    """Defensive: hosts shouldn't return lowercase but the function shouldn't
    misclassify if they do."""
    assert classify_pr_state({"merged_at": None, "state": "open"}) == "open"
    assert classify_pr_state({"merged_at": None, "state": "declined"}) == "declined"


def test_meta_error_is_unknown():
    """A fetch error → don't guess; the caller can fall back to cached state."""
    assert classify_pr_state({"error": "rate limited"}) == "unknown"


def test_empty_meta_is_unknown():
    assert classify_pr_state({}) == "unknown"
    assert classify_pr_state(None) == "unknown"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
