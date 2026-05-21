"""Pilot tests for tui/screens/agent_picker_screen.py — κ §8.2.

AgentPickerScreen is a ModalScreen[str | None]. On enter it dismisses
with the picked agent's id (registry name). On escape it dismisses with
None. The modal must be pushed inside an actual App for Textual's modal
machinery to work — we use the same _Harness pattern as
test_prompt_screen.py.
"""
from __future__ import annotations

import asyncio

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.agent_registry import list_agents
from tui.screens.agent_picker_screen import AgentPickerScreen


class _Harness(App):
    """Minimal App that pushes an AgentPickerScreen and captures dismiss."""

    def __init__(self, current: str = "claude") -> None:
        super().__init__()
        self._current = current
        self.captured: str | None = "<unset>"  # sentinel
        self._fired = False

    def compose(self) -> ComposeResult:
        yield Static("host")

    def _on_dismiss(self, value: str | None) -> None:
        self.captured = value
        self._fired = True

    def on_mount(self) -> None:
        self.push_screen(
            AgentPickerScreen(current=self._current),
            callback=self._on_dismiss,
        )


async def _wait_for_modal(pilot, app: _Harness, timeout_s: float = 3.0) -> bool:
    elapsed = 0.0
    tick = 0.05
    while elapsed < timeout_s:
        await pilot.pause()
        if any(isinstance(s, AgentPickerScreen) for s in app.screen_stack):
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


def test_agent_picker_appears_and_highlights_current() -> None:
    """Modal appears; the OptionList highlights the current agent."""
    app = _Harness(current="claude")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            # Locate the picker screen and its OptionList; verify the
            # highlighted index points at the current agent.
            from textual.widgets import OptionList

            picker = next(
                s for s in app.screen_stack if isinstance(s, AgentPickerScreen)
            )
            opt_list = picker.query_one(OptionList)
            specs = list_agents()
            expected_idx = next(
                i for i, s in enumerate(specs) if s.name == "claude"
            )
            assert opt_list.highlighted == expected_idx, (
                f"expected highlighted={expected_idx} (claude), "
                f"got {opt_list.highlighted}"
            )
            # Don't leave the modal dangling — cancel before exit.
            await pilot.press("escape")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"

    asyncio.run(_run())


def test_agent_picker_escape_dismisses_with_none() -> None:
    app = _Harness(current="claude")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            await pilot.press("escape")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured is None, (
                f"expected None on escape, got {app.captured!r}"
            )

    asyncio.run(_run())


def test_agent_picker_down_then_enter_picks_second_agent() -> None:
    """From claude (idx 0), pressing `down` highlights codex (idx 1); enter
    dismisses with 'codex'."""
    app = _Harness(current="claude")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            await pilot.press("down")
            await pilot.press("enter")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured == "codex", (
                f"expected 'codex', got {app.captured!r}"
            )

    asyncio.run(_run())


def test_agent_picker_enter_on_current_returns_current_id() -> None:
    """If you don't move, enter dismisses with the current agent's id."""
    app = _Harness(current="claude")

    async def _run() -> None:
        async with app.run_test() as pilot:
            assert await _wait_for_modal(pilot, app), "modal never appeared"
            await pilot.press("enter")
            assert await _wait_for_dismiss(pilot, app), "modal never dismissed"
            assert app.captured == "claude", (
                f"expected 'claude', got {app.captured!r}"
            )

    asyncio.run(_run())
