from __future__ import annotations

from textual.widgets import Static


class FooterBar(Static):
    def __init__(self) -> None:
        super().__init__("", markup=False)

    def update_status(
        self,
        filter_mode: str,
        sort_mode: str,
        *,
        sync_running: bool = False,
        review_running: bool = False,
    ) -> None:
        sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
        review_label = "[r] review (running…)" if review_running else "[r] review"
        text = (
            f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
            f"  [j/k] nav  [q] quit  ·  {sync_label}  {review_label}"
        )
        self.update(text)
