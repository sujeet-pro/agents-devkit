"""Tests for the simplified work-queue TUI (no multi-select)."""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp
from tui.widgets.footer_bar import FooterBar
from tui.widgets.queue_table import QueueTable


def _footer_text(app: AdkApp) -> str:
    return str(app.query_one(FooterBar).render())


def _current_cells(app: AdkApp) -> list[str]:
    table = app.query_one(QueueTable)
    active_cols = table._current_column_set or ()
    if "current" not in active_cols:
        return []
    col_keys = list(table.columns)
    current_idx = active_cols.index("current")
    current_col = col_keys[current_idx]
    return [str(table.get_cell(row_key, current_col)) for row_key in table.rows]


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


def test_footer_shows_four_primary_actions(tui_app) -> None:
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            footer = _footer_text(tui_app)
            assert "[S]Sync PR" in footer
            assert "[R]Sync+Rev" in footer
            assert "[s]Sync all" in footer
            assert "[A]Sync+Rev all" in footer
            assert "run-sel" not in footer
            assert "[space]" not in footer
            assert "par:" not in footer
            assert "sel:" not in footer

    asyncio.run(_run())


def test_footer_has_no_multi_select_labels(eligible_multi_queue: Path) -> None:
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            footer = _footer_text(app)
            assert "[r] review" not in footer
            assert "[p]" not in footer

    asyncio.run(_run())


def test_sync_pr_shows_running_state_in_table(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    fake_adk_script: Path,
    tmp_path: Path,
) -> None:
    slow = tmp_path / "slow-adk"
    slow.write_text(
        "#!/bin/sh\n"
        "echo \"$@\"\n"
        "sleep 0.6\n"
        "echo ok\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=slow,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("S")
            ok = await _poll_until(
                lambda: any("running (sync)" in cell for cell in _current_cells(app)),
                pilot=pilot,
                timeout_s=4.0,
            )
            assert ok, f"expected running work state; cells={_current_cells(app)}"

    asyncio.run(_run())
