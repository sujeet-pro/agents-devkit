"""Tests for pr_queue.print_summary — the ready-to-merge bucketing the user sees
at the tail of every review.
"""
from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from pr_queue import print_summary
from queue_io import STATUS_APPROVED, STATUS_COMMENTS, STATUS_REVIEWED, STATUS_MERGED


def _capture(prs: list[dict]) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_summary(prs)
    return buf.getvalue()


def test_three_buckets_with_approved_host_signal():
    """The new bucket logic uses approved_host to separate 'approved with
    open comments' from 'reviewed with open comments but no approval'.
    """
    prs = [
        {"pr_url": "u1", "status": STATUS_APPROVED},  # clean approval
        {"pr_url": "u2", "status": STATUS_COMMENTS, "approved_host": True,
         "approve_ready": True},
        {"pr_url": "u2b", "status": STATUS_COMMENTS, "approved_host": True},
        {"pr_url": "u3", "status": STATUS_COMMENTS, "approved_host": False},
        {"pr_url": "u4", "status": STATUS_COMMENTS},  # missing field == not approved
    ]
    out = _capture(prs)
    assert "Approved (no open comments)" in out
    assert "Approved (comments resolvable)" in out
    assert "Approved (open comments)" in out
    assert "Reviewed (open comments)" in out
    # u1: clean approval
    assert "u1" in out
    # u2: approved + has comments (legit "approved with comments")
    assert "u2" in out
    assert "u2b" in out
    # u3, u4: reviewed-with-comments — neither approved
    assert "u3" in out
    assert "u4" in out


def test_omits_non_approved_statuses():
    prs = [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": STATUS_REVIEWED},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": STATUS_MERGED},
        {"pr_url": "https://github.com/acme/foo/pull/3", "status": "pending"},
    ]
    out = _capture(prs)
    # No approved/comments rows → "Ready to merge: none."
    assert "none" in out.lower()
    for link in ("/pull/1", "/pull/2", "/pull/3"):
        assert link not in out


def test_counts_match_bucket_membership():
    """Counts in the three headers exactly match the bucket sizes."""
    prs = [
        {"pr_url": "u1", "status": STATUS_APPROVED},
        {"pr_url": "u2", "status": STATUS_APPROVED},
        {"pr_url": "u3", "status": STATUS_COMMENTS, "approved_host": True,
         "approve_ready": True},
        {"pr_url": "u4", "status": STATUS_COMMENTS, "approved_host": False},
    ]
    out = _capture(prs)
    # 2 approved-clean, 1 approved-resolvable, 1 reviewed-with-comments.
    assert "Approved (no open comments)   · 2" in out
    assert "Approved (comments resolvable) · 1" in out
    assert "Approved (open comments)      · 0" in out
    assert "Reviewed (open comments)      · 1" in out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
