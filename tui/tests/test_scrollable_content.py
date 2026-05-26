"""Tests that the PR list and tab contents are scrollable.

Scrollability matters when content exceeds the available viewport — long
findings markdown, many comments, or a long PR queue should not get clipped
silently. We rely on:

- ``VerticalScroll`` wrappers around each tab's content (Overview / Review /
  Comments). The Activity tab manages its own internal scroll.
- ``DataTable``'s built-in scrolling for the PR queue.

The checks here are structural (the wrappers exist) and functional (long
content produces a virtual size taller than the viewport).
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from textual.containers import VerticalScroll
from textual.widgets import Markdown

from tui.widgets.detail_pane import TabbedDetailPane


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    monkeypatch.setenv("ADK_DATA_HOME", str(data))
    return cfg


def test_overview_tab_wrapped_in_vertical_scroll(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            scroll = app.query_one("#overview-scroll", VerticalScroll)
            assert scroll is not None

    asyncio.run(_run())


def test_review_tab_wrapped_in_vertical_scroll(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            scroll = app.query_one("#review-scroll", VerticalScroll)
            assert scroll is not None

    asyncio.run(_run())


def test_comments_tab_wrapped_in_vertical_scroll(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            scroll = app.query_one("#comments-scroll", VerticalScroll)
            assert scroll is not None

    asyncio.run(_run())


def test_tab_scroll_wrappers_are_vertical_scroll_containers(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """The Comments and Review tab content must be wrapped in VerticalScroll
    so long markdown can scroll. Activity has its own internal scroll
    (see ActivityPane); Overview is short by design but still wrapped for
    consistency. Markdown's auto-height inside a VerticalScroll is the
    mechanism that produces a scrollable viewport at runtime."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.pause()
            # Each wrapper exists, and the Markdown lives inside it.
            comments_scroll = app.query_one("#comments-scroll", VerticalScroll)
            comments_md = app.query_one("#detail-comments", Markdown)
            review_scroll = app.query_one("#review-scroll", VerticalScroll)
            review_md = app.query_one("#detail-review", Markdown)

            # The Markdown widget is a descendant of the scroll wrapper.
            assert comments_md in comments_scroll.walk_children(), (
                "#detail-comments must be inside #comments-scroll"
            )
            assert review_md in review_scroll.walk_children(), (
                "#detail-review must be inside #review-scroll"
            )

    asyncio.run(_run())


def test_queue_table_scrolls_when_rows_exceed_height(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The PR queue must scroll when row count exceeds the viewport height."""
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    monkeypatch.setenv("ADK_DATA_HOME", str(data))

    queue_path = tmp_path / "pr-queue.json5"
    prs = []
    for i in range(60):
        prs.append({
            "pr_url": f"https://github.com/acme/foo/pull/{1000 + i}",
            "status": "pending",
            "prep_status": "ready",
            "head_sha": f"abc{i:08x}{'0' * 32}"[:40],
            "last_reviewed_head_sha": None,
            "target_branch": "main",
            "last_checked_at": "2026-05-26T12:00:00Z",
            "title": f"PR #{i}",
            "author": f"user{i}",
        })
    queue_path.write_text(
        json.dumps({"filters": None, "prs": prs}, indent=2), encoding="utf-8"
    )

    from tui.app import AdkApp
    from tui.widgets.queue_table import QueueTable
    app = AdkApp(queue_path=queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 20)) as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            # With 60 rows and a 20-row terminal (minus header/footer/splitter/tabs),
            # the data viewport is well under 60 → must overflow.
            assert table.virtual_size.height > table.size.height, (
                f"queue table should overflow with 60 rows; "
                f"virtual={table.virtual_size.height} viewport={table.size.height}"
            )

    asyncio.run(_run())
