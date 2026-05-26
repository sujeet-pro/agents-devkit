from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


class PRActionBar(Static):
    """One-row bar showing PR-specific keybind chips.

    Sits below TabbedDetailPane, at the very bottom of the app.
    When no PR is selected, shows a prompt to select one.
    """

    def __init__(self) -> None:
        super().__init__("(select a PR for actions)", markup=False)

    def update_pr(self, row: "QueueRow | None") -> None:
        if row is None:
            self.update("(select a PR for actions)")
            return
        parts = [
            "[S]Sync PR",
            "[R]Sync+Rev",
            "[enter]act",
            "·",
            "[a]pprove",
            "[v]re-review",
            "[x]refresh",
            "·",
            "[m]ergeable?",
            "[M]Merge",
            "·",
            "[1-5]tab",
            "[?]help",
            "[q]quit",
        ]
        self.update("  ".join(parts))
