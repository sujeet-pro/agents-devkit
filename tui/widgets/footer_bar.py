from __future__ import annotations

from textual.widgets import Static


class FooterBar(Static):
    """Minimal footer: [?]help  [q]quit  — always visible at the bottom."""

    def __init__(self) -> None:
        super().__init__("[?]help  [q]quit", markup=False)

    def update_status(self, *args, **kwargs) -> None:
        pass
