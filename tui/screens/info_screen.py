"""Dedicated info panel for user-requested output.

When the user explicitly requests information (e.g. merge status), the output
is shown here rather than being lost in the bottom activity log.  The log
still receives the command invocation and exit code for traceability.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static


class InfoScreen(ModalScreen[None]):
    """Display a titled, scrollable block of text in a focused modal.

    Dismissed with escape, enter, or q.
    """

    BINDINGS = [
        Binding("escape", "dismiss", show=False),
        Binding("enter", "dismiss", show=False),
        Binding("q", "dismiss", show=False),
    ]

    DEFAULT_CSS = """
    InfoScreen {
        align: center middle;
    }
    InfoScreen > Container {
        width: 90;
        max-width: 95%;
        height: auto;
        max-height: 40;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    InfoScreen Static.info-title {
        text-style: bold;
        padding-bottom: 1;
        width: 100%;
    }
    InfoScreen VerticalScroll {
        height: auto;
        max-height: 28;
        width: 100%;
    }
    InfoScreen Static.info-body {
        width: 100%;
    }
    InfoScreen Static.info-footer {
        padding-top: 1;
        width: 100%;
    }
    """

    def __init__(self, *, title: str, content: str, rc: int | None = None) -> None:
        super().__init__()
        self._title = title
        self._content = content
        self._rc = rc

    def compose(self) -> ComposeResult:
        rc_suffix = f"  (rc={self._rc})" if self._rc is not None else ""
        with Container():
            yield Static(
                f"{self._title}{rc_suffix}",
                classes="info-title",
                markup=False,
            )
            with VerticalScroll():
                yield Static(
                    self._content if self._content.strip() else "(no output)",
                    classes="info-body",
                    markup=False,
                )
            yield Static(
                "(press escape / enter / q to close)",
                classes="info-footer",
                markup=False,
            )
