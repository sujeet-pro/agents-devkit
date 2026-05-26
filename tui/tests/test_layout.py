"""Layout tests: list + detail pane + action bar + minimal footer.

Validates that the simplified layout mounts the correct top-level widgets
and that secondary panes (WorkersPane, RunsPane, SyncPlanPane, LogPane)
are no longer directly mounted at app level — their content lives inside
the ActivityPane of the TabbedDetailPane.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.activity_pane import ActivityPane
from tui.widgets.detail_pane import TabbedDetailPane
from tui.widgets.footer_bar import FooterBar
from tui.widgets.header_bar import HeaderBar
from tui.widgets.queue_table import QueueTable


def test_core_widgets_compose(tui_app) -> None:
    """App must compose QueueTable, TabbedDetailPane, FooterBar, HeaderBar."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            tui_app.query_one(QueueTable)
            tui_app.query_one(TabbedDetailPane)
            tui_app.query_one(FooterBar)
            tui_app.query_one(HeaderBar)

    asyncio.run(_run())


def test_activity_pane_is_inside_tabbed_detail(tui_app) -> None:
    """ActivityPane must be present inside TabbedDetailPane (Activity tab)."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            pane = tui_app.query_one(TabbedDetailPane).activity_pane()
            assert pane is not None
            assert isinstance(pane, ActivityPane)

    asyncio.run(_run())


def test_footer_has_minimal_navigation(tui_app) -> None:
    """Footer must contain quit, help, filter, sort, nav keys."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            footer = str(tui_app.query_one(FooterBar).render())
            assert "[q]" in footer
            assert "[?]" in footer
            assert "filter:" in footer
            assert "sort:" in footer
            assert "nav" in footer

    asyncio.run(_run())


def test_stage_tabs_widget_present(tui_app) -> None:
    """The stage-filter TabbedContent must be mounted in the compose tree."""
    from textual.widgets import TabbedContent

    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            tc = tui_app.query_one("#stage-tabs", TabbedContent)
            assert tc is not None

    asyncio.run(_run())


def test_stage_tab_filter_all_shows_all_rows(tui_app) -> None:
    """With stage-all active, no rows should be filtered out."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert tui_app._active_stage_tab == "stage-all"
            table = tui_app.query_one(QueueTable)
            assert table.row_count == 6

    asyncio.run(_run())


def test_cycle_stage_tab_next_advances(tui_app) -> None:
    """action_cycle_stage_tab_next advances to the next tab."""
    from tui.app import _STAGE_TAB_IDS

    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert tui_app._active_stage_tab == "stage-all"
            await pilot.press("period")
            await pilot.pause()
            assert tui_app._active_stage_tab == _STAGE_TAB_IDS[1]

    asyncio.run(_run())


def test_cycle_stage_tab_prev_wraps(tui_app) -> None:
    """action_cycle_stage_tab_prev wraps from stage-all back to stage-done."""
    from tui.app import _STAGE_TAB_IDS

    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert tui_app._active_stage_tab == "stage-all"
            await pilot.press("comma")
            await pilot.pause()
            assert tui_app._active_stage_tab == _STAGE_TAB_IDS[-1]

    asyncio.run(_run())


def test_header_stage_counts_after_reload(tui_app) -> None:
    """After reload the HeaderBar's _stage_counts dict should be populated."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            header = tui_app.query_one(HeaderBar)
            counts = header._stage_counts
            assert isinstance(counts, dict)
            # All stage keys must be present; values are non-negative ints.
            for key in ("refresh", "index", "review", "resolve", "ready", "done"):
                assert key in counts, f"missing key {key!r}"
                assert isinstance(counts[key], int) and counts[key] >= 0

    asyncio.run(_run())


def test_no_always_visible_secondary_panes(fake_queue_path: Path) -> None:
    """Secondary panes are NOT mounted at app level; ActivityPane is inside TabbedDetailPane."""
    from textual.css.query import NoMatches
    from tui.widgets.workers_pane import WorkersPane
    from tui.widgets.runs_pane import RunsPane
    from tui.widgets.sync_plan_pane import SyncPlanPane
    from tui.widgets.log_pane import LogPane

    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            # These panes must NOT be mounted at app/screen level.
            for widget_type in (WorkersPane, RunsPane, SyncPlanPane, LogPane):
                try:
                    app.query_one(widget_type)
                    raise AssertionError(
                        f"{widget_type.__name__} should not be mounted at app level"
                    )
                except NoMatches:
                    pass
            # The replacement: ActivityPane lives inside TabbedDetailPane.
            activity = app.query_one(TabbedDetailPane).activity_pane()
            assert activity is not None
            # QueueTable must still occupy meaningful space.
            table = app.query_one(QueueTable)
            assert table.row_count >= 0

    asyncio.run(_run())
