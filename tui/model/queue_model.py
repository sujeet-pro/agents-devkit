from __future__ import annotations

import sys
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os import environ
from pathlib import Path
from typing import Callable, Literal

_CLI_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "skills" / "adk-cli" / "scripts"
if str(_CLI_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CLI_SCRIPTS))

import queue_io  # noqa: E402

_ADK_HOME = Path(environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
_PR_REVIEW_ROOT = _ADK_HOME / "skill-pr-review"


FilterMode = Literal["all", "open", "ready", "reviewed", "terminal"]
SortMode = Literal["queue", "fifo", "newest", "repo"]


# Single source of truth for terminal queue statuses.
# Used by widgets and screens; keep public so they can import without
# triggering the full queue_io import chain themselves.
TERMINAL_STATUSES: frozenset[str] = frozenset({"merged", "closed"})
_TERMINAL_STATUSES = TERMINAL_STATUSES  # backward-compat alias
_REVIEWED_STATUSES = {"reviewed", "approved", "comments", "reminded"}


@dataclass(frozen=True)
class QueueRow:
    queue_index: int
    pr_url: str
    host: str
    repo: str
    number: int
    title: str | None
    author: str | None
    target_branch: str | None
    head_sha: str | None
    status: str
    prep_status: str | None
    prep_error: str | None
    taken_at: str | None
    last_checked_at: str | None
    last_reviewed_at: str | None
    last_reviewed_head_sha: str | None
    ready_for_review: bool
    slack_permalink: str | None


@dataclass
class QueueSnapshot:
    rows: list[QueueRow]
    total: int
    ready_count: int
    in_review_count: int
    platform_summary: str
    queue_path: Path
    mtime: float
    missing: bool
    now: datetime


def _row_from_entry(entry: dict, now: datetime, *, queue_index: int) -> QueueRow | None:
    pr_url = entry.get("pr_url")
    if not pr_url:
        return None
    try:
        host, repo, number = queue_io.dedupe_key(pr_url)
    except ValueError:
        return None

    slack = entry.get("slack") or {}
    slack_permalink = slack.get("permalink") if isinstance(slack, dict) else None

    title = entry.get("title") or _title_from_task_dir(repo, number)

    return QueueRow(
        queue_index=queue_index,
        pr_url=pr_url,
        host=host,
        repo=repo,
        number=number,
        title=title,
        author=entry.get("author"),
        target_branch=entry.get("target_branch"),
        head_sha=entry.get("head_sha"),
        status=entry.get("status") or "",
        prep_status=entry.get("prep_status"),
        prep_error=entry.get("prep_error"),
        taken_at=entry.get("taken_at"),
        last_checked_at=entry.get("last_checked_at"),
        last_reviewed_at=entry.get("last_reviewed_at"),
        last_reviewed_head_sha=entry.get("last_reviewed_head_sha"),
        ready_for_review=queue_io.ready_for_review(entry, now=now),
        slack_permalink=slack_permalink,
    )


def _title_from_task_dir(repo: str, number: int) -> str | None:
    """Best-effort title fallback for older queue rows without `title`.

    Existing prepared PR folders usually have `pr.json` even when the queue row
    predates title capture. Reading one small JSON file keeps the TUI useful
    without forcing a full queue refresh.
    """
    task_dir = _PR_REVIEW_ROOT / f"{repo}_pr-{number}"
    for rel in ("pr.json", "pr-review/pr.json"):
        path = task_dir / rel
        if not path.exists():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        title = raw.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    return None


def _passes_filter(row: QueueRow, filter_mode: FilterMode) -> bool:
    if filter_mode == "all":
        return True
    if filter_mode == "open":
        return row.status not in _TERMINAL_STATUSES
    if filter_mode == "ready":
        return row.ready_for_review
    if filter_mode == "reviewed":
        return row.status in _REVIEWED_STATUSES
    if filter_mode == "terminal":
        return row.status in _TERMINAL_STATUSES
    return True


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _sort_key_fifo(row: QueueRow) -> int:
    return row.queue_index


def _sort_key_newest(row: QueueRow) -> tuple[int, str]:
    if not row.last_checked_at:
        return (1, "")
    return (0, row.last_checked_at)


def _sort_rows(rows: list[QueueRow], sort_mode: SortMode) -> list[QueueRow]:
    if sort_mode in {"queue", "fifo"}:
        return sorted(rows, key=_sort_key_fifo)
    if sort_mode == "newest":
        # Rows with a last_checked_at come first (bucket 0), sorted descending
        # by the ISO timestamp; rows without one go to the end.
        with_ts = [r for r in rows if r.last_checked_at]
        without_ts = [r for r in rows if not r.last_checked_at]
        with_ts.sort(key=lambda r: r.last_checked_at or "", reverse=True)
        return with_ts + without_ts
    if sort_mode == "repo":
        return sorted(rows, key=lambda r: (r.host, r.repo, r.number))
    return rows


def _platform_summary(rows: list[QueueRow]) -> str:
    if not rows:
        return "empty"
    hosts = {r.host for r in rows}
    if hosts == {"github"}:
        return "github"
    if hosts == {"bitbucket"}:
        return "bitbucket"
    return "github+bitbucket"


class QueueModel:
    """Wraps queue_io.read_queue + ready_for_review + filter/sort."""

    def __init__(
        self,
        queue_path: Path | None = None,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.queue_path: Path = queue_path if queue_path is not None else queue_io.DEFAULT_QUEUE_PATH
        if now_fn is None:
            now_fn = lambda: datetime.now(tz=timezone.utc)  # noqa: E731
        self._now_fn: Callable[[], datetime] = now_fn
        self._last_mtime: float | None = None

    def has_changed(self) -> bool:
        exists_now = self.queue_path.exists()
        if self._last_mtime is None:
            return True
        if not exists_now:
            # File disappeared since last snapshot. Sentinel for "missing" mtime is 0.0.
            return self._last_mtime != 0.0
        try:
            cur_mtime = self.queue_path.stat().st_mtime
        except OSError:
            return self._last_mtime != 0.0
        return cur_mtime != self._last_mtime

    def snapshot(
        self,
        *,
        filter_mode: FilterMode = "all",
        sort_mode: SortMode = "queue",
    ) -> QueueSnapshot:
        now = self._now_fn()
        if not self.queue_path.exists():
            self._last_mtime = 0.0
            return QueueSnapshot(
                rows=[],
                total=0,
                ready_count=0,
                in_review_count=0,
                platform_summary="empty",
                queue_path=self.queue_path,
                mtime=0.0,
                missing=True,
                now=now,
            )

        queue = queue_io.read_queue(self.queue_path)
        try:
            mtime = self.queue_path.stat().st_mtime
        except OSError:
            mtime = 0.0
        self._last_mtime = mtime

        entries = queue.get("prs") or []
        all_rows: list[QueueRow] = []
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            row = _row_from_entry(entry, now, queue_index=idx)
            if row is not None:
                all_rows.append(row)

        total = len(all_rows)
        ready_count = sum(1 for r in all_rows if r.ready_for_review)

        lock_max = timedelta(seconds=queue_io.TAKEN_LOCK_MAX_AGE_SECONDS)
        in_review_count = 0
        for r in all_rows:
            ts = _parse_iso(r.taken_at)
            if ts is not None and (now - ts) < lock_max:
                in_review_count += 1

        platform_summary = _platform_summary(all_rows)

        filtered = [r for r in all_rows if _passes_filter(r, filter_mode)]
        sorted_rows = _sort_rows(filtered, sort_mode)

        return QueueSnapshot(
            rows=sorted_rows,
            total=total,
            ready_count=ready_count,
            in_review_count=in_review_count,
            platform_summary=platform_summary,
            queue_path=self.queue_path,
            mtime=mtime,
            missing=False,
            now=now,
        )
