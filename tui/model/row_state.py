from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .queue_model import QueueRow, _parse_iso

import queue_io  # type: ignore[import-not-found]  # sys.path set by queue_model


@dataclass(frozen=True)
class RowState:
    icon: str
    label: str
    color: str


ICON_SET: dict[str, str] = {
    "queued": "🌱",
    "fetching": "🔍",
    "waiting_for_base": "⏳",
    "preparing": "⚙",
    "ready": "✓",
    "in_review": "⚙↻",
    "reviewed": "📝",
    "approved": "✅",
    "blocked": "🚫",
    "merged": "🔒",
    "closed": "🔒",
    "prep_failed": "⚠",
    "stale": "⏰",
}

ASCII_FALLBACK: dict[str, str] = {
    "queued": "*",
    "fetching": "?",
    "waiting_for_base": "_",
    "preparing": ".",
    "ready": "+",
    "in_review": "~",
    "reviewed": "#",
    "approved": "v",
    "blocked": "x",
    "merged": "X",
    "closed": "X",
    "prep_failed": "!",
    "stale": "@",
}


_LABELS: dict[str, str] = {
    "queued": "queued",
    "fetching": "fetching",
    "waiting_for_base": "waiting for base",
    "preparing": "preparing",
    "ready": "ready",
    "in_review": "in review",
    "reviewed": "reviewed",
    "approved": "approved",
    "blocked": "blocked",
    "merged": "merged",
    "closed": "closed",
    "prep_failed": "prep failed",
    "stale": "stale",
}


_COLORS: dict[str, str] = {
    "queued": "white",
    "fetching": "white",
    "waiting_for_base": "yellow",
    "preparing": "yellow",
    "ready": "green",
    "in_review": "blue",
    "reviewed": "blue",
    "approved": "green",
    "blocked": "red",
    "merged": "grey",
    "closed": "grey",
    "prep_failed": "red",
    "stale": "yellow",
}


def _is_locked_fresh(row: QueueRow, now: datetime) -> bool:
    ts = _parse_iso(row.taken_at)
    if ts is None:
        return False
    age = (now - ts).total_seconds()
    return age < queue_io.TAKEN_LOCK_MAX_AGE_SECONDS


def _classify(row: QueueRow, now: datetime) -> str:
    status = row.status or ""
    prep = row.prep_status

    if status in {"merged", "closed"}:
        return status
    if prep == "failed":
        return "prep_failed"
    if _is_locked_fresh(row, now):
        return "in_review"
    if status == "approved":
        return "approved"
    if status in {"reviewed", "comments", "reminded"}:
        return "reviewed"
    if prep == "preparing":
        return "preparing"
    if prep == "waiting_for_base":
        return "waiting_for_base"
    if prep == "pending":
        return "queued"
    if row.ready_for_review:
        return "ready"
    return "queued"


def derive(
    row: QueueRow,
    *,
    ascii_only: bool = False,
    now: datetime | None = None,
) -> RowState:
    if now is None:
        now = datetime.now(tz=timezone.utc)
    key = _classify(row, now)
    icons = ASCII_FALLBACK if ascii_only else ICON_SET
    return RowState(
        icon=icons[key],
        label=_LABELS[key],
        color=_COLORS[key],
    )
