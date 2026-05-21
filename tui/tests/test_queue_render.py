from __future__ import annotations

import asyncio

from tui.app import AdkApp
from tui.widgets.detail_pane import DetailPane
from tui.widgets.queue_table import QueueTable


def test_rows_visible(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            table = tui_app.query_one(QueueTable)
            assert table.row_count == 6

    asyncio.run(_run())


def test_empty_state_when_queue_missing(missing_queue_path):
    app = AdkApp(queue_path=missing_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            assert table.row_count == 1
            # Concatenate every cell render into a single string and substring-match.
            cells: list[str] = []
            for col_key in table.columns:
                for row_key in table.rows:
                    cells.append(str(table.get_cell(row_key, col_key)))
            blob = " ".join(cells)
            assert "no PRs" in blob

    asyncio.run(_run())


def test_detail_pane_updates_on_cursor_move(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            pane = tui_app.query_one(DetailPane)
            before = str(pane.render())
            await pilot.press("j")
            await pilot.pause()
            after = str(pane.render())
            assert before != after

    asyncio.run(_run())
