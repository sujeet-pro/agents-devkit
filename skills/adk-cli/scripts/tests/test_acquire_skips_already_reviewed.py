"""Tests for the queue acquisition filter: `/adk-pr-review` (no arg) should
skip rows whose head_oid matches `last_reviewed_head_oid` so the same commit
isn't reviewed twice in a row. New commits push the row back into eligibility.

Explicit URL invocations bypass this filter — they go through `find_row`,
not `acquire_next_row`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from queue_io import (
    STATUS_PENDING, STATUS_MERGED,
    _is_already_reviewed_at_head, acquire_next_row,
)


def test_is_already_reviewed_at_head_true_when_matches():
    assert _is_already_reviewed_at_head({
        "head_oid": "abc123",
        "last_reviewed_head_oid": "abc123",
    }) is True


def test_is_already_reviewed_at_head_false_when_new_commits():
    assert _is_already_reviewed_at_head({
        "head_oid": "newhead",
        "last_reviewed_head_oid": "oldhead",
    }) is False


def test_is_already_reviewed_at_head_false_when_never_reviewed():
    """A row scanned but never reviewed has no last_reviewed_head_oid."""
    assert _is_already_reviewed_at_head({"head_oid": "abc123"}) is False
    assert _is_already_reviewed_at_head({
        "head_oid": "abc123",
        "last_reviewed_head_oid": None,
    }) is False


def test_is_already_reviewed_at_head_false_when_no_head_oid():
    """Defensive: missing head_oid → never skip."""
    assert _is_already_reviewed_at_head({"last_reviewed_head_oid": "xx"}) is False


def _write(tmp_path: Path, prs: list[dict]) -> Path:
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


def test_acquire_skips_already_reviewed(tmp_path):
    """Three rows: one new-commits, one already-reviewed-at-head, one
    never-reviewed. Acquire should hand back the already-reviewed row's
    NEIGHBORS, not the row itself."""
    p = _write(tmp_path, [
        {
            "pr_link": "https://github.com/acme/foo/pull/1",
            "status": STATUS_PENDING,
            "head_oid": "abc",
            "last_reviewed_head_oid": "abc",   # skip — no new commits
        },
        {
            "pr_link": "https://github.com/acme/foo/pull/2",
            "status": STATUS_PENDING,
            "head_oid": "newhead",
            "last_reviewed_head_oid": "oldhead",  # new commits since last review
        },
        {
            "pr_link": "https://github.com/acme/foo/pull/3",
            "status": STATUS_PENDING,
            "head_oid": "fresh",
            # never reviewed
        },
    ])
    picked = acquire_next_row(p)
    assert picked is not None
    assert picked["pr_link"] in {
        "https://github.com/acme/foo/pull/2",
        "https://github.com/acme/foo/pull/3",
    }


def test_acquire_returns_none_when_only_already_reviewed_left(tmp_path):
    """If every row is either merged or already-reviewed-at-head, queue
    returns None and the caller prints `queue_empty`."""
    p = _write(tmp_path, [
        {
            "pr_link": "u1", "status": STATUS_PENDING,
            "head_oid": "x", "last_reviewed_head_oid": "x",
        },
        {
            "pr_link": "u2", "status": STATUS_MERGED,
            "head_oid": "y", "last_reviewed_head_oid": "y",
        },
    ])
    assert acquire_next_row(p) is None


def test_new_commit_after_review_makes_row_eligible_again(tmp_path):
    """Simulate the flow: row reviewed at head=A → row gets new commits at
    head=B → next acquire claims it."""
    p = _write(tmp_path, [
        {
            "pr_link": "u1",
            "status": STATUS_PENDING,
            "head_oid": "B",        # author pushed new commits
            "last_reviewed_head_oid": "A",
        },
    ])
    picked = acquire_next_row(p)
    assert picked is not None
    assert picked["pr_link"] == "u1"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
