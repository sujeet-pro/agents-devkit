r"""Tests for the user-controlled split layout.

The TUI no longer auto-switches layout by terminal width. Instead the user
pins direction (horizontal | vertical) and split percent via:
  - `\` to toggle direction
  - `[` / `]` to shrink / grow the queue's share
  - `=` to reset to 50/50

Preferences persist to `$ADK_CONFIG_HOME/tui-prefs.json`.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from tui.widgets.queue_table import QueueTable, _ALL_COLUMN_NAMES
from tui.widgets.detail_pane import TabbedDetailPane


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect $ADK_CONFIG_HOME to a tmp dir so prefs reads/writes are isolated."""
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    data = tmp_path / "data"
    data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    monkeypatch.setenv("ADK_DATA_HOME", str(data))
    return cfg


def test_queue_table_always_uses_all_columns(fake_queue_path: Path) -> None:
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            assert table._current_column_set == _ALL_COLUMN_NAMES

    asyncio.run(_run())


def test_default_layout_horizontal_50_50(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """With no prefs file, default to horizontal (stacked) at 50/50."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.direction == "horizontal"
            assert app._layout_prefs.split_percent == 50

    asyncio.run(_run())


def test_toggle_direction_persists(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Pressing `\\` flips direction and saves to tui-prefs.json."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.direction == "horizontal"
            await pilot.press("backslash")
            await pilot.pause()
            assert app._layout_prefs.direction == "vertical"

            # Persisted to sidecar.
            prefs_path = isolated_config / "tui-prefs.json"
            assert prefs_path.exists(), "tui-prefs.json must be written on toggle"
            saved = json.loads(prefs_path.read_text(encoding="utf-8"))
            assert saved.get("layout") == "vertical"
            assert saved.get("split_percent") == 50

    asyncio.run(_run())


def test_grow_queue_adjusts_split(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Pressing `]` grows the queue's share by ADJUST_STEP."""
    from tui.app import AdkApp
    from tui.model.prefs import ADJUST_STEP
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            start = app._layout_prefs.split_percent
            await pilot.press("right_square_bracket")
            await pilot.pause()
            assert app._layout_prefs.split_percent == start + ADJUST_STEP

    asyncio.run(_run())


def test_shrink_queue_adjusts_split(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Pressing `[` shrinks the queue's share by ADJUST_STEP."""
    from tui.app import AdkApp
    from tui.model.prefs import ADJUST_STEP
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            start = app._layout_prefs.split_percent
            await pilot.press("left_square_bracket")
            await pilot.pause()
            assert app._layout_prefs.split_percent == start - ADJUST_STEP

    asyncio.run(_run())


def test_reset_split_to_50(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Pressing `=` resets the split to 50/50 (direction unchanged)."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await pilot.press("right_square_bracket")  # 50 → 55
            await pilot.press("right_square_bracket")  # 55 → 60
            await pilot.pause()
            assert app._layout_prefs.split_percent == 60
            await pilot.press("equals_sign")
            await pilot.pause()
            assert app._layout_prefs.split_percent == 50

    asyncio.run(_run())


def test_split_clamped_to_min_max(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """[ and ] are clamped to MIN/MAX_SPLIT_PERCENT — no off-by-one runaways."""
    from tui.app import AdkApp
    from tui.model.prefs import MIN_SPLIT_PERCENT, MAX_SPLIT_PERCENT
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            for _ in range(30):
                await pilot.press("right_square_bracket")
            await pilot.pause()
            assert app._layout_prefs.split_percent == MAX_SPLIT_PERCENT
            for _ in range(60):
                await pilot.press("left_square_bracket")
            await pilot.pause()
            assert app._layout_prefs.split_percent == MIN_SPLIT_PERCENT

    asyncio.run(_run())


def test_horizontal_layout_stacks_widgets(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Horizontal direction puts queue on top, tabs below — same width, sum of heights."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            tabs = app.query_one(TabbedDetailPane)
            assert table.size.width == tabs.size.width, (
                f"horizontal layout: widths must match; "
                f"queue.width={table.size.width} tabs.width={tabs.size.width}"
            )
            assert table.size.height > 0 and tabs.size.height > 0

    asyncio.run(_run())


def test_vertical_layout_places_widgets_side_by_side(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Vertical direction puts queue beside tabs — same height, sum of widths."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(160, 40)) as pilot:
            await pilot.pause()
            await pilot.press("backslash")  # horizontal → vertical
            await pilot.pause()
            table = app.query_one(QueueTable)
            tabs = app.query_one(TabbedDetailPane)
            assert table.size.height == tabs.size.height, (
                f"vertical layout: heights must match; "
                f"queue.height={table.size.height} tabs.height={tabs.size.height}"
            )
            assert table.size.width > 0 and tabs.size.width > 0

    asyncio.run(_run())


def test_prefs_loaded_from_sidecar(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """A pre-existing tui-prefs.json must be respected at startup."""
    (isolated_config / "tui-prefs.json").write_text(
        json.dumps({"layout": "vertical", "split_percent": 35}),
        encoding="utf-8",
    )
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.direction == "vertical"
            assert app._layout_prefs.split_percent == 35

    asyncio.run(_run())
