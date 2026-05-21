from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncPlanStep:
    name: str
    status: str
    rc: int | None
    started_at: str | None
    completed_at: str | None


@dataclass(frozen=True)
class SyncPlanSnapshot:
    queue: str
    started_at: str
    updated_at: str
    completed_at: str | None
    rc: int | None
    steps: list[SyncPlanStep]


def default_plan_path() -> Path:
    env = os.environ.get("ADK_TUI_PLAN_PATH")
    if env:
        return Path(env)
    return Path.home() / ".agents-devkit" / "tui" / "workers" / "sync-plan.json"


class SyncPlanModel:
    def __init__(self, plan_path: Path | None = None) -> None:
        self.plan_path = plan_path if plan_path is not None else default_plan_path()
        self._last_mtime: float | None = None

    def has_changed(self) -> bool:
        # Sentinel: _last_mtime == 0.0 means "we already observed the file
        # was missing"; None means "never sampled". Both surface as "changed"
        # on the first call so the pane gets its initial render.
        if not self.plan_path.exists():
            return self._last_mtime != 0.0
        try:
            cur = self.plan_path.stat().st_mtime
        except OSError:
            return False
        return cur != self._last_mtime

    def snapshot(self) -> SyncPlanSnapshot | None:
        if not self.plan_path.exists():
            self._last_mtime = 0.0
            return None
        try:
            self._last_mtime = self.plan_path.stat().st_mtime
            raw = json.loads(self.plan_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if raw.get("version") != 1:
            return None
        try:
            steps = [
                SyncPlanStep(
                    name=str(s.get("name", "")),
                    status=str(s.get("status", "pending")),
                    rc=s.get("rc"),
                    started_at=s.get("started_at"),
                    completed_at=s.get("completed_at"),
                )
                for s in raw.get("steps") or []
            ]
            return SyncPlanSnapshot(
                queue=str(raw.get("queue", "")),
                started_at=str(raw.get("started_at", "")),
                updated_at=str(raw.get("updated_at", "")),
                completed_at=raw.get("completed_at"),
                rc=raw.get("rc"),
                steps=steps,
            )
        except (TypeError, ValueError):
            return None
