"""Unit tests for WorkQueueModel."""
from __future__ import annotations

from tui.model.work_queue_model import WorkQueueModel, format_work_cell, PrWorkState


def test_format_work_cell_truncates_long_messages() -> None:
    state = PrWorkState(
        status="failed",
        action="sync",
        message="x" * 80,
    )
    cell = format_work_cell(state)
    assert len(cell) <= 26


def test_work_queue_tracks_per_pr_state() -> None:
    wq = WorkQueueModel()
    url = "https://github.com/acme/foo/pull/1"
    wq.set(url, "queued", "sync+review")
    wq.set(url, "running", "sync+review")
    state = wq.get(url)
    assert state is not None
    assert state.status == "running"
    assert wq.format_cell(url) == "running (sync+review)"
