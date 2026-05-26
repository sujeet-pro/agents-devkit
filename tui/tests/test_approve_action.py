from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Static

from tui.app import AdkApp
from tui.screens.confirm_screen import ConfirmScreen
from tui.widgets.activity_pane import ActivityPane


def _log_text(app: AdkApp) -> str:
    try:
        pane = app.screen_stack[0].query_one(ActivityPane)
        widget = pane.query_one("#activity-log", Static)
        return str(widget.content)
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


def _recording_adk(tmp_path: Path, log_path: Path) -> Path:
    p = tmp_path / "adk"
    p.write_text(
        f"#!/bin/sh\n"
        f"echo \"$@\" >> \"{log_path}\"\n"
        "echo ok\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


def test_press_a_with_row_opens_confirm_screen(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, (
                f"ConfirmScreen never appeared after 'a'.\n"
                f"screens={[type(s).__name__ for s in app.screen_stack]}"
            )

    asyncio.run(_run())


def test_press_a_then_n_does_not_invoke_cli(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, "ConfirmScreen did not open"
            await pilot.press("n")
            await pilot.pause()
            await pilot.pause()

    asyncio.run(_run())
    assert not log_path.exists(), (
        f"CLI was invoked despite 'n' dismissal.\nCalls:\n{log_path.read_text()}"
    )


def test_press_a_then_y_invokes_approve_command(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, "ConfirmScreen did not open"
            await pilot.press("y")
            ok2 = await _poll_until(
                lambda: "approve PR exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=5.0,
            )
            assert ok2, f"approve command never completed.\nlog:\n{_log_text(app)}"

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "approve" in calls
    assert "--yes" in calls


def test_press_a_then_y_passes_queue_and_pr_url(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, "ConfirmScreen did not open"
            await pilot.press("y")
            ok2 = await _poll_until(
                lambda: "approve PR exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=5.0,
            )
            assert ok2, f"approve command never completed.\nlog:\n{_log_text(app)}"

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "--queue" in calls
    assert "approve" in calls
    assert "--yes" in calls
    assert "https://github.com/foo/bar/pull/200" in calls


def test_press_a_with_no_row_logs_no_row_selected(
    missing_queue_path: Path,
    fake_adk_script: Path,
) -> None:
    app = AdkApp(
        queue_path=missing_queue_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            ok = await _poll_until(
                lambda: "(no row selected)" in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, f"expected '(no row selected)' in log; got:\n{_log_text(app)}"

    asyncio.run(_run())


def test_press_a_with_no_row_does_not_open_confirm_screen(
    missing_queue_path: Path,
    fake_adk_script: Path,
) -> None:
    app = AdkApp(
        queue_path=missing_queue_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("a")
            await _poll_until(
                lambda: "(no row selected)" in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert not any(isinstance(s, ConfirmScreen) for s in app.screen_stack), (
                "ConfirmScreen must not appear when no row is selected"
            )

    asyncio.run(_run())
