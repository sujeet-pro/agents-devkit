from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from textual import events
from textual.message import Message
from textual.widgets import DataTable

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow, QueueSnapshot
    from tui.model.work_queue_model import PrWorkState
    from tui.model.workers_model import WorkerRow


_ALL_COLUMNS: dict[str, dict] = {
    "repo":    {"width": 24},
    "pr":      {"width": 8},
    "author":  {"width": 16},
    "title":   {"width": 40},
    "task":    {"width": 18},
    "stage":   {"width": 6},
    "current": {"width": 18},
    "branch":  {"width": 18},
    "age":     {"width": 8},
}

_ALL_COLUMN_NAMES: tuple[str, ...] = tuple(_ALL_COLUMNS.keys())

# Backward-compat alias: tuple of (name, width) pairs in the full-width order.
_COLUMNS: tuple[tuple[str, int], ...] = tuple(
    (name, cfg["width"]) for name, cfg in _ALL_COLUMNS.items()
)

PR_NUMBER_COLUMN = 1


def _severity_badge(row: "QueueRow", *, ascii_only: bool = False) -> str:
    """Return a single-char badge for the highest open severity, else ' '."""
    from tui.model.queue_model import _PR_REVIEW_ROOT
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "findings.json"
    if not path.exists():
        return " "
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return " "
    findings = data if isinstance(data, list) else (data.get("findings") or [])
    severities = {(f.get("severity") or "").lower() for f in findings if isinstance(f, dict)}
    if "blocker" in severities:
        return "X" if ascii_only else "⛔"
    if "critical" in severities:
        return "!" if ascii_only else "⚠"
    return "." if ascii_only else "·"


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
        self._current_column_set: tuple[str, ...] | None = None

    def _pr_number_column_index(self) -> int:
        return PR_NUMBER_COLUMN

    def _ensure_columns(self) -> None:
        if self._current_column_set == _ALL_COLUMN_NAMES:
            return
        self.clear(columns=True)
        for name in _ALL_COLUMN_NAMES:
            self.add_column(name, width=_ALL_COLUMNS[name]["width"])
        self._current_column_set = _ALL_COLUMN_NAMES

    def load(
        self,
        snapshot: "QueueSnapshot",
        *,
        ascii_only: bool = False,
        work_states: "dict[str, PrWorkState] | None" = None,
        workers_by_url: "dict[str, WorkerRow] | None" = None,
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
                "—",
                "no PRs",
                f"(queue: {snapshot.queue_path})",
                "—",
                "no PRs",
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
                current_base = f"{prefix}{format_work_cell(work_state)}"
            else:
                current_base = _format_current_status(state.icon, state.label, worker)
            badge = _severity_badge(row, ascii_only=ascii_only)
            current = f"{badge} {current_base}"
            stage = _format_stage_glyph(row, worker, ascii_only=ascii_only)
            self.add_row(
                row.repo,
                str(row.number),
                _format_author(row.author),
                title,
                pr_status,
                stage,
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
        if coordinate is None or coordinate.column != self._pr_number_column_index():
            return
        pr_url = self.pr_url_for_row(coordinate.row)
        if pr_url is None:
            return
        event.stop()
        self.post_message(self.PrNumberClicked(pr_url))


def _format_author(author: "dict | None") -> str:
    """Return a truncated author display string for the queue table column."""
    if not isinstance(author, dict):
        return "—"
    name = (
        author.get("display_name")
        or author.get("login")
        or author.get("host_user_id")
        or ""
    )
    if not name:
        return "—"
    return name[:16]


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


def _format_current_status(icon: str, label: str, worker: "WorkerRow | None") -> str:
    if worker is None:
        return f"{icon} {label}"
    phase = worker.current_phase or worker.status
    return f"{icon} {phase}"


# Stage glyph column: S I R V P for Sync / Index / Review / Validate / Post.
# Each slot: · pending (gray), ✓ done, ⚡ running, ! failed.
_STAGE_GLYPH_DONE    = "✓"
_STAGE_GLYPH_RUNNING = "⚡"
_STAGE_GLYPH_FAILED  = "!"
_STAGE_GLYPH_PENDING = "·"

_STAGE_GLYPH_DONE_ASCII    = "v"
_STAGE_GLYPH_RUNNING_ASCII = ">"
_STAGE_GLYPH_FAILED_ASCII  = "!"
_STAGE_GLYPH_PENDING_ASCII = "."

# Maps worker task_type values to which stage slot is "running".
_WORKER_TASK_TYPE_TO_STAGE: dict[str, str] = {
    "sync":    "sync",
    "prepare": "index",
    "index":   "index",
    "review":  "review",
    "post":    "post",
}


def _stage_char(
    done: bool,
    running: bool,
    failed: bool,
    *,
    ascii_only: bool,
) -> str:
    if ascii_only:
        if running:
            return _STAGE_GLYPH_RUNNING_ASCII
        if failed:
            return _STAGE_GLYPH_FAILED_ASCII
        if done:
            return _STAGE_GLYPH_DONE_ASCII
        return _STAGE_GLYPH_PENDING_ASCII
    if running:
        return _STAGE_GLYPH_RUNNING
    if failed:
        return _STAGE_GLYPH_FAILED
    if done:
        return _STAGE_GLYPH_DONE
    return _STAGE_GLYPH_PENDING


def _format_stage_glyph(
    row: "QueueRow",
    worker: "WorkerRow | None",
    *,
    ascii_only: bool = False,
) -> str:
    """Build the 5-char stage progress string: S I R V P."""
    live_stage = None
    if worker is not None and not worker.is_stale:
        live_stage = _WORKER_TASK_TYPE_TO_STAGE.get(worker.task_type or "", None)

    def _ch(stage: str, done_ts: "str | None") -> str:
        running = live_stage == stage
        done = bool(done_ts)
        return _stage_char(done=done, running=running, failed=False, ascii_only=ascii_only)

    s = _ch("sync", getattr(row, "last_synced_at", None))
    i = _ch("index", getattr(row, "last_indexed_at", None))
    r = _ch("review", getattr(row, "last_reviewed_at", None))
    v = _ch("validate", getattr(row, "last_validated_at", None))
    p = _ch("post", getattr(row, "last_posted_at", None))
    return f"{s}{i}{r}{v}{p}"
