"""Pilot-driven tests for Sync + Review (`2`) and secondary review actions."""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.detail_pane import TabbedDetailPane


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


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


def test_sync_review_with_no_row_selected_logs_no_row(
    missing_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    app = AdkApp(
        queue_path=missing_queue_path,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("R")
            ok = await _poll_until(
                lambda: "(no row selected)" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected '(no row selected)' in log; got:\n{_log_text(app)}"

    asyncio.run(_run())


def test_sync_review_on_not_ready_row_marks_skipped(
    fake_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    app = AdkApp(
        queue_path=fake_queue_path,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            from tui.widgets.queue_table import QueueTable
            table = app.query_one(QueueTable)
            found = False
            for _ in range(table.row_count + 1):
                url = table.selected_pr_url()
                if url is not None:
                    row = app._rows_by_url.get(url)
                    if row is not None and not row.ready_for_review:
                        found = True
                        break
                await pilot.press("j")
                await pilot.pause()
            assert found, "no not-ready row found in sample_queue fixture"

            await pilot.press("R")
            ok = await _poll_until(
                lambda: "skipping review — row not ready" in _log_text(app)
                or any(
                    s.status == "skipped"
                    for s in app._work_queue.all_states().values()
                ),
                pilot=pilot,
                timeout_s=15.0,
            )
            assert ok, f"expected skipped review; log:\n{_log_text(app)}"

    asyncio.run(_run())


def test_sync_review_on_eligible_row_spawns_worker(
    eligible_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    app = AdkApp(
        queue_path=eligible_queue_path,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("R")
            ok = await _poll_until(
                lambda: "(worker exited rc=0)" in _log_text(app),
                pilot=pilot,
                timeout_s=20.0,
            )
            text = _log_text(app)
            assert ok, f"worker never finished; log:\n{text}"
            assert str(WORKER_SCRIPT) in text, text

    asyncio.run(_run())


def test_sync_all_while_sync_review_blocked(
    eligible_queue_path: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
    tmp_path: Path,
) -> None:
    slow_claude = tmp_path / "slow-claude"
    slow_claude.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "sleep 1.5\n"
        "echo '[claude] done'\n"
        "exit 0\n"
    )
    slow_claude.chmod(0o755)

    app = AdkApp(
        queue_path=eligible_queue_path,
        agent_bin=slow_claude,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("R")
            ok = await _poll_until(
                lambda: "[claude] starting" in _log_text(app),
                pilot=pilot,
                timeout_s=12.0,
            )
            assert ok, f"sync+review never started; log:\n{_log_text(app)}"

            await pilot.press("s")
            ok2 = await _poll_until(
                lambda: "(can't start Sync all — work queue already running)"
                in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok2, f"expected sync-blocked message; log:\n{_log_text(app)}"
            await _poll_until(
                lambda: "(worker exited rc=0)" in _log_text(app),
                pilot=pilot,
                timeout_s=20.0,
            )

    asyncio.run(_run())


def test_sync_review_while_sync_all_blocked(
    eligible_queue_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    slow_adk = tmp_path / "slow-adk"
    slow_adk.write_text(
        "#!/bin/sh\n"
        "echo 'pr-sync: starting'\n"
        "sleep 1.5\n"
        "echo 'pr-sync: done'\n"
        "exit 0\n"
    )
    slow_adk.chmod(0o755)

    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        agent_bin=fake_claude_script,
        adk_bin=slow_adk,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("s")
            ok = await _poll_until(
                lambda: "pr-sync: starting" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            assert ok, f"sync never started; log:\n{_log_text(app)}"

            await pilot.press("R")
            ok2 = await _poll_until(
                lambda: "(can't start Sync + Review — sync all already running)"
                in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok2, f"expected blocked message; log:\n{_log_text(app)}"
            await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )

    asyncio.run(_run())
