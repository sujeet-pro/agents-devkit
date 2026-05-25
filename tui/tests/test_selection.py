"""Legacy selection tests — multi-select removed; verify space is inert."""
from __future__ import annotations

import asyncio
from pathlib import Path

from tui.app import AdkApp


def test_space_does_not_toggle_selection(eligible_multi_queue: Path) -> None:
    app = AdkApp(queue_path=eligible_multi_queue, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert not hasattr(app, "_selection_order")
            await pilot.press("space")
            await pilot.pause()
            work_states = app._work_queue.all_states()
            assert work_states == {}

    asyncio.run(_run())
