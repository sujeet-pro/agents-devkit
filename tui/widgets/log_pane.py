from __future__ import annotations

from textual.widgets import RichLog


class LogPane(RichLog):
    """Streaming output pane for `adk pr-sync` stdout. Use `.write(line)`
    directly; convention is `$ ` prefix for shell commands, `(...)` for
    meta-lines like exit/error/already-running."""

    def __init__(self) -> None:
        super().__init__(highlight=False, markup=False, wrap=False, auto_scroll=True)
