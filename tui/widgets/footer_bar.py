from __future__ import annotations

from textual.widgets import Static


class FooterBar(Static):
    def __init__(self) -> None:
        super().__init__("", markup=False)

    def update_status(self, filter_mode: str, sort_mode: str) -> None:
        text = (
            f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
            f"  [j/k] nav  [q] quit  ·  [s] sync (disabled)  [r] run (disabled)"
        )
        self.update(text)
