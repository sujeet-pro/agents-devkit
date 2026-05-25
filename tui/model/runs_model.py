from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_data_home  # noqa: E402


@dataclass(frozen=True)
class RunRow:
    run_id: str
    task_type: str
    status: str
    started_by: str
    runner: str
    parallel: int | None
    selected: int | None
    started_at: str
    updated_at: str
    completed_at: str | None
    run_dir: str | None
    links: dict
    steps: list[dict]
    results: list[dict]
    artifacts: dict
    workers: list[str]


def default_runs_dir() -> Path:
    return adk_data_home() / "tui" / "runs"


class RunsModel:
    def __init__(self, runs_dir: Path | None = None) -> None:
        self.runs_dir = runs_dir if runs_dir is not None else default_runs_dir()
        self._last_signature: tuple | None = None

    def _signature(self) -> tuple:
        if not self.runs_dir.exists():
            return (0.0, ())
        try:
            dm = self.runs_dir.stat().st_mtime
        except OSError:
            return (0.0, ())
        items = []
        try:
            for p in self.runs_dir.iterdir():
                if p.suffix == ".json":
                    try:
                        st = p.stat()
                        items.append((p.name, st.st_mtime, st.st_size))
                    except OSError:
                        continue
        except OSError:
            return (dm, ())
        return (dm, tuple(sorted(items)))

    def has_changed(self) -> bool:
        return self._signature() != self._last_signature

    def snapshot(self, *, limit: int = 6) -> list[RunRow]:
        self._last_signature = self._signature()
        if not self.runs_dir.exists():
            return []
        rows = []
        try:
            entries = sorted(
                [p for p in self.runs_dir.iterdir() if p.suffix == ".json"],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            return []
        for p in entries[:limit]:
            row = self._parse_one(p)
            if row is not None:
                rows.append(row)
        return rows

    def _parse_one(self, p: Path) -> RunRow | None:
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(raw, dict):
            return None
        try:
            return RunRow(
                run_id=str(raw.get("run_id") or p.stem),
                task_type=str(raw.get("task_type") or ""),
                status=str(raw.get("status") or ""),
                started_by=str(raw.get("started_by") or ""),
                runner=str(raw.get("runner") or raw.get("agent") or ""),
                parallel=(int(raw["parallel"]) if raw.get("parallel") is not None else None),
                selected=(int(raw["selected"]) if raw.get("selected") is not None else None),
                started_at=str(raw.get("started_at") or raw.get("created_at") or ""),
                updated_at=str(raw.get("updated_at") or ""),
                completed_at=(str(raw.get("completed_at")) if raw.get("completed_at") else None),
                run_dir=(str(raw.get("run_dir")) if raw.get("run_dir") else None),
                links=raw.get("links") if isinstance(raw.get("links"), dict) else {},
                steps=[s for s in (raw.get("steps") or []) if isinstance(s, dict)],
                results=[r for r in (raw.get("results") or []) if isinstance(r, dict)],
                artifacts=raw.get("artifacts") if isinstance(raw.get("artifacts"), dict) else {},
                workers=[str(w) for w in (raw.get("workers") or [])],
            )
        except (TypeError, ValueError):
            return None
