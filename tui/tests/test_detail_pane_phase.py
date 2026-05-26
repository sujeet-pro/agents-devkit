"""Unit tests for the simplified detail pane."""
from __future__ import annotations

from tui.model.queue_model import QueueRow
from tui.model.work_queue_model import PrWorkState
from tui.model.workers_model import WorkerRow
from tui.model.work_queue_model import format_work_cell
from tui.widgets.detail_pane import (
    DetailPane,
    _format_relative_age,
    _stage_timeline_lines,
    _STAGE_LEGEND,
    _compute_overview_text,
)


def _make_row(
    *,
    last_synced_at: str | None = None,
    last_synced_head_sha: str | None = None,
    last_indexed_at: str | None = None,
    last_indexed_head_sha: str | None = None,
    last_validated_at: str | None = None,
    last_validated_head_sha: str | None = None,
    last_posted_at: str | None = None,
    last_posted_head_sha: str | None = None,
) -> QueueRow:
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
        last_synced_at=last_synced_at,
        last_synced_head_sha=last_synced_head_sha,
        last_indexed_at=last_indexed_at,
        last_indexed_head_sha=last_indexed_head_sha,
        last_validated_at=last_validated_at,
        last_validated_head_sha=last_validated_head_sha,
        last_posted_at=last_posted_at,
        last_posted_head_sha=last_posted_head_sha,
    )


def _make_worker(*, phase: str = "phase 4: Triage", task_type: str = "review",
                 is_stale: bool = False) -> WorkerRow:
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
        current_phase=phase,
        rc=None,
        log_path="/tmp/review.log",
        links={},
        artifacts={},
        age_s=30.0,
        is_stale=is_stale,
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


# ---------------------------------------------------------------------------
# Stage legend
# ---------------------------------------------------------------------------

def test_stage_legend_present_in_overview() -> None:
    """The one-line stage glyph legend must appear in every Overview."""
    pane = DetailPane()
    pane.show(_make_row())
    assert _STAGE_LEGEND in pane.overview_text


def test_stage_legend_content() -> None:
    """Legend must mention all five stage abbreviations."""
    for abbrev in ("S=Sync", "I=Index", "R=Review", "V=Validate", "P=Post"):
        assert abbrev in _STAGE_LEGEND, f"{abbrev!r} missing from legend"
    for glyph in ("pending", "done", "running", "failed"):
        assert glyph in _STAGE_LEGEND, f"{glyph!r} missing from legend"


def test_stage_legend_is_one_line() -> None:
    assert "\n" not in _STAGE_LEGEND
    assert len(_STAGE_LEGEND) <= 120


# ---------------------------------------------------------------------------
# Stage timeline renders 5 lines
# ---------------------------------------------------------------------------

def test_stage_timeline_has_five_stage_lines() -> None:
    """_stage_timeline_lines must return exactly 6 lines: header + 5 stages."""
    lines = _stage_timeline_lines(_make_row(), None)
    assert lines[0] == "Stages:"
    stage_lines = lines[1:]
    assert len(stage_lines) == 5
    for abbrev in ("[S]", "[I]", "[R]", "[V]", "[P]"):
        assert any(abbrev in l for l in stage_lines), f"{abbrev} missing from timeline"


def test_stage_timeline_all_pending_when_no_timestamps() -> None:
    """With no timestamps and no worker, all 5 stages must show · pending."""
    import dataclasses
    row = dataclasses.replace(_make_row(), last_reviewed_at=None)
    lines = _stage_timeline_lines(row, None)
    stage_lines = lines[1:]
    for line in stage_lines:
        assert "pending" in line, f"expected pending in: {line!r}"
        assert "·" in line


def test_stage_timeline_done_glyph_when_timestamp_set() -> None:
    """A stage with a timestamp must show ✓ done."""
    row = _make_row(last_synced_at="2026-05-22T10:00:00Z", last_synced_head_sha="abc12345")
    lines = _stage_timeline_lines(row, None)
    sync_line = next(l for l in lines if "[S]" in l)
    assert "✓" in sync_line
    assert "done" in sync_line
    assert "abc12345" in sync_line


