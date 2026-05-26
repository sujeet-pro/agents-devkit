"""Layout tests: list + detail pane + new action bars.

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
from tui.widgets.pr_action_bar import PRActionBar
from tui.widgets.pr_status_bar import PRStatusBar
from tui.widgets.queue_action_bar import QueueActionBar
from tui.widgets.queue_status_bar import QueueStatusBar
from tui.widgets.queue_table import QueueTable
from tui.widgets.splitter_handle import SplitterHandle


def test_core_widgets_compose(tui_app) -> None:
    """App must compose all expected widgets."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            tui_app.query_one(QueueTable)
            tui_app.query_one(TabbedDetailPane)
            tui_app.query_one(FooterBar)
            tui_app.query_one(HeaderBar)
            tui_app.query_one(QueueStatusBar)
            tui_app.query_one(QueueActionBar)
            tui_app.query_one(PRStatusBar)
            tui_app.query_one(PRActionBar)
            tui_app.query_one(SplitterHandle)

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


def test_footer_is_slim(tui_app) -> None:
    """Footer must only contain help and quit — no queue stats or actions."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            footer = str(tui_app.query_one(FooterBar).render())
            assert "[q]" in footer
            assert "[?]" in footer
            # Stats and filter/sort have moved to action bars.
            assert "filter:" not in footer
            assert "sort:" not in footer

    asyncio.run(_run())


def test_queue_action_bar_has_navigation(tui_app) -> None:
    """QueueActionBar must show filter, sort, nav keys."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            bar = str(tui_app.query_one(QueueActionBar).render())
            assert "filter:" in bar
            assert "sort:" in bar
            assert "nav" in bar

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


def test_stage_tab_click_updates_filter(tui_app) -> None:
    """Activating a stage tab through TabbedContent.active must apply the filter."""
    from textual.widgets import TabbedContent

    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert tui_app._active_stage_tab == "stage-all"
            tc = tui_app.query_one("#stage-tabs", TabbedContent)
            tc.active = "stage-ready"
            await pilot.pause()
            assert tui_app._active_stage_tab == "stage-ready"

    asyncio.run(_run())


def test_queue_status_bar_stage_counts_after_reload(tui_app) -> None:
    """After reload the QueueStatusBar must have been updated with stage counts."""
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            bar = tui_app.query_one(QueueStatusBar)
            assert bar._stage_counts is not None
            counts = bar._stage_counts
            assert isinstance(counts, dict)
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
            for widget_type in (WorkersPane, RunsPane, SyncPlanPane, LogPane):
                try:
                    app.query_one(widget_type)
                    raise AssertionError(
                        f"{widget_type.__name__} should not be mounted at app level"
                    )
                except NoMatches:
                    pass
            activity = app.query_one(TabbedDetailPane).activity_pane()
            assert activity is not None
            table = app.query_one(QueueTable)
            assert table.row_count >= 0

    asyncio.run(_run())
