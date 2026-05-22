"""Generic yes/no confirm modal. Used by the λ detach-prompt flow and
re-usable for any future "are you sure?" gate."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static


class ConfirmScreen(ModalScreen[bool]):
    """Dismiss with True on `y` / `enter`; False on `n` / `escape` / `q`."""

    BINDINGS = [
        Binding("y", "yes", show=False),
        Binding("enter", "yes", show=False),
        Binding("n", "no", show=False),
        Binding("escape", "no", show=False),
        Binding("q", "no", show=False),
    ]

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }
    ConfirmScreen > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    ConfirmScreen Static {
        width: 100%;
    }
    """

    def __init__(self, prompt: str, *, yes_label: str = "yes",
                 no_label: str = "no") -> None:
        super().__init__()
        self._prompt = prompt
        self._yes_label = yes_label
        self._no_label = no_label

    def compose(self) -> ComposeResult:
        body = (
            f"{self._prompt}\n\n"
            f"  [y / enter]  {self._yes_label}\n"
            f"  [n / esc / q]  {self._no_label}"
        )
        with Container():
            yield Static(body, markup=False)

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)
