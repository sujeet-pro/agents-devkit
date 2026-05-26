from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Static, TextArea


class FindingsEditScreen(ModalScreen[str | None]):
    """Multiline text editor for a single finding body + suggestion.

    Dismissed with the edited text on Save, or None on Cancel.
    """

    BINDINGS = [
        Binding("escape", "cancel", show=False),
        Binding("ctrl+s", "save", show=False),
    ]

    DEFAULT_CSS = """
    FindingsEditScreen {
        align: center middle;
    }
    FindingsEditScreen > Container {
        width: 95%;
        height: 80%;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    FindingsEditScreen .fe-title {
        text-style: bold;
        padding-bottom: 1;
        width: 100%;
    }
    FindingsEditScreen TextArea {
        width: 100%;
        height: 1fr;
    }
    FindingsEditScreen .fe-buttons {
        height: 3;
        layout: horizontal;
        align: right middle;
        padding-top: 1;
    }
    FindingsEditScreen .fe-hint {
        color: $text-muted;
        padding-top: 1;
        width: 100%;
    }
    """

    def __init__(self, *, title: str, body: str) -> None:
        super().__init__()
        self._title = title
        self._initial_body = body

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(self._title, classes="fe-title", markup=False)
            yield TextArea(self._initial_body, id="fe-editor", language=None)
            yield Static(
                "ctrl+s to save · escape to cancel",
                classes="fe-hint",
                markup=False,
            )
            with Container(classes="fe-buttons"):
                yield Button("Save", id="fe-save", variant="primary")
                yield Button("Cancel", id="fe-cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fe-save":
            self.action_save()
        elif event.button.id == "fe-cancel":
            self.action_cancel()

    def action_save(self) -> None:
        editor = self.query_one("#fe-editor", TextArea)
        self.dismiss(editor.text)

    def action_cancel(self) -> None:
        self.dismiss(None)
