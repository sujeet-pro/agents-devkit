"""Pilot tests for tui/screens/prompt_screen.py — η.

PromptScreen is a generic single-input modal. dismiss() with the typed
value on submit; dismiss(None) on cancel (escape). Empty submit yields ""
which callers treat as cancel.
"""
from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.screens.prompt_screen import PromptScreen


class _Harness(App):
    """Minimal App that pushes a PromptScreen and captures its dismiss value.

    Uses push_screen(...,  callback=...) instead of push_screen_wait so we
    don't need an active worker context (push_screen_wait requires one).
    """

    def __init__(self, label: str = "test", placeholder: str = "") -> None:
        super().__init__()
        self._label = label
        self._placeholder = placeholder
        self.captured: str | None = "<unset>"  # sentinel — distinguishes None from never-set
        self._fired = False

    def compose(self) -> ComposeResult:
        yield Static("host")

    def _on_dismiss(self, value: str | None) -> None:
        self.captured = value
        self._fired = True

    def on_mount(self) -> None:
        self.push_screen(
            PromptScreen(self._label, self._placeholder),
            callback=self._on_dismiss,
        )


async def _wait_for_modal(pilot, app: _Harness, timeout_s: float = 3.0) -> bool:
    """Poll until the PromptScreen is on the screen stack."""
    elapsed = 0.0
    tick = 0.05
    while elapsed < timeout_s:
        await pilot.pause()
        if any(isinstance(s, PromptScreen) for s in app.screen_stack):
            return True
        await asyncio.sleep(tick)
        elapsed += tick
    return False


async def _wait_for_dismiss(pilot, app: _Harness, timeout_s: float = 3.0) -> bool:
    elapsed = 0.0
    tick = 0.05
    while elapsed < timeout_s:
        await pilot.pause()
        if app._fired:
            return True
        await asyncio.sleep(tick)
        elapsed += tick
    return False


def test_prompt_screen_submit_returns_typed_value() -> None:
    app = _Harness(label="Add PR", placeholder="URL")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            # Type one char at a time then submit with enter.
            await pilot.press(*"hello")
            await pilot.press("enter")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured == "hello"

    asyncio.run(_run())


def test_prompt_screen_escape_returns_none() -> None:
    app = _Harness(label="Add PR", placeholder="URL")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            await pilot.press("escape")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured is None

    asyncio.run(_run())


def test_prompt_screen_empty_submit_returns_empty_string() -> None:
    """Hitting Enter with empty input dismisses with ''. Callers treat that as cancel."""
    app = _Harness(label="Add PR", placeholder="URL")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            await pilot.press("enter")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured == ""

    asyncio.run(_run())
