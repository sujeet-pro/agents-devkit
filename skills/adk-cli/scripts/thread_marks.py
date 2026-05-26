"""thread_marks.py — persistent dedupe for one-shot Slack posts per thread.

The gentle-reminder path in `pr_scan.maybe_emit_gentle_reminders` used to dedupe
solely from the queue's `slack.gentle_reminder_at` field on a row. That works
while the row is alive, but once every PR in the thread reaches a terminal
state, the row is garbage-collected and the mark goes with it — letting the
next scan re-discover the thread and re-post.

This sidecar survives row GC. One JSON file keyed by `(channel_id, thread_ts)`.
24h-rolling retention by the writer; expired entries are pruned on every write.

File: `$ADK_CONFIG_HOME/pr-thread-marks.json`
Lock: `$ADK_CONFIG_HOME/pr-thread-marks.json.lock` (fcntl).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import file_lock  # noqa: E402

_ADK_REPO_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if str(_ADK_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_ADK_REPO_LIB))
from config import adk_config_home  # noqa: E402


DEFAULT_RETENTION_HOURS = 24.0


def default_marks_path() -> Path:
    """Resolve the sidecar path against the current `ADK_CONFIG_HOME`.

    Lazy by design: the env var is mutable in tests (and config-relocation
    flows), so a frozen module-level constant would silently outrun reality.
    """
    return adk_config_home() / "pr-thread-marks.json"


def _lock_path(path: Path) -> Path:
    return Path(str(path) + ".lock")


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.exists():
        return {"marks": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"marks": []}


def _prune(marks: list[dict], *, now: datetime, retention_hours: float) -> list[dict]:
    cutoff = now - timedelta(hours=retention_hours)
    kept = []
    for m in marks:
        ts = _parse_iso(m.get("gentle_reminder_at"))
        if ts is None or ts >= cutoff:
            kept.append(m)
    return kept


def recent_thread_marks(*, path: Path | None = None,
                        within_hours: float = DEFAULT_RETENTION_HOURS,
                        now: datetime | None = None) -> set[tuple[str, str]]:
    """Return the set of `(channel_id, thread_ts)` posted within `within_hours`.

    Read-only; does not lock. Callers use this to gate a post.
    """
    path = path or default_marks_path()
    now = now or datetime.now(tz=timezone.utc)
    cutoff = now - timedelta(hours=within_hours)
    out: set[tuple[str, str]] = set()
    for m in _read(path).get("marks", []) or []:
        ts = _parse_iso(m.get("gentle_reminder_at"))
        if ts is None or ts < cutoff:
            continue
        cid, tts = m.get("channel_id"), m.get("thread_ts")
        if cid and tts:
            out.add((cid, tts))
    return out


def record_thread_mark(channel_id: str, thread_ts: str, *,
                       path: Path | None = None,
                       at_iso: str | None = None,
                       retention_hours: float = DEFAULT_RETENTION_HOURS,
                       now: datetime | None = None) -> None:
    """Record (or refresh) a mark for this thread. Prunes expired entries.

    Held under fcntl lock; safe under concurrent `adk pr-scan` invocations.
    """
    path = path or default_marks_path()
    now = now or datetime.now(tz=timezone.utc)
    at_iso = at_iso or _now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(_lock_path(path), timeout_s=30.0):
        data = _read(path)
        marks = data.get("marks", []) or []
        # Update or append.
        idx = next((i for i, m in enumerate(marks)
                    if m.get("channel_id") == channel_id
                    and m.get("thread_ts") == thread_ts), None)
        if idx is None:
            marks.append({"channel_id": channel_id, "thread_ts": thread_ts,
                          "gentle_reminder_at": at_iso})
        else:
            marks[idx]["gentle_reminder_at"] = at_iso
        marks = _prune(marks, now=now, retention_hours=retention_hours)
        data["marks"] = marks
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
