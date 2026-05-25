from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class WorkerRow:
    pid: int
    worker_id: str
    run_id: str | None
    pr_url: str
    subject: str
    task_type: str
    status: str
    agent: str
    queue: str
    started_at: str
    last_heartbeat: str
    current_phase: str
    rc: int | None
    log_path: str | None
    links: dict
    artifacts: dict
    age_s: float
    is_stale: bool


def default_workers_dir() -> Path:
    return Path.home() / ".agents-devkit" / "tui" / "workers"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


class WorkersModel:
    """Scans a directory of <pid>.json heartbeat files. Returns the live ones,
    GCs the dead. Mtime-gated by directory mtime AND by aggregate file mtime
    (to catch a single file's update without a directory mutation)."""

    def __init__(
        self,
        workers_dir: Path | None = None,
        *,
        stale_after_s: float = 30.0,
        gc_after_s: float = 120.0,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.workers_dir = workers_dir if workers_dir is not None else default_workers_dir()
        self.stale_after_s = stale_after_s
        self.gc_after_s = gc_after_s
        if now_fn is None:
            now_fn = lambda: datetime.now(tz=timezone.utc)  # noqa: E731
        self._now_fn = now_fn
        self._last_signature: tuple | None = None

    def _signature(self) -> tuple:
        """Cheap directory fingerprint. (dir_mtime, [(name, mtime, size)...])."""
        if not self.workers_dir.exists():
            return (0.0, ())
        try:
            dm = self.workers_dir.stat().st_mtime
        except OSError:
            return (0.0, ())
        items: list[tuple[str, float, int]] = []
        try:
            for p in self.workers_dir.iterdir():
                if p.suffix == ".json":
                    try:
                        st = p.stat()
                        items.append((p.name, st.st_mtime, st.st_size))
                    except OSError:
                        continue
        except OSError:
            return (dm, ())
        items.sort()
        return (dm, tuple(items))

    def has_changed(self) -> bool:
        cur = self._signature()
        if cur != self._last_signature:
            return True
        return False

    def snapshot(self) -> list[WorkerRow]:
        self._last_signature = self._signature()
        if not self.workers_dir.exists():
            return []
        now = self._now_fn()
        rows: list[WorkerRow] = []
        try:
            entries = sorted(self.workers_dir.iterdir())
        except OSError:
            return []
        for p in entries:
            if p.suffix != ".json":
                continue
            row = self._parse_one(p, now)
            if row is None:
                continue
            rows.append(row)
        return rows

    def gc(self) -> int:
        """Remove heartbeat files older than gc_after_s. Returns the count removed."""
        if not self.workers_dir.exists():
            return 0
        now = self._now_fn()
        removed = 0
        try:
            entries = list(self.workers_dir.iterdir())
        except OSError:
            return 0
        for p in entries:
            if p.suffix != ".json":
                continue
            try:
                raw = json.loads(p.read_text())
                last = _parse_iso(raw.get("last_heartbeat")) if isinstance(raw, dict) else None
            except (OSError, json.JSONDecodeError, TypeError):
                last = None
            if last is None:
                # Unparseable file — GC if its mtime is also old enough.
                try:
                    file_age = (now.timestamp() - p.stat().st_mtime)
                except OSError:
                    continue
                if file_age > self.gc_after_s:
                    self._unlink(p)
                    removed += 1
                continue
            age = (now - last).total_seconds()
            if age > self.gc_after_s:
                self._unlink(p)
                removed += 1
        return removed

    def _parse_one(self, p: Path, now: datetime) -> WorkerRow | None:
        try:
            raw = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(raw, dict):
            return None
        last = _parse_iso(raw.get("last_heartbeat"))
        if last is None:
            return None
        age = (now - last).total_seconds()
        is_stale = age > self.stale_after_s
        try:
            return WorkerRow(
                pid=int(raw.get("pid", 0)),
                worker_id=str(raw.get("worker_id") or p.stem),
                run_id=(str(raw.get("run_id")) if raw.get("run_id") else None),
                pr_url=str(raw.get("pr_url", "")),
                subject=str(raw.get("subject") or raw.get("pr_url") or ""),
                task_type=str(raw.get("task_type", "")),
                status=str(raw.get("status") or ("running" if raw.get("rc") is None else "done")),
                agent=str(raw.get("agent", "")),
                queue=str(raw.get("queue", "")),
                started_at=str(raw.get("started_at", "")),
                last_heartbeat=str(raw.get("last_heartbeat", "")),
                current_phase=str(raw.get("current_phase", "")),
                rc=raw.get("rc"),
                log_path=(str(raw.get("log_path")) if raw.get("log_path") else None),
                links=raw.get("links") if isinstance(raw.get("links"), dict) else {},
                artifacts=raw.get("artifacts") if isinstance(raw.get("artifacts"), dict) else {},
                age_s=age,
                is_stale=is_stale,
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _unlink(p: Path) -> None:
        try:
            p.unlink()
        except OSError:
            pass
