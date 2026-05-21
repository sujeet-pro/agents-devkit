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
        selected_count: int = 0,
        parallel_n: int = 4,
    ) -> None:
        sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
        review_label = "[r] review (running…)" if review_running else "[r] review"
        sel_label = f"sel:{selected_count}" if selected_count else "sel:0"
        par_label = f"par:{parallel_n}"
        text = (
            f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
            f"  [j/k] nav  [q] quit"
            f"  ·  {sync_label}  {review_label}  [R] run-sel  [space] sel  [p] par"
            f"  ·  {sel_label}  {par_label}"
        )
        self.update(text)
