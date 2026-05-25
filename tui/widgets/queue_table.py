from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from textual import events
from textual.message import Message
from textual.widgets import DataTable

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow, QueueSnapshot
    from tui.model.work_queue_model import PrWorkState
    from tui.model.workers_model import WorkerRow


_COLUMNS: tuple[tuple[str, int], ...] = (
    ("repo", 24),
    ("pr", 8),
    ("title", 40),
    ("task", 18),
    ("current", 26),
    ("branch", 18),
    ("age", 8),
)
PR_NUMBER_COLUMN = 1


def _format_age(iso_str: str | None, now: datetime) -> str:
    if not iso_str:
        return "—"
    ts = iso_str
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(ts)
    except ValueError:
        return "—"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta = now - parsed
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    return f"{days}d"


class QueueTable(DataTable):
    class PrNumberClicked(Message):
        def __init__(self, pr_url: str) -> None:
            super().__init__()
            self.pr_url = pr_url

    def __init__(self) -> None:
        super().__init__(zebra_stripes=True)
        self.cursor_type = "row"
        self._row_urls: list[str | None] = []
        self._columns_added = False

    def _ensure_columns(self) -> None:
        if self._columns_added:
            return
        for label, width in _COLUMNS:
            self.add_column(label, width=width)
        self._columns_added = True

    def load(
        self,
        snapshot: QueueSnapshot,
        *,
        ascii_only: bool = False,
        work_states: dict[str, "PrWorkState"] | None = None,
        workers_by_url: dict[str, WorkerRow] | None = None,
    ) -> None:
        from tui.model.row_state import derive
        from tui.model.work_queue_model import format_work_cell

        self._ensure_columns()
        prev_url = self.selected_pr_url()

        self.clear()
        self._row_urls = []

        if snapshot.missing or not snapshot.rows:
            self.add_row(
                "—",
                "—",
                "no PRs",
                f"(queue: {snapshot.queue_path})",
                "—",
                "—",
                "—",
            )
            self._row_urls.append(None)
            return

        work_states = work_states or {}
        workers_by_url = workers_by_url or {}

        for row in snapshot.rows:
            state = derive(row, ascii_only=ascii_only, now=snapshot.now)
            branch = row.target_branch or "—"
            title = row.title or "—"
            worker = workers_by_url.get(row.pr_url)
            pr_status = _format_pr_status(row, worker)
            work_state = work_states.get(row.pr_url)
            if work_state is not None:
                prefix = "▶ " if work_state.status == "running" else ""
                current = f"{prefix}{format_work_cell(work_state)}"
            else:
                current = _format_current_status(state.icon, state.label, worker)
            self.add_row(
                row.repo,
                str(row.number),
                title,
                pr_status,
                current,
                branch,
                _format_age(row.last_checked_at, snapshot.now),
            )
            self._row_urls.append(row.pr_url)

        if prev_url is not None and prev_url in self._row_urls:
            self.move_cursor(row=self._row_urls.index(prev_url))

    def selected_pr_url(self) -> str | None:
        if not self._row_urls:
            return None
        idx = self.cursor_row
        return self.pr_url_for_row(idx)

    def pr_url_for_row(self, idx: int | None) -> str | None:
        if idx is None:
            return None
        if not self._row_urls:
            return None
        if idx < 0 or idx >= len(self._row_urls):
            return None
        return self._row_urls[idx]

    @staticmethod
    def is_pr_number_column(column: int | None) -> bool:
        return column == PR_NUMBER_COLUMN

    def on_click(self, event: events.Click) -> None:
        coordinate = self.hover_coordinate
        if coordinate is None or not self.is_pr_number_column(coordinate.column):
            return
        pr_url = self.pr_url_for_row(coordinate.row)
        if pr_url is None:
            return
        event.stop()
        self.post_message(self.PrNumberClicked(pr_url))


def _format_pr_status(row: "QueueRow", worker: "WorkerRow | None" = None) -> str:
    """Return the developer-facing task_status for this PR row.

    Uses ``derive_task_status`` from the pr_status model so the column shows
    richer lifecycle state (indexing / reviewing / needs_re_review / …)
    rather than the raw queue status string.  The worker is passed in so that
    live heartbeat state (syncing / reviewing / posting …) is reflected
    immediately without waiting for a queue-file write.
    """
    from tui.model.pr_status import derive_task_status
    workers = [worker] if worker is not None else None
    return derive_task_status(row, workers)


def _format_current_status(icon: str, label: str, worker: WorkerRow | None) -> str:
    if worker is None:
        return f"{icon} {label}"
    phase = worker.current_phase or worker.status
    return f"{icon} {phase}"
