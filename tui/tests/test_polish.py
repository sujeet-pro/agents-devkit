"""Pilot tests for λ — theme cycle + detach prompt + reattach banner."""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.app import AdkApp, _THEME_CYCLE
from tui.screens.confirm_screen import ConfirmScreen
from tui.widgets.detail_pane import TabbedDetailPane


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


def _log_text(app: AdkApp) -> str:
    try:
        ap = app.query_one(TabbedDetailPane).activity_pane()
        return "\n".join(ap._log_buffer)
    except Exception:
        return ""


async def _poll_until(predicate, *, pilot, timeout_s: float = 4.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        if predicate():
            return True
        await asyncio.sleep(tick_s)
        elapsed += tick_s
    return False


# --- 1. theme cycle ---------------------------------------------------------

def test_theme_cycle_constant_exists(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
) -> None:
    # _THEME_CYCLE is imported so callers can reference valid theme names;
    # the interactive binding was moved to help_screen. Verify the constant is non-empty.
    assert len(_THEME_CYCLE) > 0
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.theme in _THEME_CYCLE, (
                f"default theme {app.theme!r} not in _THEME_CYCLE"
            )

    asyncio.run(_run())


# --- 2. ConfirmScreen unit-style (via a tiny host app) ---------------------

class _Harness(App):
    def __init__(self, prompt: str) -> None:
        super().__init__()
        self._prompt = prompt
        self.result: bool | None = None

    def compose(self) -> ComposeResult:
        yield Static("(harness)")

    def on_mount(self) -> None:
        # Use the callback form to avoid needing a worker context here —
        # ConfirmScreen's dismiss(value) routes the value into the callback.
        self.push_screen(ConfirmScreen(self._prompt), callback=self._record)

    def _record(self, result: bool) -> None:
        self.result = result


def test_confirm_screen_y_returns_true() -> None:
    app = _Harness("Test prompt — really?")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, ConfirmScreen)
            await pilot.press("y")
            await pilot.pause()
            await pilot.pause()
            assert app.result is True

    asyncio.run(_run())


def test_confirm_screen_n_returns_false() -> None:
    app = _Harness("Test prompt — really?")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            await pilot.pause()
            assert app.result is False

    asyncio.run(_run())


def test_confirm_screen_escape_returns_false() -> None:
    app = _Harness("Test prompt — really?")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            await pilot.pause()
            assert app.result is False

    asyncio.run(_run())


def test_confirm_screen_enter_returns_true() -> None:
    app = _Harness("Test prompt — really?")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.pause()
            assert app.result is True

    asyncio.run(_run())


# --- 3. q-while-busy detach prompt ------------------------------------------

class _AliveProcMock:
    """Mimics an asyncio.subprocess.Process that's still running."""
    def __init__(self) -> None:
        self.returncode: int | None = None

    def terminate(self) -> None:
        self.returncode = -15

    async def wait(self) -> int:
        return self.returncode if self.returncode is not None else 0


def test_q_while_idle_quits_immediately(
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
            await pilot.press("q")
            await pilot.pause()
        # If the app exited the run_test() context cleanly, that's success.
        assert app.return_value is None

    asyncio.run(_run())


def test_q_while_review_running_prompts_confirm(
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
            # Simulate a live worker without spawning a real subprocess.
            app._review_workers["fake-url"] = _AliveProcMock()  # type: ignore[assignment]
            await pilot.press("q")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok, "ConfirmScreen never appeared"
            # Pressing `n` dismisses and the app stays alive.
            await pilot.press("n")
            await pilot.pause()
            await pilot.pause()
            assert not any(isinstance(s, ConfirmScreen) for s in app.screen_stack)
            # App is still alive (no exit).
            assert app._review_workers, "live worker entry should still be tracked"

    asyncio.run(_run())


def test_q_while_review_running_y_quits(
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
            app._review_workers["fake-url"] = _AliveProcMock()  # type: ignore[assignment]
            await pilot.press("q")
            ok = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            await pilot.press("y")
            await pilot.pause()

    asyncio.run(_run())


# --- 4. Reattach banner -----------------------------------------------------

def test_reattach_banner_when_existing_workers(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
    tmp_path: Path,
) -> None:
    """When the heartbeat dir already has live <pid>.json files at mount,
    the LogPane shows a reattach banner."""
    hb_dir = tmp_path / "workers"
    hb_dir.mkdir()
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (hb_dir / "12345.json").write_text(json.dumps({
        "pid": 12345, "pr_url": "https://github.com/acme/foo/pull/42",
        "task_type": "review", "agent": "claude", "queue": "/tmp/q",
        "started_at": now_iso, "last_heartbeat": now_iso,
        "current_phase": "phase 2: review", "rc": None,
    }))
    (hb_dir / "12346.json").write_text(json.dumps({
        "pid": 12346, "pr_url": "https://github.com/acme/foo/pull/43",
        "task_type": "review", "agent": "claude", "queue": "/tmp/q",
        "started_at": now_iso, "last_heartbeat": now_iso,
        "current_phase": "phase 4: Triage", "rc": None,
    }))

    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        heartbeat_dir=hb_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            log = _log_text(app)
            assert "(reattached: 2 existing workers" in log, log

    asyncio.run(_run())


def test_no_reattach_banner_when_no_existing_workers(
    fake_queue_path: Path, fake_plan_path: Path, fake_adk_script: Path,
    tmp_path: Path,
) -> None:
    hb_dir = tmp_path / "workers"
    hb_dir.mkdir()
    app = AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        heartbeat_dir=hb_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            log = _log_text(app)
            assert "reattached" not in log

    asyncio.run(_run())
