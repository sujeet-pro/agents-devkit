"""Shared run/worker state for long-running ADK operations.

The TUI, CLI, and skills use these JSON files as the small public progress
contract. Writers use atomic replace so the TUI can poll without seeing partial
JSON.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
STATE_ROOT = ADK_HOME / "tui"
DEFAULT_RUNS_DIR = STATE_ROOT / "runs"
DEFAULT_WORKERS_DIR = STATE_ROOT / "workers"
DEFAULT_LOGS_DIR = STATE_ROOT / "logs"
STATE_VERSION = 1


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id(stem: str) -> str:
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}-{_safe_part(stem)}"


def worker_id(run_id_value: str, subject: str) -> str:
    return f"{run_id_value}-{_safe_part(subject)[-72:]}"


def run_path(run_id_value: str, *, runs_dir: Path | None = None) -> Path:
    root = runs_dir if runs_dir is not None else DEFAULT_RUNS_DIR
    return root / f"{run_id_value}.json"


def worker_path(worker_id_value: str, *, workers_dir: Path | None = None) -> Path:
    root = workers_dir if workers_dir is not None else DEFAULT_WORKERS_DIR
    return root / f"{worker_id_value}.json"


def write_run(run_id_value: str, payload: dict[str, Any], *,
              runs_dir: Path | None = None) -> Path:
    path = run_path(run_id_value, runs_dir=runs_dir)
    body = _base_payload(payload)
    body["run_id"] = run_id_value
    _atomic_json(path, body)
    return path


def update_run(run_id_value: str, updates: dict[str, Any], *,
               runs_dir: Path | None = None) -> Path:
    path = run_path(run_id_value, runs_dir=runs_dir)
    existing = read_json(path) if path.exists() else {}
    merged = _deep_merge(existing, updates)
    merged["updated_at"] = now_iso()
    return write_run(run_id_value, merged, runs_dir=runs_dir)


def write_worker(worker_id_value: str, payload: dict[str, Any], *,
                 workers_dir: Path | None = None) -> Path:
    path = worker_path(worker_id_value, workers_dir=workers_dir)
    body = _base_payload(payload)
    body["worker_id"] = worker_id_value
    if "last_heartbeat" not in body:
        body["last_heartbeat"] = body["updated_at"]
    _atomic_json(path, body)
    return path


def update_worker(worker_id_value: str, updates: dict[str, Any], *,
                  workers_dir: Path | None = None) -> Path:
    path = worker_path(worker_id_value, workers_dir=workers_dir)
    existing = read_json(path) if path.exists() else {}
    merged = _deep_merge(existing, updates)
    merged["updated_at"] = now_iso()
    if merged.get("status") in {"running", "starting"}:
        merged["last_heartbeat"] = merged["updated_at"]
    return write_worker(worker_id_value, merged, workers_dir=workers_dir)


def complete_worker(worker_id_value: str, *, status: str, rc: int | None = None,
                    outcome: str | None = None, workers_dir: Path | None = None,
                    **updates: Any) -> Path:
    payload: dict[str, Any] = {
        "status": status,
        "completed_at": now_iso(),
        "rc": rc,
    }
    if outcome is not None:
        payload["outcome"] = outcome
    payload.update(updates)
    return update_worker(worker_id_value, payload, workers_dir=workers_dir)


def remove_worker(worker_id_value: str, *, workers_dir: Path | None = None) -> None:
    path = worker_path(worker_id_value, workers_dir=workers_dir)
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def file_link(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path).expanduser()
    resolved = p.resolve() if p.exists() else p
    return f"file://{resolved}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _base_payload(payload: dict[str, Any]) -> dict[str, Any]:
    now = now_iso()
    out = dict(payload)
    out.setdefault("version", STATE_VERSION)
    out.setdefault("created_at", now)
    out["updated_at"] = now
    return out


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _deep_merge(existing: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    out = dict(existing)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _safe_part(value: str) -> str:
    cleaned = []
    for ch in str(value):
        if ch.isalnum() or ch in {"-", "_"}:
            cleaned.append(ch)
        else:
            cleaned.append("-")
    out = "".join(cleaned).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out[:120] or "run"
