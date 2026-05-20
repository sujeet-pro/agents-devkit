"""Tests for queue_release._compute_new_status (the mapping that decides
whether a finished review puts the queue row into approved / comments / reviewed).
"""
from __future__ import annotations

import pytest

from queue_release import _compute_new_status
from queue_io import STATUS_APPROVED, STATUS_COMMENTS, STATUS_REVIEWED


def test_findings_make_it_comments_even_when_host_approved():
    """A reviewer who left N>0 comments alongside an approval ends in COMMENTS.
    This is the "approved with open comments" bucket in the ready-to-merge tail.
    """
    assert _compute_new_status(n_findings=3, approved_host=True, recommendation="approve") == STATUS_COMMENTS


def test_zero_findings_plus_host_approved_is_approved():
    """The "approved with no open comments" bucket — safe to merge."""
    assert _compute_new_status(n_findings=0, approved_host=True, recommendation="approve") == STATUS_APPROVED


def test_recommendation_approve_alone_qualifies():
    """No host-side approval yet (CI hasn't seen the review post yet),
    but the review itself recommended approve → still approved."""
    assert _compute_new_status(n_findings=0, approved_host=False, recommendation="approve") == STATUS_APPROVED


def test_no_findings_and_no_approval_is_reviewed():
    """Reviewed but not yet approved (e.g. comment_only recommendation)."""
    assert _compute_new_status(n_findings=0, approved_host=False, recommendation="comment_only") == STATUS_REVIEWED


def test_findings_take_precedence_over_no_approval():
    """The presence of findings always pins the row into COMMENTS — the row needs
    attention from either the author or the reviewer."""
    assert _compute_new_status(n_findings=2, approved_host=False, recommendation="request_changes") == STATUS_COMMENTS


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
