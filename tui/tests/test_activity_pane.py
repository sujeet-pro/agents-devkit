from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.model.runs_model import RunRow
from tui.model.sync_plan_model import SyncPlanSnapshot, SyncPlanStep
from tui.model.workers_model import WorkerRow
from tui.widgets.activity_pane import ActivityPane


class _Harness(App):
    def compose(self) -> ComposeResult:
        yield ActivityPane()


def _log_text(app: _Harness) -> str:
    return str(app.query_one("#activity-log", Static).content)


def _worker(
    pr_url: str = "https://github.com/acme/foo/pull/42",
    status: str = "running",
) -> WorkerRow:
    return WorkerRow(
        pid=12345,
        worker_id="w-12345",
        run_id=None,
        pr_url=pr_url,
        subject=pr_url,
        task_type="review",
        status=status,
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:01:00Z",
        current_phase="review",
        rc=None,
        log_path=None,
        links={},
        artifacts={},
        age_s=12.5,
        is_stale=False,
    )


def _run_row(
    run_id: str = "run-1",
    status: str = "running",
    task_type: str = "sync-review-all",
) -> RunRow:
    return RunRow(
        run_id=run_id,
        task_type=task_type,
        status=status,
        started_by="tui",
        runner="claude",
        parallel=None,
        selected=None,
        started_at="2026-05-22T14:00:00Z",
        updated_at="2026-05-22T14:01:00Z",
        completed_at=None,
        run_dir=None,
        links={},
        steps=[],
        results=[],
        artifacts={},
        workers=[],
    )


def _plan_with_2_ok_3_pending() -> SyncPlanSnapshot:
    return SyncPlanSnapshot(
        queue="/tmp/q.json5",
        started_at="2026-05-22T14:00:00Z",
        updated_at="2026-05-22T14:01:00Z",
        completed_at=None,
        rc=None,
        steps=[
            SyncPlanStep("pr-scan", "ok", 0, "2026-05-22T14:00:00Z", "2026-05-22T14:00:42Z"),
            SyncPlanStep("pr-queue update", "ok", 0, "2026-05-22T14:00:42Z", "2026-05-22T14:01:20Z"),
            SyncPlanStep("step-c", "pending", None, None, None),
            SyncPlanStep("step-d", "pending", None, None, None),
            SyncPlanStep("step-e", "pending", None, None, None),
        ],
    )


def test_activity_pane_composes_without_error() -> None:
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(ActivityPane)

    asyncio.run(_run())


# --- update_workers / update_runs / update_plan are now no-ops ---

def test_update_workers_is_noop() -> None:
    """update_workers no longer renders anything — call must not raise."""
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.update_workers([_worker()])
            pane.update_workers([])
            await pilot.pause()

    asyncio.run(_run())


def test_update_runs_is_noop() -> None:
    """update_runs no longer renders anything — call must not raise."""
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.update_runs([_run_row()])
            pane.update_runs([])
            await pilot.pause()

    asyncio.run(_run())


def test_update_plan_is_noop() -> None:
    """update_plan no longer renders anything — call must not raise."""
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.update_plan(_plan_with_2_ok_3_pending())
            pane.update_plan(None)
            await pilot.pause()

    asyncio.run(_run())


def test_write_appends_to_log_section() -> None:
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.write("hello")
            await pilot.pause()
            assert "hello" in _log_text(app)

    asyncio.run(_run())


def test_write_multiple_calls_preserve_order() -> None:
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.write("first")
            pane.write("second")
            pane.write("third")
            await pilot.pause()
            text = _log_text(app)
            assert text.index("first") < text.index("second") < text.index("third")

    asyncio.run(_run())


def test_write_past_buffer_cap_drops_oldest() -> None:
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            cap = ActivityPane.LOG_BUFFER_LINES
            for i in range(cap + 1):
                pane.write(f"line-{i}")
            await pilot.pause()
            text = _log_text(app)
            assert "line-0" not in text
            assert f"line-{cap}" in text

    asyncio.run(_run())


def test_clear_log_empties_log_section() -> None:
    app = _Harness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.write("some log line")
            await pilot.pause()
            pane.clear_log()
            await pilot.pause()
            text = _log_text(app)
            assert "some log line" not in text
            assert "(no log output)" in text

    asyncio.run(_run())
