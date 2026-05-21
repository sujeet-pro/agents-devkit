"""Pilot-driven tests for the `r` review action (δ).

These exercise the TUI's `r` keybinding wiring: precondition checks (row
selected, ready), subprocess spawn of `tui/worker.py`, busy-mutex with sync.
The worker subprocess is steered with injected `--agent-bin` + `--adk-bin`
fakes so no real `claude -p` / `adk` calls happen.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from tui.app import AdkApp
from tui.widgets.footer_bar import FooterBar
from tui.widgets.log_pane import LogPane


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


def _log_text(app: AdkApp) -> str:
    pane = app.query_one(LogPane)
    lines = getattr(pane, "lines", [])
    return "\n".join(getattr(line, "text", None) or str(line) for line in lines)


def _footer_text(app: AdkApp) -> str:
    return str(app.query_one(FooterBar).render())


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


# --- 1. no row selected -----------------------------------------------------

def test_r_with_no_row_selected_logs_no_row(
    missing_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """With a missing queue file there's no selectable PR row → `(no row
    selected)`."""
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
            await pilot.press("r")
            ok = await _poll_until(
                lambda: "(no row selected)" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected '(no row selected)' in log; got:\n{_log_text(app)}"

    asyncio.run(_run())


# --- 2. row not ready -------------------------------------------------------

def test_r_on_not_ready_row_logs_not_ready(
    fake_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """sample_queue's first row (#100) IS ready per the predicate; we need to
    move the cursor to a row that fails ready_for_review. Row #101 has
    `prep_status=preparing` → not ready. Sort=fifo orders by last_checked_at;
    let's just press `j` until we hit a not-ready row."""
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
            # Walk the table looking for a not-ready row. We give up after
            # the table size — sample_queue.json5 has 6 rows.
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

            await pilot.press("r")
            ok = await _poll_until(
                lambda: "(row not ready" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected '(row not ready' in log; got:\n{_log_text(app)}"

    asyncio.run(_run())


# --- 3. eligible row spawns worker -----------------------------------------

def test_r_on_eligible_row_spawns_worker_and_streams_output(
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
            await pilot.press("r")

            ok = await _poll_until(
                lambda: "(worker exited rc=0)" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )
            text = _log_text(app)
            assert ok, f"worker never finished; log:\n{text}"
            # The `$ ...` announce line for the python worker invocation.
            assert "$ " in text, text
            assert str(WORKER_SCRIPT) in text, text
            # The 3 claude lines reach the pane.
            assert "[claude] phase 2: querying" in text, text
            assert "[claude] phase 6: report" in text, text
            # After exit, footer should NOT show running label.
            await pilot.pause()
            footer_after = _footer_text(app)
            assert "(running…)" not in footer_after, footer_after

    asyncio.run(_run())


# --- 4. `s` while review running --------------------------------------------

def test_s_while_review_running_blocked(
    eligible_queue_path: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
    tmp_path: Path,
) -> None:
    """Use a slow fake_claude so we can press `s` while review is mid-run."""
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
            await pilot.press("r")
            # Wait until the review is clearly mid-run.
            ok = await _poll_until(
                lambda: "[claude] starting" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            assert ok, f"review never started; log:\n{_log_text(app)}"

            await pilot.press("s")
            ok2 = await _poll_until(
                lambda: "(can't start sync — review already running)" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok2, (
                f"expected sync-blocked message; log:\n{_log_text(app)}"
            )
            # Drain so the test doesn't leave a child hanging.
            await _poll_until(
                lambda: "(worker exited rc=0)" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )

    asyncio.run(_run())


# --- 5. `r` while sync running ----------------------------------------------

def test_r_while_sync_running_blocked(
    eligible_queue_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """Use a slow fake_adk (used by `s`) so a sync is mid-run when we press
    `r`."""
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

            await pilot.press("r")
            ok2 = await _poll_until(
                lambda: "(can't start review — sync already running)" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok2, (
                f"expected review-blocked message; log:\n{_log_text(app)}"
            )
            # Drain.
            await _poll_until(
                lambda: "pr-sync exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )

    asyncio.run(_run())
