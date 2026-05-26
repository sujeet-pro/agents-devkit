"""Unit tests for the simplified detail pane."""
from __future__ import annotations

from tui.model.queue_model import QueueRow
from tui.model.work_queue_model import PrWorkState
from tui.model.workers_model import WorkerRow
from tui.model.work_queue_model import format_work_cell
from tui.widgets.detail_pane import DetailPane


def _make_row() -> QueueRow:
    return QueueRow(
        queue_index=0,
        pr_url="https://github.com/acme/foo/pull/42",
        host="github",
        repo="acme/foo",
        number=42,
        title="feat: coupon engine",
        author="sujeet",
        target_branch="main",
        head_sha="a4f2c1ab9d8e7f6c",
        status="in_review",
        prep_status="ready",
        prep_error=None,
        taken_at="2026-05-22T14:32:15Z",
        last_checked_at=None,
        last_reviewed_at="2026-05-21T10:00:00Z",
        last_reviewed_head_sha=None,
        ready_for_review=True,
        slack_permalink="#eng-prs",
    )


def _make_worker(*, phase: str = "phase 4: Triage") -> WorkerRow:
    return WorkerRow(
        pid=1234,
        worker_id="w1234",
        run_id=None,
        pr_url="https://github.com/acme/foo/pull/42",
        subject="https://github.com/acme/foo/pull/42",
        task_type="review",
        status="running",
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:00:30Z",
        current_phase=phase,
        rc=None,
        log_path="/tmp/review.log",
        links={},
        artifacts={},
        age_s=30.0,
        is_stale=False,
    )


def test_show_none_returns_no_row_selected() -> None:
    pane = DetailPane()
    pane.show(None)
    assert pane.overview_text == "(no row selected)"


def test_show_row_without_worker_shows_last_review() -> None:
    pane = DetailPane()
    pane.show(_make_row())
    text = pane.overview_text
    assert "Last review:" in text
    assert "Lock:" not in text


def test_show_row_with_worker_renders_phase_and_log() -> None:
    pane = DetailPane()
    pane.show(_make_row(), worker=_make_worker(phase="phase 4: Triage"))
    text = pane.overview_text
    assert "Phase:" in text
    assert "phase 4: Triage" in text
    assert "Log:" in text
    assert "/tmp/review.log" in text


def test_work_state_line_rendered_when_provided() -> None:
    pane = DetailPane()
    work = format_work_cell(PrWorkState(status="running", action="sync+review"))
    pane.show(_make_row(), work_text=work)
    text = pane.overview_text
    assert "Work:" in text
    assert "running (sync+review)" in text


def test_context_actions_points_to_secondary_menu() -> None:
    pane = DetailPane()
    pane.show(_make_row())
    text = pane.overview_text
    assert "More:" in text
    assert "[enter] actions" in text
    assert "[r] review" not in text
