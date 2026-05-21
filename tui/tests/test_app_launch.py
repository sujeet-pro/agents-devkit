from __future__ import annotations

import asyncio

from tui.widgets.header_bar import HeaderBar
from tui.widgets.help_screen import HelpScreen


def test_app_starts_and_quits(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")
            await pilot.pause()
        # If the context exited cleanly, the app finished without raising.
        assert tui_app.return_value is None

    asyncio.run(_run())


def test_app_renders_header(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            header = tui_app.query_one(HeaderBar)
            text = str(header.render())
            assert "queue:" in text

    asyncio.run(_run())


def test_help_screen_opens_and_closes(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert len(tui_app.screen_stack) == 1
            await pilot.press("question_mark")
            await pilot.pause()
            assert len(tui_app.screen_stack) == 2
            assert isinstance(tui_app.screen_stack[-1], HelpScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert len(tui_app.screen_stack) == 1

    asyncio.run(_run())
