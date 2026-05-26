"""adk_invocation_log.py — unconditional per-verb invocation ledger.

Appends one JSON line to $ADK_DATA_HOME/logs/invocations.jsonl on every
adk verb entry, and a second line on process exit. Concurrent writers are
serialized via fcntl.flock.

Never raises: all I/O is wrapped in try/except so a logging failure never
crashes an adk verb.
"""
from __future__ import annotations

import atexit
import fcntl
import json
import os
import sys
import time
from pathlib import Path


def _ledger_path() -> Path | None:
    val = os.environ.get("ADK_DATA_HOME")
    if not val:
        return None
    return Path(os.path.expanduser(val)) / "logs" / "invocations.jsonl"


def _append_line(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(".jsonl.lock")
    try:
        with open(lock_path, "a") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                with open(path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, separators=(",", ":")) + "\n")
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except OSError:
        pass


def record_invocation(verb: str) -> None:
    """Append a start record; register an atexit handler to append the exit record."""
    try:
        path = _ledger_path()
        if path is None:
            return
        pid = os.getpid()
        ts_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        start_record = {
            "ts": ts_start,
            "event": "start",
            "verb": verb,
            "argv": sys.argv[1:],
            "pid": pid,
            "cwd": os.getcwd(),
            "python_version": sys.version.split()[0],
        }
        _append_line(path, start_record)

        def _on_exit() -> None:
            try:
                _append_line(path, {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "event": "exit",
                    "verb": verb,
                    "pid": pid,
                })
            except Exception:
                pass

        atexit.register(_on_exit)
    except Exception:
        pass
