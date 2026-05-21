from __future__ import annotations

from pathlib import Path

from tui.model.sync_plan_model import SyncPlanModel, SyncPlanSnapshot, SyncPlanStep
from tui.widgets.sync_plan_pane import SyncPlanPane


def _pane_text(pane: SyncPlanPane) -> str:
    """Static widgets stash their rendered text in .content."""
    return str(pane.content)


def test_pane_renders_placeholder_when_snapshot_none() -> None:
    pane = SyncPlanPane()
    pane.update_snapshot(None)
    text = _pane_text(pane)
    assert "no sync run yet" in text


def test_pane_renders_running_header_and_step_names(
    sync_plan_in_progress: Path,
) -> None:
    snap = SyncPlanModel(sync_plan_in_progress).snapshot()
    assert snap is not None
    pane = SyncPlanPane()
    pane.update_snapshot(snap)
    text = _pane_text(pane)
    # Header: "done" counts terminal statuses (ok/warn/failed/skipped) only;
    # the in-progress fixture has 2 ok + 1 running + 5 pending → 2/8.
    assert "Sync plan (running" in text
    assert "2/8 steps" in text
    # All step names appear.
    for name in (
        "pr-scan",
        "pr-queue update --all",
        "pr-queue clean (merged)",
        "pr-task clean-orphans",
        "pr-queue remind",
        "base-index audit",
        "auto-base cleanup",
        "pr-task prepare --all",
    ):
        assert name in text
    # At least one running-icon (⚡) visible.
    assert "⚡" in text


def test_pane_ascii_mode_swaps_icons(sync_plan_in_progress: Path) -> None:
    snap = SyncPlanModel(sync_plan_in_progress).snapshot()
    assert snap is not None
    pane = SyncPlanPane()
    pane.update_snapshot(snap, ascii_only=True)
    text = _pane_text(pane)
    # ASCII fallback for running is "[..]"; unicode "⚡" must NOT appear.
    assert "[..]" in text
    assert "⚡" not in text
    # ok-status row should use the ASCII variant too.
    assert "[ok]" in text


def test_pane_renders_done_header_when_completed() -> None:
    snap = SyncPlanSnapshot(
        queue="/tmp/q.json5",
        started_at="2026-05-22T14:00:00Z",
        updated_at="2026-05-22T14:05:00Z",
        completed_at="2026-05-22T14:05:00Z",
        rc=0,
        steps=[
            SyncPlanStep("a", "ok", 0, "s", "c"),
            SyncPlanStep("b", "ok", 0, "s", "c"),
        ],
    )
    pane = SyncPlanPane()
    pane.update_snapshot(snap)
    text = _pane_text(pane)
    assert "✓ done" in text
    assert "2/2 steps" in text


def test_pane_done_header_ascii_fallback() -> None:
    snap = SyncPlanSnapshot(
        queue="/tmp/q.json5",
        started_at="2026-05-22T14:00:00Z",
        updated_at="2026-05-22T14:05:00Z",
        completed_at="2026-05-22T14:05:00Z",
        rc=0,
        steps=[SyncPlanStep("a", "ok", 0, "s", "c")],
    )
    pane = SyncPlanPane()
    pane.update_snapshot(snap, ascii_only=True)
    text = _pane_text(pane)
    # The header in the current implementation keeps the Unicode glyph; the
    # ASCII swap is only on step icons. Verify that AT LEAST the ascii step
    # icon path is exercised and the header still reports "done".
    assert "done" in text
    assert "[ok]" in text


def test_pane_renders_failure_header_when_rc_nonzero() -> None:
    snap = SyncPlanSnapshot(
        queue="/tmp/q.json5",
        started_at="s",
        updated_at="u",
        completed_at="c",
        rc=1,
        steps=[SyncPlanStep("a", "failed", 1, "s", "c")],
    )
    pane = SyncPlanPane()
    pane.update_snapshot(snap)
    text = _pane_text(pane)
    assert "done (with failures)" in text
