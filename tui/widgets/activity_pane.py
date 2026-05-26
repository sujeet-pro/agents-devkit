from __future__ import annotations

import sys
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.runs_model import RunRow
    from tui.model.sync_plan_model import SyncPlanSnapshot
    from tui.model.workers_model import WorkerRow

_ADK_REPO_LIB = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_ADK_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_ADK_REPO_LIB))

_TAIL_BYTES = 4096


def _narration_log_path(pr_url: str) -> Path | None:
    """Resolve $ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/narration.log."""
    try:
        import sys as _sys
        _scripts = Path(__file__).resolve().parents[2] / "skills" / "adk-cli" / "scripts"
        if str(_scripts) not in _sys.path:
            _sys.path.insert(0, str(_scripts))
        import queue_io as _queue_io
        from config import adk_data_home
        _host, _owner, repo, number = _queue_io.dedupe_key(pr_url)
        pr_dir = adk_data_home() / "skill-pr-review" / f"{repo}_pr-{number}"
        return pr_dir / "narration.log"
    except Exception:
        return None


class ActivityPane(Widget):
    """Log-only activity pane for the Activity tab.

    Two operating modes:

    1. No PR selected (default): shows content from _log_buffer, which is
       populated by write() calls (e.g. global operational messages from
       app.py). This preserves backward compatibility with existing tests
       that read _log_buffer to verify that operational messages appeared.

    2. PR selected (via set_pr()): shows the tail of the PR's narration.log,
       updated on every update_tail() call. The _log_buffer continues to
       receive write() calls but those writes do not update the display
       while a PR is active.

    The update_workers / update_runs / update_plan methods are retained as
    no-ops so app.py call sites do not need to be touched.
    """

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
        # Global / compat buffer — always updated by write().
        self._log_buffer: deque[str] = deque(maxlen=self.LOG_BUFFER_LINES)
        # Per-PR tail state.
        self._pr_url: str | None = None
        self._narration_path: Path | None = None
        self._narration_buffer: deque[str] = deque(maxlen=self.LOG_BUFFER_LINES)
        self._file_offset: int = 0

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("Log", classes="activity-section-header", markup=False)
            yield Static("(select a PR to see its activity)", id="activity-log", markup=False)

    # --- public API ---

    def set_pr(self, pr_url: str | None) -> None:
        """Switch to tailing the given PR's narration.log.

        Passing None returns to showing the global _log_buffer.
        """
        if pr_url == self._pr_url:
            return
        self._pr_url = pr_url
        self._narration_buffer.clear()
        self._file_offset = 0
        if pr_url is None:
            self._narration_path = None
            # Restore global log view.
            self._refresh_static_global()
        else:
            self._narration_path = _narration_log_path(pr_url)
            if self._narration_path is None:
                self.query_one("#activity-log", Static).update("(could not resolve narration log)")
            else:
                # Immediate tail so the user sees existing content right away.
                self.update_tail()

    def update_tail(self) -> None:
        """Tail the active PR's narration.log. Called by the app's poll timer."""
        if self._narration_path is None:
            return
        log_path = self._narration_path
        if not log_path.exists():
            return
        try:
            size = log_path.stat().st_size
            if size == self._file_offset:
                return
            if size < self._file_offset:
                self._file_offset = 0
                self._narration_buffer.clear()
            with log_path.open("r", encoding="utf-8", errors="replace") as fh:
                fh.seek(self._file_offset)
                new_text = fh.read()
            self._file_offset = size
            for line in new_text.splitlines():
                self._narration_buffer.append(line)
            self._refresh_static_pr()
        except OSError:
            pass

    def update_workers(self, rows: "list[WorkerRow]", *, ascii_only: bool = False) -> None:
        """No-op: worker state is now reflected by the stage tab counts."""

    def update_runs(self, rows: "list[RunRow]") -> None:
        """No-op: run state is now reflected by the stage tab counts."""

    def update_plan(self, snapshot: "SyncPlanSnapshot | None", *, ascii_only: bool = False) -> None:
        """No-op: sync plan is now reflected by the stage tab counts."""

    def write(self, line: str) -> None:
        """Append a single log line.

        Always updates _log_buffer and the visible static. This preserves
        backward compatibility: tests read _log_buffer and the static to
        verify that operational messages appeared.

        In production, update_tail() on the next poll cycle will overwrite
        the static with per-PR content when a PR is selected; that is
        acceptable because global messages are also visible in GlobalActivityStrip.
        """
        self._log_buffer.append(line)
        self._refresh_static_global()

    def clear_log(self) -> None:
        """Clear the global log buffer."""
        self._log_buffer.clear()
        if self._pr_url is None:
            self.query_one("#activity-log", Static).update("(no log output)")

    # --- internal ---

    def _refresh_static_global(self) -> None:
        text = "\n".join(self._log_buffer) if self._log_buffer else "(no log output)"
        self.query_one("#activity-log", Static).update(text)

    def _refresh_static_pr(self) -> None:
        text = "\n".join(self._narration_buffer) if self._narration_buffer else "(no activity)"
        self.query_one("#activity-log", Static).update(text)
