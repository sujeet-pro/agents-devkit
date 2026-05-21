from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueSnapshot


class HeaderBar(Static):
    def __init__(self) -> None:
        super().__init__("adk", markup=False)

    def update_snapshot(self, snapshot: QueueSnapshot) -> None:
        text = (
            f"adk · queue: {snapshot.total} · ready: {snapshot.ready_count}"
            f" · in-review: {snapshot.in_review_count}/4"
            f" · platform: {snapshot.platform_summary}"
        )
        self.update(text)
