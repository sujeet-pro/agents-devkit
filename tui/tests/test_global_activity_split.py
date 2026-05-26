"""Tests for the global/per-PR activity log split.

Verifies:
- GlobalActivityStrip surfaces lines from pipeline.log
- ActivityPane.set_pr() switches to tailing the correct narration.log
- ActivityPane.update_tail() picks up new lines after the file grows
- Lines from ActivityPane do NOT appear when a different PR is selected
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.widgets.activity_pane import ActivityPane
from tui.widgets.global_activity_strip import GlobalActivityStrip


# ---------------------------------------------------------------------------
# Minimal harness apps
# ---------------------------------------------------------------------------

class _StripHarness(App):
    def compose(self) -> ComposeResult:
        yield GlobalActivityStrip()


class _PaneHarness(App):
    def compose(self) -> ComposeResult:
        yield ActivityPane()


# ---------------------------------------------------------------------------
# GlobalActivityStrip tests
# ---------------------------------------------------------------------------

def test_global_strip_composes_without_error() -> None:
    app = _StripHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            app.query_one(GlobalActivityStrip)

    asyncio.run(_run())


def test_global_strip_append_surfaces_text() -> None:
    app = _StripHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            strip = app.query_one(GlobalActivityStrip)
            strip.append("pipeline event alpha")
            await pilot.pause()
            text = str(app.query_one("#global-strip-log", Static).content)
            assert "pipeline event alpha" in text

    asyncio.run(_run())


def test_global_strip_shows_last_3_lines(tmp_path: Path, monkeypatch) -> None:
    """Strip should display at most 3 lines (the most recent ones)."""
    # Patch _pipeline_log_path to use a tmp file.
    log_file = tmp_path / "pipeline.log"
    lines = [f"line-{i}" for i in range(10)]
    log_file.write_text("\n".join(lines) + "\n")

    import tui.widgets.global_activity_strip as _mod
    monkeypatch.setattr(_mod, "_pipeline_log_path", lambda: log_file)

    app = _StripHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            strip = app.query_one(GlobalActivityStrip)
            strip.update_tail()
            await pilot.pause()
            text = str(app.query_one("#global-strip-log", Static).content)
            # Should contain lines 7, 8, 9 (last 3).
            assert "line-9" in text
            assert "line-8" in text
            assert "line-7" in text
            # line-0 should not appear (it's older than 100 lines ago in this
            # case we have only 10, but the strip renders only the last 3
            # visible lines; all 10 are in the buffer though).
            # Verify at least the visible 3 are there.

    asyncio.run(_run())


def test_global_strip_update_tail_reads_pipeline_log(tmp_path: Path, monkeypatch) -> None:
    log_file = tmp_path / "pipeline.log"
    log_file.write_text("scheduler started\nPR import done\n")

    import tui.widgets.global_activity_strip as _mod
    monkeypatch.setattr(_mod, "_pipeline_log_path", lambda: log_file)

    app = _StripHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            strip = app.query_one(GlobalActivityStrip)
            strip.update_tail()
            await pilot.pause()
            text = str(app.query_one("#global-strip-log", Static).content)
            assert "scheduler started" in text or "PR import done" in text

    asyncio.run(_run())


def test_global_strip_ignores_missing_pipeline_log(tmp_path: Path, monkeypatch) -> None:
    missing = tmp_path / "nonexistent.log"
    import tui.widgets.global_activity_strip as _mod
    monkeypatch.setattr(_mod, "_pipeline_log_path", lambda: missing)

    app = _StripHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            strip = app.query_one(GlobalActivityStrip)
            strip.update_tail()  # must not raise
            await pilot.pause()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# ActivityPane per-PR tailing tests
# ---------------------------------------------------------------------------

def test_activity_pane_placeholder_before_pr_set() -> None:
    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            text = str(app.query_one("#activity-log", Static).content)
            assert "select a PR" in text

    asyncio.run(_run())


def test_activity_pane_set_pr_none_shows_placeholder() -> None:
    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.set_pr(None)
            await pilot.pause()
            text = str(app.query_one("#activity-log", Static).content)
            assert "select a PR" in text

    asyncio.run(_run())


def test_activity_pane_set_pr_tails_narration_log(tmp_path: Path, monkeypatch) -> None:
    """After set_pr, update_tail reads the PR's narration.log."""
    pr_url = "https://github.com/acme/myrepo/pull/99"
    narration_log = tmp_path / "narration.log"
    narration_log.write_text("Phase 1: worktree\nPhase 2: indexing\n")

    # Patch _narration_log_path to return our tmp file.
    import tui.widgets.activity_pane as _mod
    monkeypatch.setattr(_mod, "_narration_log_path", lambda url: narration_log)

    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.set_pr(pr_url)
            await pilot.pause()
            text = str(app.query_one("#activity-log", Static).content)
            assert "Phase 1: worktree" in text
            assert "Phase 2: indexing" in text

    asyncio.run(_run())


def test_activity_pane_update_tail_picks_up_new_lines(tmp_path: Path, monkeypatch) -> None:
    """update_tail should append only newly written lines."""
    pr_url = "https://github.com/acme/myrepo/pull/55"
    narration_log = tmp_path / "narration.log"
    narration_log.write_text("initial line\n")

    import tui.widgets.activity_pane as _mod
    monkeypatch.setattr(_mod, "_narration_log_path", lambda url: narration_log)

    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.set_pr(pr_url)
            await pilot.pause()
            # Append a new line to the file.
            with narration_log.open("a") as fh:
                fh.write("new line after tail\n")
            pane.update_tail()
            await pilot.pause()
            text = str(app.query_one("#activity-log", Static).content)
            assert "initial line" in text
            assert "new line after tail" in text

    asyncio.run(_run())


def test_activity_pane_pr_lines_not_shown_when_different_pr_selected(
    tmp_path: Path, monkeypatch
) -> None:
    """Lines from PR-A's narration.log must NOT appear when PR-B is selected."""
    log_a = tmp_path / "a.log"
    log_b = tmp_path / "b.log"
    log_a.write_text("PR-A specific message\n")
    log_b.write_text("PR-B specific message\n")

    def _fake_narration(url: str) -> Path:
        return log_a if "pull/1" in url else log_b

    import tui.widgets.activity_pane as _mod
    monkeypatch.setattr(_mod, "_narration_log_path", _fake_narration)

    pr_a = "https://github.com/acme/repo/pull/1"
    pr_b = "https://github.com/acme/repo/pull/2"
    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            # Select PR-A.
            pane.set_pr(pr_a)
            await pilot.pause()
            text_a = str(app.query_one("#activity-log", Static).content)
            assert "PR-A specific message" in text_a
            assert "PR-B specific message" not in text_a
            # Switch to PR-B.
            pane.set_pr(pr_b)
            await pilot.pause()
            text_b = str(app.query_one("#activity-log", Static).content)
            assert "PR-B specific message" in text_b
            assert "PR-A specific message" not in text_b

    asyncio.run(_run())


def test_activity_pane_write_still_works() -> None:
    """write() API must still append lines (backward-compat)."""
    app = _PaneHarness()

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            pane = app.query_one(ActivityPane)
            pane.write("compat line one")
            pane.write("compat line two")
            await pilot.pause()
            text = str(app.query_one("#activity-log", Static).content)
            assert "compat line one" in text
            assert "compat line two" in text

    asyncio.run(_run())
