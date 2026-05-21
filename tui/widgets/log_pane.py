from __future__ import annotations

from textual.widgets import RichLog


class LogPane(RichLog):
    """Streaming output pane for `adk pr-sync` stdout."""

    def __init__(self) -> None:
        super().__init__(highlight=False, markup=False, wrap=False, auto_scroll=True)

    def announce(self, msg: str) -> None:
        self.write(msg)