def test_stage_timeline_running_glyph_for_active_worker() -> None:
    """The stage matching the active worker's task_type must show ⚡ running."""
    worker = _make_worker(task_type="review")
    lines = _stage_timeline_lines(_make_row(), worker)
    review_line = next(l for l in lines if "[R]" in l)
    assert "⚡" in review_line
    assert "running" in review_line


def test_stage_timeline_stale_worker_shows_pending() -> None:
    """A stale worker must not mark a stage as running."""
    import dataclasses
    row = dataclasses.replace(_make_row(), last_reviewed_at=None)
    worker = _make_worker(task_type="review", is_stale=True)
    lines = _stage_timeline_lines(row, worker)
    review_line = next(l for l in lines if "[R]" in l)
    assert "⚡" not in review_line
    assert "pending" in review_line


def test_stage_timeline_stale_head_sha_shows_stale_note() -> None:
    """When done_sha != current head, a stale note must appear in the stage line."""
    row = _make_row(
        last_synced_at="2026-05-22T10:00:00Z",
        last_synced_head_sha="oldsha00",
    )
    # Override head_sha to differ from last_synced_head_sha.
    import dataclasses
    row = dataclasses.replace(row, head_sha="newsha11")
    lines = _stage_timeline_lines(row, None)
    sync_line = next(l for l in lines if "[S]" in l)
    assert "stale" in sync_line
    assert "newsha11" in sync_line


def test_stage_timeline_index_maps_prepare_task_type() -> None:
    """task_type='prepare' must mark the Index stage as running."""
    worker = _make_worker(task_type="prepare")
    lines = _stage_timeline_lines(_make_row(), worker)
    index_line = next(l for l in lines if "[I]" in l)
    assert "⚡" in index_line


def test_stage_timeline_index_maps_embed_task_type() -> None:
    """task_type='embed' must mark the Index stage as running."""
    worker = _make_worker(task_type="embed")
    lines = _stage_timeline_lines(_make_row(), worker)
    index_line = next(l for l in lines if "[I]" in l)
    assert "⚡" in index_line


# ---------------------------------------------------------------------------
# Relative age formatting
# ---------------------------------------------------------------------------

def test_format_relative_age_none_returns_empty() -> None:
    assert _format_relative_age(None) == ""


def test_format_relative_age_invalid_returns_empty() -> None:
    assert _format_relative_age("not-a-date") == ""


def test_format_relative_age_minutes() -> None:
    from datetime import datetime, timedelta, timezone
    two_min_ago = (datetime.now(tz=timezone.utc) - timedelta(minutes=2)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    result = _format_relative_age(two_min_ago)
    assert "m ago" in result
    assert "2m" in result or "1m" in result  # allow 1-second drift


def test_format_relative_age_hours() -> None:
    from datetime import datetime, timedelta, timezone
    two_hr_ago = (datetime.now(tz=timezone.utc) - timedelta(hours=2, minutes=5)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    result = _format_relative_age(two_hr_ago)
    assert "h" in result
    assert "ago" in result


def test_format_relative_age_days() -> None:
    from datetime import datetime, timedelta, timezone
    three_days_ago = (datetime.now(tz=timezone.utc) - timedelta(days=3)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    result = _format_relative_age(three_days_ago)
    assert "3d ago" in result


# ---------------------------------------------------------------------------
# Overview ordering
# ---------------------------------------------------------------------------

def test_stage_legend_before_title_line_in_overview() -> None:
    """Stage legend must appear before the Title: line."""
    pane = DetailPane()
    pane.show(_make_row())
    text = pane.overview_text
    lines = text.splitlines()
    legend_idx = next((i for i, l in enumerate(lines) if "Stage glyphs" in l), None)
    title_idx = next((i for i, l in enumerate(lines) if l.startswith("Title:")), None)
    assert legend_idx is not None
    assert title_idx is not None
    assert legend_idx < title_idx


def test_stage_timeline_appears_in_overview() -> None:
    """The overview text must contain all five stage abbreviation markers."""
    pane = DetailPane()
    pane.show(_make_row())
    text = pane.overview_text
    for marker in ("[S]", "[I]", "[R]", "[V]", "[P]"):
        assert marker in text, f"{marker} missing from overview"
