from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.runs_model import RunRow
    from tui.model.sync_plan_model import SyncPlanSnapshot
    from tui.model.workers_model import WorkerRow


class ActivityPane(Widget):
    """Log-only activity pane for the Activity tab.

    Keeps a rolling 500-line buffer; callers write lines via write().
    The update_workers / update_runs / update_plan methods are retained as
    no-ops so app.py call sites do not need to be touched."""

    DEFAULT_CSS = """
    ActivityPane { height: 1fr; }
    ActivityPane VerticalScroll { height: 1fr; }
    ActivityPane Static { padding: 0 1; }
    ActivityPane .activity-section-header { text-style: bold; padding-top: 1; }
    ActivityPane #activity-log { background: $surface; }
    """

    LOG_BUFFER_LINES = 500

    def __init__(self) -> None:
        super().__init__()
        self._log_buffer: deque[str] = deque(maxlen=self.LOG_BUFFER_LINES)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("Log", classes="activity-section-header", markup=False)
            yield Static("(no log output)", id="activity-log", markup=False)

    # --- public API ---

    def update_workers(self, rows: "list[WorkerRow]", *, ascii_only: bool = False) -> None:
        """No-op: worker state is now reflected by the stage tab counts."""

    def update_runs(self, rows: "list[RunRow]") -> None:
        """No-op: run state is now reflected by the stage tab counts."""

    def update_plan(self, snapshot: "SyncPlanSnapshot | None", *, ascii_only: bool = False) -> None:
        """No-op: sync plan is now reflected by the stage tab counts."""

    def write(self, line: str) -> None:
        """Append a single log line."""
        self._log_buffer.append(line)
        self.query_one("#activity-log", Static).update("\n".join(self._log_buffer))

    def clear_log(self) -> None:
        """Clear the log buffer."""
        self._log_buffer.clear()
        self.query_one("#activity-log", Static).update("(no log output)")
