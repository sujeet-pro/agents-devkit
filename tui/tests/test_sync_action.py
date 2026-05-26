"""Pilot-driven tests for the `s` action that spawns pr-sync as a subprocess
and streams its stdout into the LogPane. Per SPEC §6.4."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from tui.app import AdkApp
from tui.widgets.detail_pane import TabbedDetailPane
from tui.widgets.queue_action_bar import QueueActionBar


def _log_text(app: AdkApp) -> str:
    """Concatenate every line in the ActivityPane log buffer."""
    try:
        ap = app.query_one(TabbedDetailPane).activity_pane()
        return "\n".join(ap._log_buffer)
    except Exception:
        return ""


def _queue_action_text(app: AdkApp) -> str:
    return str(app.query_one(QueueActionBar).render())


async def _poll_until(predicate, *, pilot, timeout_s: float = 5.0,
                      tick_s: float = 0.05) -> bool:
    """Tick the Pilot event loop until predicate() is truthy or we time out."""
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


def test_sync_streams_subprocess_output_into_log(
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
            await pilot.press("S")
            # Give the subprocess time to launch + emit + exit; the readline
            # loop and on_exit announce-write are async.
            ok = await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            text = _log_text(app)
            assert ok, f"subprocess never finished within timeout. log:\n{text}"
            # The `$ ...` command line was announced first.
            assert "$ " in text
            assert str(fake_adk_script) in text
            assert "pr-sync" in text
            # The 3 echoed lines from the fake script reach the pane.
            assert "pr-scan: running" in text
            assert "pr-scan: 0 new" in text
            assert "done" in text

    asyncio.run(_run())


def test_sync_footer_shows_running_label_mid_run(
    fake_queue_path: Path, fake_plan_path: Path, tmp_path: Path,
) -> None:
    """Use a script that sleeps long enough that the assertion can fire while
    the subprocess is still alive."""
    slow = tmp_path / "slow-adk"
    slow.write_text(
        "#!/bin/sh\n"
        "echo 'starting'\n"
        "sleep 1.5\n"
        "echo 'done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=slow,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("S")
            # Wait until at least the `$ ...` announce has reached the log so
            # we know the subprocess has been spawned and the footer is set.
            ok = await _poll_until(
                lambda: "starting" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, "subprocess never produced the starting line"
            # While the subprocess is still alive (sleeping), the QueueActionBar
            # must show the (running…) label.
            bar = _queue_action_text(app)
            assert "Sync all (running…)" in bar, (
                f"expected running label in queue_action_bar, got: {bar!r}"
            )
            # Wait for clean exit so the test doesn't leave a child hanging.
            ok2 = await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            assert ok2, "subprocess never exited"
            # After exit, the bar flips back.
            await pilot.pause()
            bar_after = _queue_action_text(app)
            assert "(running…)" not in bar_after

    asyncio.run(_run())


def test_sync_idempotent_when_already_running(
    fake_queue_path: Path, fake_plan_path: Path, tmp_path: Path,
) -> None:
    """Pressing `s` while a sync is in flight must NOT spawn a second
    subprocess. The LogPane should announce the already-running state."""
    slow = tmp_path / "slow-adk"
    slow.write_text(
        "#!/bin/sh\n"
        "echo 'starting'\n"
        "sleep 1.0\n"
        "echo 'done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=slow,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("S")
            ok = await _poll_until(
                lambda: "starting" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok
            # Press `S` again while still running.
            await pilot.press("S")
            ok2 = await _poll_until(
                lambda: "Sync all already running" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok2, f"expected 'already running' message; log:\n{_log_text(app)}"
            # Drain.
            await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )

    asyncio.run(_run())
