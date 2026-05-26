"""Pilot tests for the `+` (add-PR) action — η §7.3.

The `+` binding pushes a PromptScreen modal; on submit, spawns
`adk pr-queue add <input> -y` and streams its output into the LogPane.
On escape or empty submit, no subprocess is spawned.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.screens.prompt_screen import PromptScreen
from tui.widgets.detail_pane import TabbedDetailPane


def _log_text(app: AdkApp) -> str:
    try:
        ap = app.query_one(TabbedDetailPane).activity_pane()
        return "\n".join(ap._log_buffer)
    except Exception:
        return ""


async def _poll_until(predicate, *, pilot, timeout_s: float = 5.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        if predicate():
            return True
        await asyncio.sleep(tick_s)
        elapsed += tick_s
    return False


def test_plus_pushes_prompt_modal_onto_stack(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
) -> None:
    """Pressing `+` pushes a PromptScreen modal onto the screen stack."""
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(app.screen_stack) == 1
            await pilot.press("plus")
            ok = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok, "PromptScreen never pushed"
            assert len(app.screen_stack) == 2

    asyncio.run(_run())


def test_plus_then_submit_spawns_pr_queue_add(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
) -> None:
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("plus")
            ok = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok, "PromptScreen never appeared"
            url = "https://github.com/foo/bar/pull/42"
            await pilot.press(*url)
            await pilot.press("enter")
            ok2 = await _poll_until(
                lambda: "pr-queue add exited rc=0" in _log_text(app),
                pilot=pilot, timeout_s=8.0,
            )
            text = _log_text(app)
            assert ok2, f"subprocess never finished. log:\n{text}"
            assert "$ " in text
            assert str(fake_adk_script) in text
            assert "pr-queue" in text
            assert "add" in text
            assert url in text
            assert "-y" in text
            assert "pr-scan: running" in text

    asyncio.run(_run())


def test_plus_then_escape_does_not_spawn_subprocess(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
) -> None:
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("plus")
            ok = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            await pilot.press("escape")
            await _poll_until(
                lambda: len(app.screen_stack) == 1,
                pilot=pilot, timeout_s=2.0,
            )
            assert len(app.screen_stack) == 1
            await asyncio.sleep(0.3)
            await pilot.pause()
            text = _log_text(app)
            assert "pr-queue" not in text
            assert "exited rc=" not in text

    asyncio.run(_run())


def test_plus_then_empty_submit_does_not_spawn_subprocess(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
) -> None:
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("plus")
            ok = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            await pilot.press("enter")
            await _poll_until(
                lambda: len(app.screen_stack) == 1,
                pilot=pilot, timeout_s=2.0,
            )
            assert len(app.screen_stack) == 1
            await asyncio.sleep(0.3)
            await pilot.pause()
            text = _log_text(app)
            assert "pr-queue" not in text
            assert "exited rc=" not in text

    asyncio.run(_run())
