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
        super().__init__("(select a PR for actions)", markup=True)

    def update_pr(self, row: "QueueRow | None") -> None:
        if row is None:
            self.update("(select a PR for actions)")
            return
        parts = [
            "[u]s[/u]ync",
            "[u]r[/u]eview",
            "[u]a[/u]pprove",
            "[u]m[/u]ergeable?",
            "[u]M[/u]erge",
            "[u]u[/u]pdate",
            "[u]x[/u] remove",
            "[u]o[/u]pen",
            "[u]l[/u]ogs",
            "[enter] more",
            "·",
            "[u]f[/u]ilter",
            "[K] sort",
            "[?] help",
            "[q] quit",
        ]
        self.update("  ".join(parts))
