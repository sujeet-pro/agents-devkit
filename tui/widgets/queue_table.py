from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from textual.widgets import DataTable

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow, QueueSnapshot


_COLUMNS: tuple[tuple[str, int], ...] = (
    ("", 5),
    ("#", 8),
    ("repo", 24),
    ("title", 40),
    ("branch", 18),
    ("age", 8),
)


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
        selected_order: list[str] | None = None,
    ) -> None:
        from tui.model.row_state import derive

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
            )
            self._row_urls.append(None)
            return

        selected_order = selected_order or []
        sel_pos: dict[str, int] = {url: i + 1 for i, url in enumerate(selected_order)}

        for row in snapshot.rows:
            state = derive(row, ascii_only=ascii_only, now=snapshot.now)
            branch = row.target_branch or "—"
            title = row.title or "—"
            pos = sel_pos.get(row.pr_url)
            if pos is not None:
                marker_label = f"[{min(pos, 9)}]"
                icon_cell = f"{marker_label}{state.icon}"
            else:
                icon_cell = f"   {state.icon}"
            self.add_row(
                icon_cell,
                str(row.number),
                row.repo,
                title,
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
        if idx is None or idx < 0 or idx >= len(self._row_urls):
            return None
        return self._row_urls[idx]
