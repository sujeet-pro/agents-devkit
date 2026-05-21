"""Pilot tests for ζ selection model + parallel-cap cycling.

Per SPEC-zeta §9.1:
  1. space toggles selection (on/off) + renders [N] marker.
  2. Selection survives filter cycle.
  3. Selection is pruned when a URL disappears from the queue.
  4. `p` cycles _parallel_n through 4 → 8 → 1 → 2.
  5. Footer text shows sel:N + par:N.

These exercise state owned by Agent A in `tui/app.py`. If Agent A hasn't
landed the refactor yet, these will fail with AttributeError / missing
binding — that's the signal to merge A first.
"""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import pytest

from tui.app import AdkApp
from tui.widgets.footer_bar import FooterBar
from tui.widgets.queue_table import QueueTable


def _footer_text(app: AdkApp) -> str:
    return str(app.query_one(FooterBar).render())


def _table_icon_cells(app: AdkApp) -> list[str]:
    """Return the icon (column 0) cell text for every row, in display order."""
    table = app.query_one(QueueTable)
    cells: list[str] = []
    col_keys = list(table.columns)
    if not col_keys:
        return cells
    first_col = col_keys[0]
    for row_key in table.rows:
        cells.append(str(table.get_cell(row_key, first_col)))
    return cells


async def _poll_until(predicate, *, pilot, timeout_s: float = 3.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


# --- 1. space toggles selection --------------------------------------------

def test_space_toggles_selection(eligible_multi_queue: Path) -> None:
    """Press space on the highlighted row → URL appended to _selection_order
    and a `[1]` marker appears in the icon column. Press again → URL removed."""
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            url = table.selected_pr_url()
            assert url is not None, "no row highlighted at start"

            await pilot.press("space")
            await pilot.pause()
            assert url in app._selection_order, (
                f"URL not added to _selection_order: {app._selection_order}"
            )
            cells = _table_icon_cells(app)
            joined = " | ".join(cells)
            assert "[1]" in joined, f"expected [1] marker; cells: {joined}"

            await pilot.press("space")
            await pilot.pause()
            assert url not in app._selection_order, (
                f"URL not removed: {app._selection_order}"
            )
            cells_after = _table_icon_cells(app)
            joined_after = " | ".join(cells_after)
            assert "[1]" not in joined_after, (
                f"[1] marker still present after deselect; cells: {joined_after}"
            )

    asyncio.run(_run())


# --- 2. selection survives filter cycle ------------------------------------

def test_selection_survives_filter_cycle(eligible_multi_queue: Path) -> None:
    """Select 2 rows, press f (cycle filter), and confirm the selected URLs
    keep their [1] / [2] markers in order."""
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            first_url = table.selected_pr_url()
            await pilot.press("space")
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            second_url = table.selected_pr_url()
            assert second_url is not None and second_url != first_url
            await pilot.press("space")
            await pilot.pause()

            assert app._selection_order == [first_url, second_url], (
                f"unexpected selection order: {app._selection_order}"
            )

            await pilot.press("f")
            await pilot.pause()

            # The selection order in app state must not have changed.
            assert app._selection_order == [first_url, second_url], (
                f"selection mutated by filter cycle: {app._selection_order}"
            )

            # Both [1] and [2] markers must still be visible if the rows are
            # still present in the post-filter snapshot. eligible_multi_queue
            # has all-ready rows so any of the all/open/ready filters keep them.
            cells = _table_icon_cells(app)
            joined = " | ".join(cells)
            # Survive even if filter cycled to a mode that hides some — the
            # selection list itself is the contract; markers are best-effort.
            visible_urls = {u for u in app._rows_by_url}
            if first_url in visible_urls:
                assert "[1]" in joined, f"missing [1]; cells: {joined}"
            if second_url in visible_urls:
                assert "[2]" in joined, f"missing [2]; cells: {joined}"

    asyncio.run(_run())


# --- 3. selection pruned when URL disappears -------------------------------

def test_selection_pruned_when_url_disappears(
    eligible_multi_queue: Path, tmp_path: Path,
) -> None:
    """Select a row, then rewrite the queue file without that URL and force a
    reload. The selection list must drop the disappeared URL."""
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            url = table.selected_pr_url()
            assert url is not None
            await pilot.press("space")
            await pilot.pause()
            assert url in app._selection_order

            # Overwrite the queue file with a fresh version that DROPS the
            # selected URL. We rewrite from scratch to bump mtime.
            import json
            raw = json.loads(eligible_multi_queue.read_text())
            raw["prs"] = [r for r in raw["prs"] if r["pr_url"] != url]
            eligible_multi_queue.write_text(json.dumps(raw))

            # Force a reload (the model has a mtime gate; force=True bypasses).
            app._reload(force=True)
            await pilot.pause()

            assert url not in app._selection_order, (
                f"disappeared URL still in selection: {app._selection_order}"
            )

    asyncio.run(_run())


# --- 4. `p` cycles parallel cap --------------------------------------------

def test_p_cycles_parallel(eligible_multi_queue: Path) -> None:
    """Default _parallel_n is 4. `p` cycles 4 → 8 → 1 → 2 → 4."""
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app._parallel_n == 4, f"expected default 4, got {app._parallel_n}"

            await pilot.press("p")
            await pilot.pause()
            assert app._parallel_n == 8

            await pilot.press("p")
            await pilot.pause()
            assert app._parallel_n == 1

            await pilot.press("p")
            await pilot.pause()
            assert app._parallel_n == 2

            await pilot.press("p")
            await pilot.pause()
            assert app._parallel_n == 4

            footer = _footer_text(app)
            assert "par:4" in footer, f"expected par:4 in footer: {footer!r}"

    asyncio.run(_run())


# --- 5. footer shows selected count ----------------------------------------

def test_footer_shows_selected_count(eligible_multi_queue: Path) -> None:
    """Select 2 rows → footer text contains `sel:2`."""
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            footer0 = _footer_text(app)
            assert "sel:0" in footer0, f"expected sel:0 initially: {footer0!r}"

            await pilot.press("space")
            await pilot.pause()
            await pilot.press("j")
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()

            footer = _footer_text(app)
            assert "sel:2" in footer, f"expected sel:2; got: {footer!r}"

    asyncio.run(_run())
