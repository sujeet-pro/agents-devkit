"""Unit tests for tui/model/workers_model.py — θ.

Each test injects `now_fn` so the suite is independent of wall-clock time.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tui.model.workers_model import WorkerRow, WorkersModel


# Anchor "now" matches conftest.workers_dir_with_two / stale_worker_file fixtures:
# fresh files use 2026-05-22T14:00:00Z, stale uses 2026-05-22T13:55:00Z.
_NOW = datetime(2026, 5, 22, 14, 0, 30, tzinfo=timezone.utc)


def _now_fn() -> datetime:
    return _NOW


def _write_heartbeat(d: Path, pid: int, *, last_heartbeat: str, pr_url: str = "https://github.com/acme/x/pull/1") -> Path:
    p = d / f"{pid}.json"
    p.write_text(
        json.dumps(
            {
                "pid": pid,
                "pr_url": pr_url,
                "task_type": "review",
                "agent": "claude",
                "queue": "/tmp/q",
                "started_at": last_heartbeat,
                "last_heartbeat": last_heartbeat,
                "current_phase": "review",
                "rc": None,
            }
        )
    )
    return p


def test_snapshot_empty_dir(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    assert model.snapshot() == []
    # has_changed() should be False on the second call once we've taken a snapshot.
    assert model.has_changed() is False


def test_snapshot_missing_dir_returns_empty(tmp_path: Path) -> None:
    d = tmp_path / "does-not-exist"
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    assert model.snapshot() == []


def test_snapshot_returns_two_fresh_rows(workers_dir_with_two: Path) -> None:
    model = WorkersModel(
        workers_dir=workers_dir_with_two,
        stale_after_s=30.0,
        now_fn=_now_fn,
    )
    rows = model.snapshot()
    assert len(rows) == 2
    for r in rows:
        assert isinstance(r, WorkerRow)
        assert r.is_stale is False
        assert r.task_type == "review"
        assert r.agent == "claude"
        assert r.age_s == 30.0  # _NOW − 14:00:00Z
    # pids preserved from fixtures
    pids = sorted(r.pid for r in rows)
    assert pids == [11111, 22222]


def test_snapshot_marks_stale_file(stale_worker_file: Path) -> None:
    model = WorkersModel(
        workers_dir=stale_worker_file,
        stale_after_s=30.0,
        now_fn=_now_fn,
    )
    rows = model.snapshot()
    assert len(rows) == 1
    r = rows[0]
    assert r.is_stale is True
    # 5 min 30 s gap from 13:55 → 14:00:30
    assert r.age_s > 30.0
    assert r.pid == 99999


def test_snapshot_skips_corrupt_json(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    # One valid + one corrupt file
    _write_heartbeat(d, 11111, last_heartbeat="2026-05-22T14:00:00Z")
    (d / "22222.json").write_text("{ this is not json")
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    rows = model.snapshot()
    assert len(rows) == 1
    assert rows[0].pid == 11111


def test_snapshot_skips_row_missing_last_heartbeat(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    (d / "1.json").write_text(json.dumps({"pid": 1, "pr_url": "x"}))  # no last_heartbeat
    _write_heartbeat(d, 2, last_heartbeat="2026-05-22T14:00:00Z")
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    rows = model.snapshot()
    assert len(rows) == 1
    assert rows[0].pid == 2


def test_gc_removes_files_older_than_threshold(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    # Fresh row — well within gc_after_s.
    fresh = _write_heartbeat(d, 11111, last_heartbeat="2026-05-22T14:00:00Z")
    # Ancient row — 1 day in the past.
    ancient = _write_heartbeat(d, 99999, last_heartbeat="2026-05-21T14:00:00Z")
    model = WorkersModel(
        workers_dir=d,
        stale_after_s=30.0,
        gc_after_s=120.0,
        now_fn=_now_fn,
    )
    removed = model.gc()
    assert removed == 1
    assert fresh.exists()
    assert not ancient.exists()


def test_gc_handles_empty_dir(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    assert model.gc() == 0


def test_has_changed_detects_new_file(tmp_path: Path) -> None:
    d = tmp_path / "workers"
    d.mkdir()
    model = WorkersModel(workers_dir=d, now_fn=_now_fn)
    # Initial snapshot stores signature → has_changed() False.
    model.snapshot()
    assert model.has_changed() is False
    # New file appears.
    _write_heartbeat(d, 31337, last_heartbeat="2026-05-22T14:00:00Z")
    assert model.has_changed() is True
    # Subsequent snapshot resets the cached signature.
    model.snapshot()
    assert model.has_changed() is False


def test_now_fn_injection_is_respected(workers_dir_with_two: Path) -> None:
    """Confirm staleness is driven by the injected `now_fn`, not wall clock."""

    def future_now() -> datetime:
        return _NOW + timedelta(minutes=10)

    model = WorkersModel(
        workers_dir=workers_dir_with_two,
        stale_after_s=30.0,
        now_fn=future_now,
    )
    rows = model.snapshot()
    assert len(rows) == 2
    assert all(r.is_stale for r in rows)
