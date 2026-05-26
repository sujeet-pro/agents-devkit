"""Confirmation modal for removing a PR row from the queue."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


class RemovePrConfirmScreen(ModalScreen[bool]):
    """Dismiss with True on `y`; False on `n` / `escape`."""

    BINDINGS = [
        Binding("y", "yes", show=False),
        Binding("n", "no", show=False),
        Binding("escape", "no", show=False),
    ]

    DEFAULT_CSS = """
    RemovePrConfirmScreen {
        align: center middle;
    }
    RemovePrConfirmScreen > Container {
        width: 70;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    RemovePrConfirmScreen Static {
        width: 100%;
    }
    """

    def __init__(self, *, pr_url: str, label: str) -> None:
        super().__init__()
        self._pr_url = pr_url
        self._label = label

    def compose(self) -> ComposeResult:
        body = (
            f"Remove PR from queue?\n\n"
            f"  {self._label}\n\n"
            f"This only removes the row from the local queue. It does NOT close or\n"
            f"delete the PR on the host.\n\n"
            f"  [y]  remove\n"
            f"  [n / esc]  cancel"
        )
        with Container():
            yield Static(body, markup=False)

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)
