"""Tests for the 'x' → action_remove_pr flow."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from tui.app import AdkApp
from tui.screens.remove_pr_screen import RemovePrConfirmScreen
from tui.widgets.detail_pane import TabbedDetailPane


_PR_URL = "https://github.com/foo/bar/pull/200"


def _log_text(app: AdkApp) -> str:
    try:
        tdp = app.screen_stack[0].query_one(TabbedDetailPane)
        return "\n".join(tdp.activity_pane()._log_buffer)
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


def _make_queue(tmp_path: Path, *, pr_url: str = _PR_URL) -> Path:
    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": [{
        "pr_url": pr_url,
        "status": "pending",
        "prep_status": "ready",
        "head_sha": "abc0001",
        "prep_head_sha": "abc0001",
        "last_reviewed_head_sha": "abc0002",
        "last_reviewed_at": "2026-05-19T10:00:00Z",
        "taken_at": None,
        "title": "test PR",
        "author": "alice",
    }]}))
    return q


# ---------------------------------------------------------------------------
# No-row guard: pressing x with nothing selected must log and not crash
# ---------------------------------------------------------------------------

def test_x_with_no_selection_logs_and_does_not_crash(fake_plan_path, tmp_path):
    q = tmp_path / "empty.json5"
    q.write_text(json.dumps({"prs": []}))
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            await pilot.pause()
            log = _log_text(app)
            assert "no row selected" in log
            assert not any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Pressing x with a row selected pushes RemovePrConfirmScreen
# ---------------------------------------------------------------------------

def test_x_with_selection_pushes_confirm_screen(fake_plan_path, tmp_path):
    q = _make_queue(tmp_path)
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            ok = await _poll_until(
                lambda: any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "RemovePrConfirmScreen did not appear after pressing x"

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Confirming with y removes the row from the queue file
# ---------------------------------------------------------------------------

def test_x_confirm_y_removes_row_from_queue(fake_plan_path, tmp_path):
    q = _make_queue(tmp_path)
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            ok = await _poll_until(
                lambda: any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "RemovePrConfirmScreen did not appear"
            await pilot.press("y")
            ok2 = await _poll_until(
                lambda: "removed" in _log_text(app),
                pilot=pilot,
            )
            assert ok2, f"removal log not found; log={_log_text(app)}"

    asyncio.run(_run())

    queue_data = json.loads(q.read_text())
    remaining = [e["pr_url"] for e in queue_data.get("prs", [])]
    assert _PR_URL not in remaining, "Row was not removed from queue file"


# ---------------------------------------------------------------------------
# Cancelling with n closes the modal without removing the row
# ---------------------------------------------------------------------------

def test_x_cancel_n_does_not_remove_row(fake_plan_path, tmp_path):
    q = _make_queue(tmp_path)
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            ok = await _poll_until(
                lambda: any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "RemovePrConfirmScreen did not appear"
            await pilot.press("n")
            await pilot.pause()
            assert not any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack), (
                "RemovePrConfirmScreen should be dismissed after n"
            )
            assert "removed" not in _log_text(app)

    asyncio.run(_run())

    queue_data = json.loads(q.read_text())
    remaining = [e["pr_url"] for e in queue_data.get("prs", [])]
    assert _PR_URL in remaining, "Row must not have been removed after cancel"


# ---------------------------------------------------------------------------
# Cancelling with escape also closes modal without removing
# ---------------------------------------------------------------------------

def test_x_cancel_escape_does_not_remove_row(fake_plan_path, tmp_path):
    q = _make_queue(tmp_path)
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            ok = await _poll_until(
                lambda: any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "RemovePrConfirmScreen did not appear"
            await pilot.press("escape")
            await pilot.pause()
            assert not any(isinstance(s, RemovePrConfirmScreen) for s in app.screen_stack), (
                "RemovePrConfirmScreen should be dismissed after escape"
            )

    asyncio.run(_run())

    queue_data = json.loads(q.read_text())
    remaining = [e["pr_url"] for e in queue_data.get("prs", [])]
    assert _PR_URL in remaining, "Row must not have been removed after escape"
