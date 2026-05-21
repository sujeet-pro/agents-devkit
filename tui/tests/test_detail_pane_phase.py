"""Unit tests for the ε `Phase:` line in `tui/widgets/detail_pane.py`.

The DetailPane gets a new keyword-only argument `worker: WorkerRow | None`.
When provided, it renders a `Phase:` line between `Status:` and `Lock:`.
When omitted or None, the line is absent.
"""
from __future__ import annotations

from tui.model.queue_model import QueueRow
from tui.model.workers_model import WorkerRow
from tui.widgets.detail_pane import DetailPane


def _make_row() -> QueueRow:
    """Construct a minimally-populated QueueRow for DetailPane tests."""
    return QueueRow(
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
        pr_url="https://github.com/acme/foo/pull/42",
        task_type="review",
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:00:30Z",
        current_phase=phase,
        rc=None,
        age_s=30.0,
        is_stale=False,
    )


def _rendered_text(pane: DetailPane) -> str:
    """Pull the current rendered text from the Static widget."""
    return str(pane.render())


def test_show_none_returns_no_row_selected() -> None:
    pane = DetailPane()
    pane.show(None)
    assert _rendered_text(pane) == "(no row selected)"


def test_show_row_without_worker_kwarg_has_no_phase_line() -> None:
    """Default call (no `worker=` kwarg) must not render a Phase line."""
    pane = DetailPane()
    pane.show(_make_row())
    text = _rendered_text(pane)
    assert "Phase:" not in text, (
        f"Phase line should be absent when worker arg omitted.\nRendered:\n{text}"
    )


def test_show_row_with_worker_none_has_no_phase_line() -> None:
    """Explicit `worker=None` also suppresses the Phase line."""
    pane = DetailPane()
    pane.show(_make_row(), worker=None)
    text = _rendered_text(pane)
    assert "Phase:" not in text, (
        f"Phase line should be absent when worker=None.\nRendered:\n{text}"
    )


def test_show_row_with_worker_renders_phase_line() -> None:
    """`worker=<WorkerRow>` adds a `Phase:` line containing the phase text."""
    pane = DetailPane()
    pane.show(_make_row(), worker=_make_worker(phase="phase 4: Triage"))
    text = _rendered_text(pane)
    assert "Phase:" in text, f"Phase line missing.\nRendered:\n{text}"
    assert "phase 4: Triage" in text, (
        f"Phase text missing.\nRendered:\n{text}"
    )
    # Phase line is positioned between Status and Lock per SPEC §3.2.
    lines = text.splitlines()
    statuses = [i for i, ln in enumerate(lines) if ln.startswith("Status:")]
    phases = [i for i, ln in enumerate(lines) if ln.startswith("Phase:")]
    locks = [i for i, ln in enumerate(lines) if ln.startswith("Lock:")]
    assert statuses and phases and locks, (
        f"missing one of Status/Phase/Lock lines:\n{text}"
    )
    assert statuses[0] < phases[0] < locks[0], (
        f"Phase line out of order (Status={statuses[0]}, "
        f"Phase={phases[0]}, Lock={locks[0]}):\n{text}"
    )
