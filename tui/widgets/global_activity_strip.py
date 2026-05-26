from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

_ADK_REPO_LIB = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_ADK_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_ADK_REPO_LIB))

_PIPELINE_LOG_LINES = 100
_STRIP_VISIBLE_LINES = 3
_TAIL_BYTES = 4096


def _pipeline_log_path() -> Path:
    from config import adk_data_home  # noqa: E402 (late import: path set above)
    return adk_data_home() / "logs" / "pipeline.log"


class GlobalActivityStrip(Widget):
    """3-line rolling tail of $ADK_DATA_HOME/logs/pipeline.log.

    Sits between QueueTable and QueueActionBar in the main layout.
    Updated on every TUI poll via update_tail(). Lines can also be
    injected directly via append() (for messages from app.py _log_global).
    """

    DEFAULT_CSS = """
    GlobalActivityStrip {
        height: 3;
        border-top: dashed $surface-darken-1;
        border-bottom: dashed $surface-darken-1;
        background: $surface;
        overflow: hidden;
    }
    GlobalActivityStrip Static {
        padding: 0 1;
        color: $text-muted;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._buffer: deque[str] = deque(maxlen=_PIPELINE_LOG_LINES)
        self._file_offset: int = 0

    def compose(self) -> ComposeResult:
        yield Static("", id="global-strip-log", markup=False)

    # --- public API ---

    def append(self, line: str) -> None:
        """Inject a line into the strip (called by app.py _log_global)."""
        self._buffer.append(line)
        self._refresh_static()

    def update_tail(self) -> None:
        """Re-read the tail of pipeline.log and surface new lines.

        Called by the app's periodic poll. Reads the last _TAIL_BYTES of the
        file rather than the whole thing. New-only detection is approximate:
        we track the file size and append the freshly-read lines when the file
        has grown. On truncation (log roll) we reset and re-read.
        """
        log_path = _pipeline_log_path()
        if not log_path.exists():
            return
        try:
            size = log_path.stat().st_size
            if size == self._file_offset:
                return
            if size < self._file_offset:
                # File was truncated/rotated — reset.
                self._file_offset = 0
                self._buffer.clear()
            with log_path.open("r", encoding="utf-8", errors="replace") as fh:
                seek_pos = max(0, size - _TAIL_BYTES)
                fh.seek(seek_pos)
                raw = fh.read()
            self._file_offset = size
            lines = raw.splitlines()
            # If we didn't read from the start, the first line may be partial —
            # drop it when seek_pos > 0.
            if seek_pos > 0 and lines:
                lines = lines[1:]
            for line in lines:
                if line:
                    self._buffer.append(line)
            self._refresh_static()
        except OSError:
            pass

    # --- internal ---

    def _refresh_static(self) -> None:
        visible = list(self._buffer)[-_STRIP_VISIBLE_LINES:]
        self.query_one("#global-strip-log", Static).update(
            "\n".join(visible) if visible else "(no pipeline activity)"
        )
