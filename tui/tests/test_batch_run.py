"""Sequential Sync + Review all (replaces multi-select batch runner)."""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.log_pane import LogPane


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


def _log_text(app: AdkApp) -> str:
    pane = app.screen_stack[0].query_one(LogPane)
    lines = getattr(pane, "lines", [])
    return "\n".join(getattr(line, "text", None) or str(line) for line in lines)


def _active_worker_count(app: AdkApp) -> int:
    workers = getattr(app, "_review_workers", {}) or {}
    return sum(1 for w in workers.values() if getattr(w, "returncode", None) is None)


async def _poll_until(predicate, *, pilot, timeout_s: float = 20.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


def test_sync_review_all_runs_sequentially(
    eligible_multi_queue: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
    tmp_path: Path,
) -> None:
    slow = tmp_path / "slow-claude"
    slow.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "sleep 0.35\n"
        "echo '[claude] done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    app = AdkApp(
        queue_path=eligible_multi_queue,
        agent_bin=slow,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("A")
            ok = await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            assert ok, f"sync phase never finished; log:\n{_log_text(app)}"

            max_observed = 0
            elapsed = 0.0
            while elapsed < 25.0:
                await pilot.pause()
                await asyncio.sleep(0.08)
                count = _active_worker_count(app)
                if count > max_observed:
                    max_observed = count
                if "Sync + Review all done" in _log_text(app):
                    break
                elapsed += 0.08

            text = _log_text(app)
            assert "Sync + Review all done" in text, f"run never finished; log:\n{text}"
            assert max_observed <= 1, (
                f"expected sequential reviews, observed {max_observed} concurrent workers"
            )

    asyncio.run(_run())


def test_sync_review_all_blocked_while_sync_all_running(
    eligible_multi_queue: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    class _AliveProcMock:
        returncode = None

        def terminate(self) -> None:
            return None

        async def wait(self) -> int:
            return 0

    app = AdkApp(
        queue_path=eligible_multi_queue,
        agent_bin=fake_claude_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            app._sync_proc = _AliveProcMock()
            await pilot.press("A")
            ok = await _poll_until(
                lambda: "can't start Sync + Review all — sync all already running"
                in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            assert ok, f"expected blocked message; log:\n{_log_text(app)}"
            app._sync_proc = None

    asyncio.run(_run())
