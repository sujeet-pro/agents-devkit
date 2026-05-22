from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

_HELP_TEXT = """adk TUI · keys

  q              quit
  ?              this help
  f              cycle filter
  S              cycle sort
  s              start `adk pr-sync` (streams into log pane)
  r              start a review on the highlighted row (claim+prepare+claude)
  R              run all selected rows as a batch (parallel cap)
  space          toggle selection on the highlighted row
  p              cycle parallel cap (1 → 2 → 4 → 8)
  a              pick agent (claude / codex / cursor / headless ...)
  +              add PR (modal — URL, owner/repo#N, or number)
  b              switch to repos screen (manage repos + branches)
  t              cycle theme (dark / light / nord / gruvbox / dracula)
  j / down       move cursor down
  k / up         move cursor up
  g / home       jump to first row
  G / end        jump to last row
  enter          (read-only — no action yet)
  escape         close this help
"""


class HelpScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    HelpScreen > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    HelpScreen Static {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("question_mark", "dismiss", show=False),
        Binding("escape", "dismiss", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(_HELP_TEXT, markup=False)
