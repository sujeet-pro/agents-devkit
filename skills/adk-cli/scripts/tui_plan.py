"""TUI sync-plan writer. Persists $ADK_DATA_HOME/tui/workers/sync-plan.json
during pr-sync execution so the TUI's Sync-plan pane can render live progress.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

_LIB_DIR = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_data_home  # noqa: E402

PLAN_VERSION = 1

DEFAULT_PLAN_PATH = adk_data_home() / "tui" / "workers" / "sync-plan.json"

StepStatus = Literal["pending", "running", "ok", "warn", "failed", "skipped"]


def plan_path() -> Path:
    """Return ADK_TUI_PLAN_PATH if set, else DEFAULT_PLAN_PATH."""
    env = os.environ.get("ADK_TUI_PLAN_PATH")
    return Path(env) if env else DEFAULT_PLAN_PATH


@dataclass
class StepRecord:
    name: str
    status: StepStatus = "pending"
    rc: int | None = None
    started_at: str | None = None
    completed_at: str | None = None


class SyncPlanWriter:
    """Append-only step tracker that persists to PLAN_PATH atomically."""

    def __init__(self, queue: str, argv: list[str], step_names: list[str], *, path: Path | None = None) -> None:
        self.path = path if path is not None else plan_path()
        self._queue = queue
        self._argv = list(argv)
        self._steps: list[StepRecord] = [StepRecord(name=n) for n in step_names]
        self._started_at = _utc_now_iso()
        self._completed_at: str | None = None
        self._rc: int | None = None
        self._index_by_name: dict[str, int] = {n: i for i, n in enumerate(step_names)}
        self._write()

    def step_start(self, name: str) -> None:
        rec = self._get(name)
        rec.status = "running"
        rec.started_at = _utc_now_iso()
        self._write()

    def step_done(self, name: str, *, status: StepStatus, rc: int | None = None) -> None:
        rec = self._get(name)
        rec.status = status
        rec.rc = rc
        rec.completed_at = _utc_now_iso()
        self._write()

    def finish(self, rc: int) -> None:
        self._completed_at = _utc_now_iso()
        self._rc = rc
        self._write()

    def _get(self, name: str) -> StepRecord:
        idx = self._index_by_name.get(name)
        if idx is None:
            rec = StepRecord(name=name)
            self._steps.append(rec)
            self._index_by_name[name] = len(self._steps) - 1
            return rec
        return self._steps[idx]

    def _write(self) -> None:
        payload = {
            "version": PLAN_VERSION,
            "queue": self._queue,
            "argv": self._argv,
            "started_at": self._started_at,
            "updated_at": _utc_now_iso(),
            "completed_at": self._completed_at,
            "rc": self._rc,
            "steps": [asdict(s) for s in self._steps],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, self.path)


def _utc_now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
