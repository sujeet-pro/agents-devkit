from __future__ import annotations

import asyncio

from tui.widgets.footer_bar import FooterBar
from tui.widgets.queue_table import QueueTable


def _footer_text(app) -> str:
    return str(app.query_one(FooterBar).render())


def test_f_cycles_filter(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _footer_text(tui_app)
            assert "filter:all" in before
            await pilot.press("f")
            await pilot.pause()
            after = _footer_text(tui_app)
            assert "filter:open" in after
            assert before != after

    asyncio.run(_run())


def test_capital_s_cycles_sort(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _footer_text(tui_app)
            assert "sort:fifo" in before
            # Capital S — Textual maps shift+s to the literal `S` key.
            await pilot.press("S")
            await pilot.pause()
            after = _footer_text(tui_app)
            assert "sort:newest" in after
            assert before != after

    asyncio.run(_run())


def test_jk_moves_cursor(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            table = tui_app.query_one(QueueTable)
            before = table.cursor_row
            await pilot.press("j")
            await pilot.pause()
            after = table.cursor_row
            assert after == before + 1

    asyncio.run(_run())
