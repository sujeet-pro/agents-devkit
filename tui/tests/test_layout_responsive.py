r"""Tests for the user-controlled split layout.

The TUI always uses queue-on-top, detail-on-bottom. The user controls the
split ratio via:
  - `[` / `]` to shrink / grow the queue's share
  - `=` to reset to 50/50

Preferences persist to `$ADK_CONFIG_HOME/tui-prefs.json`.
A sidecar that still contains ``"layout"`` / ``"direction"`` keys is silently
accepted — backwards-compat.
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


def test_default_layout_50_50(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """With no prefs file, default to 50/50 split."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.split_percent == 50

    asyncio.run(_run())


def test_no_direction_attribute_on_prefs(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """LayoutPrefs no longer has a `direction` field."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert not hasattr(app._layout_prefs, "direction")

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
    """Pressing `=` resets the split to 50/50."""
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
    """[ and ] are clamped to MIN/MAX_SPLIT_PERCENT."""
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


def test_layout_always_stacks_widgets(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """Layout is always stacked: queue on top, tabs below — same width, sum of heights."""
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            table = app.query_one(QueueTable)
            tabs = app.query_one(TabbedDetailPane)
            assert table.size.width == tabs.size.width, (
                f"stacked layout: widths must match; "
                f"queue.width={table.size.width} tabs.width={tabs.size.width}"
            )
            assert table.size.height > 0 and tabs.size.height > 0

    asyncio.run(_run())


def test_prefs_loaded_from_sidecar(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """A pre-existing tui-prefs.json must be respected at startup."""
    (isolated_config / "tui-prefs.json").write_text(
        json.dumps({"split_percent": 35}),
        encoding="utf-8",
    )
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.split_percent == 35

    asyncio.run(_run())


def test_sidecar_with_legacy_layout_key_is_ignored(
    fake_queue_path: Path, isolated_config: Path
) -> None:
    """A sidecar that still has 'layout': 'vertical' must load without error."""
    (isolated_config / "tui-prefs.json").write_text(
        json.dumps({"layout": "vertical", "split_percent": 40}),
        encoding="utf-8",
    )
    from tui.app import AdkApp
    app = AdkApp(queue_path=fake_queue_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test(size=(140, 40)) as pilot:
            await pilot.pause()
            assert app._layout_prefs.split_percent == 40

    asyncio.run(_run())
