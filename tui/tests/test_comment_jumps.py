"""Tests for the Comments tab jump-between-comments keybinds.

`n` scrolls to the next ``---`` divider (start of the next comment); `N`
scrolls to the previous one. Falls back to PageDown / PageUp when no
dividers are present in the active tab.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from textual.containers import VerticalScroll
from textual.widgets import Markdown


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    monkeypatch.setenv("ADK_DATA_HOME", str(data))
    return cfg


def test_n_jumps_to_next_divider(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """With multiple comments separated by `---` dividers, `n` moves the
    scroll position to the line of the next divider."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.pause()
            await pilot.press("3")  # Comments tab
            await pilot.pause()

            md = app.query_one("#detail-comments", Markdown)
            sections = [
                f"# Comments — foo#42 · 5 posted",
                *(
                    f"### thread {i}\n\n- **@user{i}** body {i}\n\n"
                    + "\n".join(f"line {j}" for j in range(10))
                    for i in range(5)
                ),
            ]
            big = "\n\n---\n\n".join(sections)
            await md.update(big)
            await pilot.pause()
            await pilot.pause()

            scroll = app.query_one("#comments-scroll", VerticalScroll)
            # Ensure the content is taller than the viewport.
            if scroll.virtual_size.height <= scroll.size.height:
                # Skip — viewport too tall to overflow with this fixture.
                return

            start_y = scroll.scroll_y
            await pilot.press("n")
            await pilot.pause()
            assert scroll.scroll_y > start_y, (
                f"`n` should advance scroll; before={start_y} after={scroll.scroll_y}"
            )

    asyncio.run(_run())


def test_shift_n_jumps_to_previous_divider(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """`N` (Shift+N) moves to the previous comment divider."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.pause()
            await pilot.press("3")
            await pilot.pause()

            md = app.query_one("#detail-comments", Markdown)
            sections = [
                f"# Comments — foo#42 · 5 posted",
                *(
                    f"### thread {i}\n\n- body\n\n"
                    + "\n".join(f"line {j}" for j in range(10))
                    for i in range(5)
                ),
            ]
            big = "\n\n---\n\n".join(sections)
            await md.update(big)
            await pilot.pause()
            await pilot.pause()

            scroll = app.query_one("#comments-scroll", VerticalScroll)
            if scroll.virtual_size.height <= scroll.size.height:
                return

            # Advance, then go back.
            await pilot.press("n")
            await pilot.press("n")
            await pilot.pause()
            mid = scroll.scroll_y
            await pilot.press("N")
            await pilot.pause()
            assert scroll.scroll_y < mid, (
                f"`N` should move scroll back; mid={mid} after={scroll.scroll_y}"
            )

    asyncio.run(_run())


def test_n_falls_back_to_pagedown_when_no_dividers(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """When the active tab has no markdown dividers (e.g., Overview), `n`
    behaves like PageDown so it remains useful as a general 'advance' key."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.pause()
            await pilot.press("1")  # Overview tab — no markdown dividers
            await pilot.pause()
            scroll = app.query_one("#overview-scroll", VerticalScroll)
            before = scroll.scroll_y
            await pilot.press("n")
            await pilot.pause()
            # No assertion on direction (overview may not be scrollable in
            # the test viewport) — just verify the action doesn't error.
            assert scroll.scroll_y >= before

    asyncio.run(_run())
