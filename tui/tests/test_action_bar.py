"""Action bar / primary action tests.

Validates that the four action bars expose the correct keybind chips and that
removed multi-select / parallel controls are absent.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.detail_pane import TabbedDetailPane
from tui.widgets.pr_action_bar import PRActionBar
from tui.widgets.queue_action_bar import QueueActionBar


def _queue_action_text(app: AdkApp) -> str:
    return str(app.query_one(QueueActionBar).render())


def _pr_action_text(app: AdkApp) -> str:
    return str(app.query_one(PRActionBar).render())


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
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


# ---------------------------------------------------------------------------
# Primary action labels
# ---------------------------------------------------------------------------

def test_pr_action_bar_has_sync_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            # Select the first row so PRActionBar shows actions.
            await pilot.press("j")
            await pilot.pause()
            text = _pr_action_text(tui_app)
            assert "sync" in text.lower()

    asyncio.run(_run())


def test_pr_action_bar_has_remove_chip(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            text = _pr_action_text(tui_app)
            assert "remove" in text.lower()

    asyncio.run(_run())


def test_queue_action_bar_has_sync_all_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            text = _queue_action_text(tui_app)
            assert "Sync all" in text

    asyncio.run(_run())


def test_queue_action_bar_has_review_all_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            text = _queue_action_text(tui_app)
            assert "Review all" in text

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Removed controls must not appear in any action bar
# ---------------------------------------------------------------------------

def test_no_run_selected_in_action_bars(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "run-sel" not in _queue_action_text(tui_app)
            assert "run-sel" not in _pr_action_text(tui_app)

    asyncio.run(_run())


def test_no_space_select_in_action_bars(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[space]" not in _queue_action_text(tui_app)
            assert "[space]" not in _pr_action_text(tui_app)

    asyncio.run(_run())


def test_no_parallel_key_in_action_bars(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[p]" not in _queue_action_text(tui_app)
            assert "[p]" not in _pr_action_text(tui_app)

    asyncio.run(_run())


def test_no_sel_count_in_action_bars(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            for text in (_queue_action_text(tui_app), _pr_action_text(tui_app)):
                assert "sel:" not in text
                assert "par:" not in text

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# No parallel actions: pressing S while work running is blocked
# ---------------------------------------------------------------------------

def test_sync_pr_blocked_while_work_running(eligible_queue_path: Path) -> None:
    """Pressing s (sync PR) while a work task is already running must be refused."""
    app = AdkApp(queue_path=eligible_queue_path, poll_interval=0.05)

    class _FakeTask:
        def done(self) -> bool:
            return False

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            app._work_task = _FakeTask()  # type: ignore[assignment]
            await pilot.press("s")
            ok = await _poll_until(
                lambda: "can't start Sync PR" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected busy message; log:\n{_log_text(app)}"
            app._work_task = None

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Sync all running shows label in QueueActionBar
# ---------------------------------------------------------------------------

def test_sync_all_queue_action_shows_running_when_proc_alive(
    eligible_queue_path: Path, tmp_path: Path,
) -> None:
    slow = tmp_path / "slow-adk"
    slow.write_text(
        "#!/bin/sh\n"
        "echo 'starting'\n"
        "sleep 1.2\n"
        "echo 'done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)
    app = AdkApp(queue_path=eligible_queue_path, adk_bin=slow, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("S")
            ok = await _poll_until(
                lambda: "starting" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, "sync never started"
            bar = _queue_action_text(app)
            assert "Sync all (running…)" in bar, (
                f"expected running label; queue_action_bar={bar!r}"
            )
            await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )

    asyncio.run(_run())
