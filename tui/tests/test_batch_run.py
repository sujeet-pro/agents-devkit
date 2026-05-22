"""Pilot tests for the ζ batch runner (R action).

Per SPEC-zeta §9.2:
  1. R with no selection → log `(no rows selected — ...)`.
  2. R on a single ready row → spawns one worker, batch completes.
  3. R respects parallel cap: parallel_n=1 + 3 selected → never >1 in flight.
  4. R skips unready rows in selection and logs `(skipping ...)`.
  5. R while sync running → blocked.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from tui.app import AdkApp
from tui.widgets.footer_bar import FooterBar
from tui.widgets.log_pane import LogPane
from tui.widgets.queue_table import QueueTable


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


def _log_text(app: AdkApp) -> str:
    # Query the DEFAULT screen explicitly so the call still works when a
    # modal (e.g. RecapScreen pushed by ι at end-of-batch) is on top —
    # `app.query_one(X)` resolves against the active screen, which would
    # raise NoMatches in that case.
    pane = app.screen_stack[0].query_one(LogPane)
    lines = getattr(pane, "lines", [])
    return "\n".join(getattr(line, "text", None) or str(line) for line in lines)


def _footer_text(app: AdkApp) -> str:
    return str(app.screen_stack[0].query_one(FooterBar).render())


def _active_worker_count(app: AdkApp) -> int:
    workers = getattr(app, "_review_workers", {}) or {}
    return sum(1 for w in workers.values() if getattr(w, "returncode", None) is None)


async def _poll_until(predicate, *, pilot, timeout_s: float = 8.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


# --- 1. R with no selection ------------------------------------------------

def test_R_with_no_selection_logs_no_rows(
    eligible_multi_queue: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    app = AdkApp(
        queue_path=eligible_multi_queue,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app._selection_order == []
            await pilot.press("R")
            ok = await _poll_until(
                lambda: "no rows selected" in _log_text(app),
                pilot=pilot,
                timeout_s=2.0,
            )
            assert ok, f"expected 'no rows selected' message; log:\n{_log_text(app)}"

    asyncio.run(_run())


# --- 2. R on a single eligible row -----------------------------------------

def test_R_with_one_eligible_row_spawns_one_worker(
    eligible_multi_queue: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    app = AdkApp(
        queue_path=eligible_multi_queue,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("space")  # select cursor row
            await pilot.pause()
            await pilot.press("R")

            ok = await _poll_until(
                lambda: "batch start" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, f"batch never started; log:\n{_log_text(app)}"

            # Footer flips to running while the worker is alive.
            ok_running = await _poll_until(
                lambda: "[r] review (running…)" in _footer_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            # (best-effort; very fast fakes can complete before we poll)

            ok2 = await _poll_until(
                lambda: "batch done — 1 rows" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )
            text = _log_text(app)
            assert ok2, f"batch never finished; log:\n{text}"
            # After completion, the footer must NOT show running.
            await pilot.pause()
            footer_after = _footer_text(app)
            assert "(running…)" not in footer_after, footer_after

    asyncio.run(_run())


# --- 3. parallel cap is honored --------------------------------------------

def test_R_respects_parallel_cap(
    eligible_multi_queue: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
    tmp_path: Path,
) -> None:
    """parallel_n=1, 3 selected rows: count of live workers must never exceed 1
    while the batch is running."""
    slow = tmp_path / "slow-claude"
    slow.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "sleep 0.4\n"
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

            # Cycle parallel cap to 1: 4 → 8 → 1.
            await pilot.press("p")
            await pilot.pause()
            await pilot.press("p")
            await pilot.pause()
            assert app._parallel_n == 1, f"expected 1, got {app._parallel_n}"

            # Select all 3 rows.
            await pilot.press("space")
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            assert len(app._selection_order) == 3, app._selection_order

            await pilot.press("R")
            ok = await _poll_until(
                lambda: "batch start" in _log_text(app),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, f"batch never started; log:\n{_log_text(app)}"

            # Sample active worker count repeatedly while the batch runs.
            max_observed = 0
            elapsed = 0.0
            timeout_s = 20.0
            tick_s = 0.1
            while elapsed < timeout_s:
                await pilot.pause()
                await asyncio.sleep(tick_s)
                count = _active_worker_count(app)
                if count > max_observed:
                    max_observed = count
                if "batch done — 3 rows" in _log_text(app):
                    break
                elapsed += tick_s

            text = _log_text(app)
            assert "batch done — 3 rows" in text, f"batch never finished; log:\n{text}"
            assert max_observed <= 1, (
                f"parallel cap violated: observed {max_observed} workers with cap=1"
            )

    asyncio.run(_run())


# --- 4. R skips unready rows -----------------------------------------------

def test_R_skips_unready_rows(
    fake_queue_path: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """sample_queue has rows that are ready (#100) and not-ready (#101 preparing).
    Select one of each; R should log `(skipping ...)` for the not-ready and
    `(batch start — 1 rows ...)` for the ready one."""
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
            # Default-screen query so this stays valid if a modal is up later.
            table = app.screen_stack[0].query_one(QueueTable)

            # Walk rows; select one ready + one not-ready URL.
            ready_url: str | None = None
            unready_url: str | None = None
            for _ in range(table.row_count + 1):
                url = table.selected_pr_url()
                if url is not None:
                    row = app._rows_by_url.get(url)
                    if row is not None:
                        if row.ready_for_review and ready_url is None:
                            await pilot.press("space")
                            await pilot.pause()
                            ready_url = url
                        elif (not row.ready_for_review) and unready_url is None:
                            await pilot.press("space")
                            await pilot.pause()
                            unready_url = url
                if ready_url and unready_url:
                    break
                await pilot.press("j")
                await pilot.pause()

            assert ready_url is not None, "no ready row found in sample_queue"
            assert unready_url is not None, "no unready row found in sample_queue"

            await pilot.press("R")
            ok_skip = await _poll_until(
                lambda: f"skipping {unready_url}" in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            text = _log_text(app)
            assert ok_skip, (
                f"expected '(skipping {unready_url} ...)'; log:\n{text}"
            )
            ok_start = await _poll_until(
                lambda: "batch start — 1 rows" in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            text = _log_text(app)
            assert ok_start, f"expected 'batch start — 1 rows'; log:\n{text}"

            # Drain so the worker subprocess doesn't outlive the test.
            await _poll_until(
                lambda: "batch done — 1 rows" in _log_text(app),
                pilot=pilot,
                timeout_s=15.0,
            )

    asyncio.run(_run())


# --- 5. R while sync running is blocked ------------------------------------

def test_R_while_sync_running_blocked(
    eligible_multi_queue: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """Simulate an in-flight sync by stashing an alive-proc mock into
    `app._sync_proc`. R must refuse with `(can't start batch — sync already
    running)`."""

    class _AliveProcMock:
        returncode = None

        def terminate(self) -> None:  # pragma: no cover - used by on_unmount
            return None

        async def wait(self) -> int:  # pragma: no cover
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
            # Select a row so the precondition for R-with-empty-selection doesn't
            # short-circuit first.
            await pilot.press("space")
            await pilot.pause()
            assert app._selection_order, "row select failed"

            # Stash a fake in-flight sync.
            app._sync_proc = _AliveProcMock()

            await pilot.press("R")
            ok = await _poll_until(
                lambda: "can't start batch — sync already running" in _log_text(app),
                pilot=pilot,
                timeout_s=3.0,
            )
            text = _log_text(app)
            assert ok, f"expected sync-blocked message; log:\n{text}"

            # Clear the mock so on_unmount doesn't try to terminate it.
            app._sync_proc = None

    asyncio.run(_run())
