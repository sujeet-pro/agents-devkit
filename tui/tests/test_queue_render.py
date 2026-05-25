from __future__ import annotations

import asyncio

from tui.app import AdkApp
from tui.model.queue_model import QueueModel
from tui.model.workers_model import WorkerRow
from tui.widgets.detail_pane import DetailPane, TabbedDetailPane
from tui.widgets.queue_table import QueueTable


def test_rows_visible(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            table = tui_app.query_one(QueueTable)
            assert table.row_count == 6

    asyncio.run(_run())


def test_empty_state_when_queue_missing(missing_queue_path):
    app = AdkApp(queue_path=missing_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            assert table.row_count == 1
            # Concatenate every cell render into a single string and substring-match.
            cells: list[str] = []
            for col_key in table.columns:
                for row_key in table.rows:
                    cells.append(str(table.get_cell(row_key, col_key)))
            blob = " ".join(cells)
            assert "no PRs" in blob

    asyncio.run(_run())


def test_queue_table_splits_pr_status_from_current_status(fake_queue_path, frozen_now):
    snapshot = QueueModel(queue_path=fake_queue_path, now_fn=lambda: frozen_now).snapshot()
    first = snapshot.rows[0]
    worker = WorkerRow(
        pid=123,
        worker_id="w123",
        run_id="run-1",
        pr_url=first.pr_url,
        subject=first.pr_url,
        task_type="review",
        status="running",
        agent="claude",
        queue=str(fake_queue_path),
        started_at="2026-05-21T17:59:00Z",
        last_heartbeat="2026-05-21T17:59:30Z",
        current_phase="phase 3: feature-flow",
        rc=None,
        log_path="/tmp/review.log",
        links={},
        artifacts={},
        age_s=10.0,
        is_stale=False,
    )
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            table.load(snapshot, workers_by_url={first.pr_url: worker})

            row_key = next(iter(table.rows))
            col_keys = list(table.columns)
            # col[3] is now the "task" column showing derive_task_status output.
            # With an active review worker, the task status must be "reviewing".
            assert str(table.get_cell(row_key, col_keys[3])) == "reviewing"
            assert "phase 3: feature-flow" in str(table.get_cell(row_key, col_keys[4]))

    asyncio.run(_run())


def test_detail_pane_updates_on_cursor_move(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            # DetailPane is the Overview sub-widget inside TabbedDetailPane.
            pane = tui_app.query_one(DetailPane)
            before = pane.overview_text
            await pilot.press("j")
            await pilot.pause()
            after = pane.overview_text
            assert before != after

    asyncio.run(_run())
