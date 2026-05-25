"""Tests for queue_table _format_pr_status() using derive_task_status() (Item 2).

Validates:
- Column heading renamed to "task".
- _format_pr_status returns task_status, not raw queue status.
- Worker influences the displayed task_status.
- No-worker path returns status from queue fields.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tui.model.queue_model import QueueRow
from tui.model.workers_model import WorkerRow
from tui.widgets.queue_table import _format_pr_status, _COLUMNS


def _make_row(
    *,
    status: str = "pending",
    prep_status: str | None = "ready",
    ready_for_review: bool = True,
    head_sha: str | None = "abc001",
    last_reviewed_head_sha: str | None = None,
    taken_at: str | None = None,
) -> QueueRow:
    return QueueRow(
        queue_index=0,
        pr_url="https://github.com/acme/foo/pull/42",
        host="github",
        repo="acme/foo",
        number=42,
        title="test PR",
        author="alice",
        target_branch="main",
        head_sha=head_sha,
        status=status,
        prep_status=prep_status,
        prep_error=None,
        taken_at=taken_at,
        last_checked_at=None,
        last_reviewed_at=None,
        last_reviewed_head_sha=last_reviewed_head_sha,
        ready_for_review=ready_for_review,
        slack_permalink=None,
    )


def _make_worker(*, task_type: str = "review", is_stale: bool = False) -> WorkerRow:
    return WorkerRow(
        pid=1234,
        worker_id="w1234",
        run_id=None,
        pr_url="https://github.com/acme/foo/pull/42",
        subject="https://github.com/acme/foo/pull/42",
        task_type=task_type,
        status="running",
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:00:30Z",
        current_phase="phase 2",
        rc=None,
        log_path=None,
        links={},
        artifacts={},
        age_s=30.0,
        is_stale=is_stale,
    )


# ---------------------------------------------------------------------------
# Column header
# ---------------------------------------------------------------------------

def test_columns_has_task_not_pr_status() -> None:
    """The column heading must be 'task', not the old 'pr status'."""
    col_names = [name for name, _ in _COLUMNS]
    assert "task" in col_names, "Expected 'task' column"
    assert "pr status" not in col_names, "'pr status' column should be renamed"


# ---------------------------------------------------------------------------
# _format_pr_status — no worker
# ---------------------------------------------------------------------------

def test_format_ready_row_returns_ready() -> None:
    row = _make_row(prep_status="ready", ready_for_review=True)
    assert _format_pr_status(row) == "ready"


def test_format_merged_row_returns_merged() -> None:
    row = _make_row(status="merged", prep_status="ready", ready_for_review=False)
    assert _format_pr_status(row) == "merged"


def test_format_failed_prep_returns_failed() -> None:
    row = _make_row(prep_status="failed", ready_for_review=False)
    assert _format_pr_status(row) == "failed"


def test_format_preparing_returns_indexing() -> None:
    row = _make_row(prep_status="preparing", ready_for_review=False)
    assert _format_pr_status(row) == "indexing"


def test_format_head_moved_returns_needs_re_review() -> None:
    row = _make_row(
        prep_status="ready",
        ready_for_review=True,
        head_sha="new_sha",
        last_reviewed_head_sha="old_sha",
    )
    assert _format_pr_status(row) == "needs_re_review"


# ---------------------------------------------------------------------------
# _format_pr_status — with worker
# ---------------------------------------------------------------------------

def test_format_with_active_review_worker_returns_reviewing() -> None:
    row = _make_row(prep_status="ready", ready_for_review=True)
    worker = _make_worker(task_type="review")
    assert _format_pr_status(row, worker) == "reviewing"


def test_format_with_active_index_worker_returns_indexing() -> None:
    row = _make_row(prep_status="ready", ready_for_review=True)
    worker = _make_worker(task_type="prepare")
    assert _format_pr_status(row, worker) == "indexing"


def test_format_stale_worker_ignored() -> None:
    """A stale worker must not override the queue-derived status."""
    row = _make_row(prep_status="ready", ready_for_review=True)
    stale = _make_worker(task_type="review", is_stale=True)
    assert _format_pr_status(row, stale) == "ready"


def test_format_none_worker_same_as_no_worker() -> None:
    row = _make_row(prep_status="ready", ready_for_review=True)
    assert _format_pr_status(row, None) == _format_pr_status(row)
