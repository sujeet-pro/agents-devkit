"""Tests for tui/widgets/workers_pane.py — θ.

Construct WorkerRow objects directly and assert on pane.render() text.
"""
from __future__ import annotations

from tui.model.workers_model import WorkerRow
from tui.widgets.workers_pane import WorkersPane


def _pane_text(pane: WorkersPane) -> str:
    """Static widgets stash their rendered text in .content."""
    return str(pane.content)


def _row(
    pid: int = 11111,
    pr_url: str = "https://github.com/acme/foo/pull/42",
    task_type: str = "review",
    agent: str = "claude",
    current_phase: str = "review",
    age_s: float = 12.0,
    is_stale: bool = False,
) -> WorkerRow:
    return WorkerRow(
        pid=pid,
        pr_url=pr_url,
        task_type=task_type,
        agent=agent,
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:00:00Z",
        current_phase=current_phase,
        rc=None,
        age_s=age_s,
        is_stale=is_stale,
    )


def test_pane_empty_state_when_no_rows() -> None:
    pane = WorkersPane()
    pane.update_workers([])
    text = _pane_text(pane)
    assert "no active workers" in text


def test_pane_renders_two_live_rows() -> None:
    rows = [
        _row(pid=11111, pr_url="https://github.com/acme/foo/pull/42", age_s=12.0),
        _row(
            pid=22222,
            pr_url="https://github.com/acme/bar/pull/7",
            age_s=65.0,
            current_phase="review",
        ),
    ]
    pane = WorkersPane()
    pane.update_workers(rows)
    text = _pane_text(pane)
    assert "Workers (2 active)" in text
    assert "acme/foo#42" in text
    assert "acme/bar#7" in text
    # task_type/current_phase composite appears
    assert "review/review" in text
    # agent appears
    assert "claude" in text
    # age formatted (12s + 1m for 65s)
    assert "12s" in text
    assert "1m" in text


def test_pane_ascii_mode_swaps_glyph() -> None:
    rows = [_row(age_s=5.0)]
    pane = WorkersPane()
    pane.update_workers(rows, ascii_only=True)
    text = _pane_text(pane)
    assert "~" in text
    # Unicode gear/refresh glyph should not appear in ASCII mode.
    assert "⚙" not in text


def test_pane_hides_stale_rows() -> None:
    rows = [
        _row(pid=1, age_s=600.0, is_stale=True),
        _row(pid=2, age_s=700.0, is_stale=True),
    ]
    pane = WorkersPane()
    pane.update_workers(rows)
    text = _pane_text(pane)
    # All rows stale → empty state.
    assert "no active workers" in text
    assert "acme/foo#42" not in text


def test_pane_mix_of_live_and_stale_only_shows_live() -> None:
    rows = [
        _row(pid=1, pr_url="https://github.com/acme/live/pull/1", age_s=5.0, is_stale=False),
        _row(pid=2, pr_url="https://github.com/acme/dead/pull/99", age_s=900.0, is_stale=True),
    ]
    pane = WorkersPane()
    pane.update_workers(rows)
    text = _pane_text(pane)
    assert "Workers (1 active)" in text
    assert "acme/live#1" in text
    assert "acme/dead#99" not in text


def test_pane_shortens_bitbucket_url() -> None:
    rows = [
        _row(
            pid=1,
            pr_url="https://bitbucket.org/myorg/myrepo/pull-requests/5",
            age_s=8.0,
        )
    ]
    pane = WorkersPane()
    pane.update_workers(rows)
    text = _pane_text(pane)
    assert "myorg/myrepo#5" in text
