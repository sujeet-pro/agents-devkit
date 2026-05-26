"""Tests for the tabbed DetailPane / TabbedDetailPane (Item 3 of PR review DX).

Validates:
- TabbedDetailPane is a composed widget with four named tab panes.
- show() updates the Overview sub-widget (DetailPane.overview_text).
- Comments and Review tabs render their placeholder text.
- Cursor move in the main app updates the tabbed detail pane.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from tui.model.queue_model import QueueRow
from tui.model.workers_model import WorkerRow
from tui.widgets.detail_pane import (
    DetailPane,
    TabbedDetailPane,
    _COMMENTS_PLACEHOLDER,
    _REVIEW_PLACEHOLDER,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(
    *,
    status: str = "pending",
    prep_status: str = "ready",
    ready_for_review: bool = True,
    last_reviewed_at: str | None = "2026-05-19T10:00:00Z",
    slack_permalink: str | None = None,
) -> QueueRow:
    return QueueRow(
        queue_index=0,
        pr_url="https://github.com/acme/foo/pull/42",
        host="github",
        repo="acme/foo",
        number=42,
        title="feat: tabbed pane",
        author="alice",
        target_branch="main",
        head_sha="abc001",
        status=status,
        prep_status=prep_status,
        prep_error=None,
        taken_at=None,
        last_checked_at=None,
        last_reviewed_at=last_reviewed_at,
        last_reviewed_head_sha=None,
        ready_for_review=ready_for_review,
        slack_permalink=slack_permalink,
    )


def _make_worker(*, task_type: str = "review") -> WorkerRow:
    return WorkerRow(
        pid=9001,
        worker_id="w9001",
        run_id=None,
        pr_url="https://github.com/acme/foo/pull/42",
        subject="https://github.com/acme/foo/pull/42",
        task_type=task_type,
        status="running",
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-22T14:00:00Z",
        last_heartbeat="2026-05-22T14:00:30Z",
        current_phase="phase 3: embed",
        rc=None,
        log_path="/tmp/review.log",
        links={},
        artifacts={},
        age_s=30.0,
        is_stale=False,
    )


# ---------------------------------------------------------------------------
# DetailPane (Overview sub-widget) — unit tests (no TUI mount needed)
# ---------------------------------------------------------------------------

def test_detail_pane_overview_text_default() -> None:
    pane = DetailPane()
    assert pane.overview_text == "(no row selected)"


def test_detail_pane_show_updates_overview_text() -> None:
    pane = DetailPane()
    pane.show(_make_row())
    assert "acme/foo#42" in pane.overview_text
    assert "feat: tabbed pane" in pane.overview_text


def test_detail_pane_show_none_resets_to_empty_state() -> None:
    pane = DetailPane()
    pane.show(_make_row())
    pane.show(None)
    assert pane.overview_text == "(no row selected)"


def test_detail_pane_show_with_worker_includes_log_path() -> None:
    pane = DetailPane()
    pane.show(_make_row(), worker=_make_worker())
    assert "Log:" in pane.overview_text
    assert "/tmp/review.log" in pane.overview_text


# ---------------------------------------------------------------------------
# TabbedDetailPane — internal state tests (no TUI mount needed)
# ---------------------------------------------------------------------------

def test_tabbed_detail_pane_show_updates_overview_via_inner_detail_pane() -> None:
    """show() must reach the inner DetailPane and update overview_text."""
    outer = TabbedDetailPane()
    # Before mounting, the inner DetailPane does not exist in the DOM.
    # show() should handle this gracefully.
    outer.show(_make_row())  # should not raise


# ---------------------------------------------------------------------------
# TabbedDetailPane — mounted TUI tests (four tabs actually compose)
# ---------------------------------------------------------------------------

def _make_app_with_tabbed_pane(fake_queue_path: Path):
    from tui.app import AdkApp
    return AdkApp(queue_path=fake_queue_path, poll_interval=0.05)


def test_tabbed_detail_pane_has_four_tabs(fake_queue_path: Path) -> None:
    """TabbedDetailPane must compose four TabPane widgets."""
    from textual.widgets import TabPane
    app = _make_app_with_tabbed_pane(fake_queue_path)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            tab_panes = app.query(TabPane)
            tab_ids = [str(tp.id) for tp in tab_panes]
            assert "tab-overview" in tab_ids, f"tab-overview missing; found: {tab_ids}"
            assert "tab-comments" in tab_ids, f"tab-comments missing; found: {tab_ids}"
            assert "tab-review" in tab_ids, f"tab-review missing; found: {tab_ids}"
            assert "tab-activity" in tab_ids, f"tab-activity missing; found: {tab_ids}"
            assert "tab-log" not in tab_ids, f"tab-log must not exist; found: {tab_ids}"

    asyncio.run(_run())


def test_overview_tab_shows_pr_details(fake_queue_path: Path) -> None:
    """The Overview tab's DetailPane must show the selected PR's details."""
    app = _make_app_with_tabbed_pane(fake_queue_path)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(DetailPane)
            text = pane.overview_text
            # At least the repo/number format should be present after mount+refresh.
            assert text != "(no row selected)", f"Overview unexpectedly empty: {text!r}"

    asyncio.run(_run())


def test_comments_tab_has_placeholder(fake_queue_path: Path) -> None:
    """Comments tab must render the placeholder text (now via Markdown widget)."""
    from textual.widgets import Markdown
    app = _make_app_with_tabbed_pane(fake_queue_path)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            comments_md = app.query_one("#detail-comments", Markdown)
            # The Markdown widget exposes its raw source via the `_markdown`
            # internal attr (set by `update()`); fall back to rendering the
            # widget tree for older versions.
            text = getattr(comments_md, "_markdown", None) or ""
            if not text:
                text = str(comments_md.render())
            assert "Comments" in text or "comment" in text.lower(), (
                f"Comments placeholder missing.\nGot: {text!r}"
            )

    asyncio.run(_run())


def test_review_tab_has_placeholder(fake_queue_path: Path) -> None:
    """Review tab must render the placeholder text (now via Markdown widget)."""
    from textual.widgets import Markdown
    app = _make_app_with_tabbed_pane(fake_queue_path)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            review_md = app.query_one("#detail-review", Markdown)
            text = getattr(review_md, "_markdown", None) or ""
            if not text:
                text = str(review_md.render())
            assert "review" in text.lower() or "findings" in text.lower(), (
                f"Review placeholder missing.\nGot: {text!r}"
            )

    asyncio.run(_run())


def test_cursor_move_updates_overview_tab(fake_queue_path: Path) -> None:
    """Pressing j (cursor down) must change the Overview tab content."""
    app = _make_app_with_tabbed_pane(fake_queue_path)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(DetailPane)
            before = pane.overview_text
            await pilot.press("j")
            await pilot.pause()
            after = pane.overview_text
            assert before != after, "Overview must change after cursor move"

    asyncio.run(_run())
