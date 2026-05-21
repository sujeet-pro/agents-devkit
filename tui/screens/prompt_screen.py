from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Static


class PromptScreen(ModalScreen[str | None]):
    """Single-input modal. dismiss() with the typed value on submit,
    dismiss(None) on cancel (escape)."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    DEFAULT_CSS = """
    PromptScreen {
        align: center middle;
    }
    PromptScreen > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    PromptScreen Static {
        width: 100%;
    }
    PromptScreen Input {
        width: 100%;
    }
    """

    def __init__(self, label: str, placeholder: str = "") -> None:
        super().__init__()
        self._label = label
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(self._label, markup=False)
            yield Input(placeholder=self._placeholder)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss(None)
