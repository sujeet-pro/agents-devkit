"""Tests for `release_after_review` writing `last_reviewed_head_oid` +
`last_reviewed_at` so the queue filter knows the PR was reviewed at this
exact commit and shouldn't re-pick it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from queue_release import release_after_review
from queue_io import STATUS_APPROVED


def _write(tmp_path: Path, prs: list[dict]) -> Path:
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


def test_release_writes_last_reviewed_head_oid(tmp_path):
    p = _write(tmp_path, [{
        "pr_link": "https://github.com/acme/foo/pull/1",
        "status": "pending",
        "head_oid": "old",
        "taken_at": "2026-05-21T00:00:00Z",
    }])
    new_status = release_after_review(
        queue_path=p,
        pr_link="https://github.com/acme/foo/pull/1",
        head_oid="new-head-abc",
        n_findings=0,
        approved_host=True,
        recommendation="approve",
    )
    assert new_status == STATUS_APPROVED
    row = json.loads(p.read_text())["prs"][0]
    assert row["last_reviewed_head_oid"] == "new-head-abc"
    assert row["head_oid"] == "new-head-abc"
    assert row["last_reviewed_at"], "last_reviewed_at should be set"
    assert row["taken_at"] is None       # lock released
    assert row["status"] == STATUS_APPROVED


def test_release_without_head_oid_still_sets_timestamp(tmp_path):
    """If the orchestrator somehow lost head_oid, we still record the
    review timestamp so the queue knows a pass happened."""
    p = _write(tmp_path, [{
        "pr_link": "u1",
        "status": "pending",
        "taken_at": "2026-05-21T00:00:00Z",
    }])
    release_after_review(
        queue_path=p, pr_link="u1", head_oid=None,
        n_findings=2, approved_host=False, recommendation="comment",
    )
    row = json.loads(p.read_text())["prs"][0]
    assert "last_reviewed_at" in row
    # head_oid wasn't supplied, so we can't link the timestamp to a commit —
    # the row remains eligible for re-acquisition.
    assert "last_reviewed_head_oid" not in row


def test_full_cycle_review_then_no_repick(tmp_path):
    """The shipping use case: review completes → release writes
    last_reviewed_head_oid → next acquire_next_row skips the row."""
    from queue_io import acquire_next_row

    p = _write(tmp_path, [{
        "pr_link": "u1",
        "status": "pending",
        "head_oid": "commit-abc",
        "taken_at": "2026-05-21T00:00:00Z",   # claimed by the active reviewer
    }])
    release_after_review(
        queue_path=p, pr_link="u1", head_oid="commit-abc",
        n_findings=0, approved_host=True, recommendation="approve",
    )
    # Now nothing claimable in the queue — the row was reviewed at this head.
    assert acquire_next_row(p) is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
