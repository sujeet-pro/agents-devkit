"""Action bar / primary action tests.

Validates that the primary action surface exposes exactly the four new
actions and none of the removed multi-select / parallel controls.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.footer_bar import FooterBar
from tui.widgets.log_pane import LogPane


def _footer_text(app: AdkApp) -> str:
    return str(app.query_one(FooterBar).render())


def _log_text(app: AdkApp) -> str:
    pane = app.query_one(LogPane)
    lines = getattr(pane, "lines", [])
    return "\n".join(getattr(line, "text", None) or str(line) for line in lines)


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

def test_footer_has_sync_pr_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[1] Sync PR" in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_sync_review_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[2] Sync+Review" in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_sync_all_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[s] Sync all" in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_sync_review_all_action(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[A] Sync+Review all" in _footer_text(tui_app)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Removed controls must not appear in footer
# ---------------------------------------------------------------------------

def test_footer_has_no_run_selected(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "run-sel" not in _footer_text(tui_app)
            assert "[R]" not in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_no_space_select(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[space]" not in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_no_parallel_key(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "[p]" not in _footer_text(tui_app)

    asyncio.run(_run())


def test_footer_has_no_sel_count(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            assert "sel:" not in _footer_text(tui_app)
            assert "par:" not in _footer_text(tui_app)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# No parallel actions: pressing 1 while work running is blocked
# ---------------------------------------------------------------------------

def test_sync_pr_blocked_while_work_running(eligible_queue_path: Path) -> None:
    """Pressing 1 (Sync PR) while a work task is already running must be refused."""
    app = AdkApp(queue_path=eligible_queue_path, poll_interval=0.05)

    import asyncio as _asyncio

    class _FakeTask:
        def done(self) -> bool:
            return False

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            app._work_task = _FakeTask()  # type: ignore[assignment]
            await pilot.press("1")
            ok = await _poll_until(
                lambda: "can't start Sync PR" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected busy message; log:\n{_log_text(app)}"
            app._work_task = None

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Sync all running shows label
# ---------------------------------------------------------------------------

def test_sync_all_footer_shows_running_when_proc_alive(
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
            await pilot.press("s")
            ok = await _poll_until(
                lambda: "starting" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, "sync never started"
            footer = _footer_text(app)
            assert "[s] Sync all (running…)" in footer, (
                f"expected running label; footer={footer!r}"
            )
            await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )

    asyncio.run(_run())
