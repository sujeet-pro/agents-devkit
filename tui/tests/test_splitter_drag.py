"""Tests for the mouse-draggable SplitterHandle.

The drag flow is: ``MouseDown`` captures the mouse; subsequent ``MouseMove``
events emit :class:`SplitterHandle.Dragged` with screen-coord deltas. The app
translates each vertical delta into a new ``split_percent`` (clamped) and
re-applies layout live. ``MouseUp`` emits :class:`SplitterHandle.Released`
and the app persists the final ratio to the sidecar.

The layout is always stacked (vertical motion only). Horizontal deltas are
ignored.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from tui.widgets.splitter_handle import SplitterHandle


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    monkeypatch.setenv("ADK_DATA_HOME", str(data))
    return cfg


def test_splitter_present_between_queue_and_tabs(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """The SplitterHandle widget must be mounted in the main container."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            splitter = app.query_one(SplitterHandle)
            assert splitter is not None

    asyncio.run(_run())


def test_drag_downward_increases_queue_share(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Dragging the handle downward (positive delta_y) grows the queue's share."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            before = app._layout_prefs.split_percent
            splitter = app.query_one(SplitterHandle)
            splitter.post_message(SplitterHandle.Dragged(0, 8))
            await pilot.pause()
            assert app._layout_prefs.split_percent > before

    asyncio.run(_run())


def test_drag_upward_shrinks_queue(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Dragging up shrinks the queue's share."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            before = app._layout_prefs.split_percent
            splitter = app.query_one(SplitterHandle)
            splitter.post_message(SplitterHandle.Dragged(0, -8))
            await pilot.pause()
            assert app._layout_prefs.split_percent < before

    asyncio.run(_run())


def test_horizontal_drag_delta_is_ignored(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """A purely horizontal drag (delta_x only, delta_y=0) has no effect."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            before = app._layout_prefs.split_percent
            splitter = app.query_one(SplitterHandle)
            splitter.post_message(SplitterHandle.Dragged(50, 0))
            await pilot.pause()
            assert app._layout_prefs.split_percent == before

    asyncio.run(_run())


def test_release_persists_to_sidecar(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Drag deltas only persist on Released — one disk write per drag, not per pixel."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            splitter = app.query_one(SplitterHandle)
            splitter.post_message(SplitterHandle.Dragged(0, 6))
            await pilot.pause()
            prefs_path = isolated_config / "tui-prefs.json"
            assert not prefs_path.exists(), (
                "drag deltas must not persist; only Released persists"
            )
            splitter.post_message(SplitterHandle.Released())
            await pilot.pause()
            assert prefs_path.exists()
            saved = json.loads(prefs_path.read_text(encoding="utf-8"))
            assert saved.get("split_percent") == app._layout_prefs.split_percent

    asyncio.run(_run())


def test_drag_clamped_to_min_max(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """A huge drag delta is clamped to the [MIN, MAX] window."""
    from tui.app import AdkApp
    from tui.model.prefs import MAX_SPLIT_PERCENT, MIN_SPLIT_PERCENT
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            splitter = app.query_one(SplitterHandle)
            splitter.post_message(SplitterHandle.Dragged(0, 9999))
            await pilot.pause()
            assert app._layout_prefs.split_percent == MAX_SPLIT_PERCENT
            splitter.post_message(SplitterHandle.Dragged(0, -9999))
            await pilot.pause()
            assert app._layout_prefs.split_percent == MIN_SPLIT_PERCENT

    asyncio.run(_run())
