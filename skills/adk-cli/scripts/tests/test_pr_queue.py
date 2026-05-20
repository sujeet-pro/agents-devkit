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


def test_separates_approved_with_and_without_comments():
    prs = [
        {"pr_link": "https://github.com/acme/foo/pull/1", "status": STATUS_APPROVED},
        {"pr_link": "https://github.com/acme/foo/pull/2", "status": STATUS_COMMENTS},
        {"pr_link": "https://github.com/acme/foo/pull/3", "status": STATUS_APPROVED},
    ]
    out = _capture(prs)
    assert "Approved (no open comments)" in out
    assert "Approved (open comments)" in out
    # Both approved PRs must show; the approved-with-comments one must show too.
    assert "https://github.com/acme/foo/pull/1" in out
    assert "https://github.com/acme/foo/pull/3" in out
    assert "https://github.com/acme/foo/pull/2" in out


def test_omits_non_approved_statuses():
    prs = [
        {"pr_link": "https://github.com/acme/foo/pull/1", "status": STATUS_REVIEWED},
        {"pr_link": "https://github.com/acme/foo/pull/2", "status": STATUS_MERGED},
        {"pr_link": "https://github.com/acme/foo/pull/3", "status": "pending"},
    ]
    out = _capture(prs)
    # No approved rows → "Ready to merge: none."
    assert "none" in out.lower()
    for link in ("/pull/1", "/pull/2", "/pull/3"):
        assert link not in out


def test_counts_are_accurate():
    prs = [
        {"pr_link": "u1", "status": STATUS_APPROVED},
        {"pr_link": "u2", "status": STATUS_APPROVED},
        {"pr_link": "u3", "status": STATUS_COMMENTS},
    ]
    out = _capture(prs)
    assert "· 2" in out  # two approved-no-comments
    assert "· 1" in out  # one approved-with-comments


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
