"""Tests for `adk pr-queue clean --stale-days N` (improvement #10).

The clean subcommand must:
  - skip rows that are STATUS_IN_REVIEW
  - skip rows that have `taken_at` set (actively locked)
  - drop rows older than N days, with --yes confirmation
  - return 2 (refuse) without --yes
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def pr_queue_mod():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import pr_queue
    return pr_queue


def _ts_n_days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_queue(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"prs": rows}, indent=2), encoding="utf-8")


def test_row_age_days_parses_iso(pr_queue_mod):
    assert pr_queue_mod._row_age_days({"last_checked_at": _ts_n_days_ago(30)}) >= 29
    assert pr_queue_mod._row_age_days({"last_checked_at": _ts_n_days_ago(1)}) < 2


def test_row_age_days_handles_missing(pr_queue_mod):
    assert pr_queue_mod._row_age_days({}) is None
    assert pr_queue_mod._row_age_days({"last_checked_at": ""}) is None
    assert pr_queue_mod._row_age_days({"last_checked_at": "not-a-date"}) is None


def test_clean_stale_days_refuses_without_yes(tmp_path, pr_queue_mod):
    q = tmp_path / "pr-queue.json5"
    _write_queue(q, [
        {"pr_url": "https://github.com/a/b/pull/1", "status": "reviewed",
         "last_checked_at": _ts_n_days_ago(30)},
    ])
    args = type("A", (), {"queue": str(q), "all": False, "stale_days": 7, "yes": False})()
    rc = pr_queue_mod.cmd_clean(args)
    assert rc == 2
    # Queue untouched.
    rows = json.loads(q.read_text(encoding="utf-8"))["prs"]
    assert len(rows) == 1


def test_clean_stale_days_drops_old_rows(tmp_path, pr_queue_mod, monkeypatch):
    q = tmp_path / "pr-queue.json5"
    _write_queue(q, [
        {"pr_url": "https://github.com/a/b/pull/1", "status": "reviewed",
         "last_checked_at": _ts_n_days_ago(30)},
        {"pr_url": "https://github.com/a/b/pull/2", "status": "reviewed",
         "last_checked_at": _ts_n_days_ago(1)},
    ])
    monkeypatch.setattr(pr_queue_mod, "_task_dir_for_link", lambda link: None)  # no folder cleanup
    args = type("A", (), {"queue": str(q), "all": False, "stale_days": 7, "yes": True})()
    rc = pr_queue_mod.cmd_clean(args)
    assert rc == 0
    rows = json.loads(q.read_text(encoding="utf-8"))["prs"]
    assert len(rows) == 1
    assert rows[0]["pr_url"].endswith("/pull/2")


def test_clean_stale_days_skips_in_review(tmp_path, pr_queue_mod, monkeypatch):
    q = tmp_path / "pr-queue.json5"
    _write_queue(q, [
        {"pr_url": "https://github.com/a/b/pull/1", "status": "in_review",
         "last_checked_at": _ts_n_days_ago(30)},
    ])
    monkeypatch.setattr(pr_queue_mod, "_task_dir_for_link", lambda link: None)
    args = type("A", (), {"queue": str(q), "all": False, "stale_days": 7, "yes": True})()
    rc = pr_queue_mod.cmd_clean(args)
    assert rc == 0
    rows = json.loads(q.read_text(encoding="utf-8"))["prs"]
    assert len(rows) == 1  # in_review row preserved


def test_clean_stale_days_skips_locked(tmp_path, pr_queue_mod, monkeypatch):
    """taken_at set → row is actively being reviewed → don't sweep it."""
    q = tmp_path / "pr-queue.json5"
    _write_queue(q, [
        {"pr_url": "https://github.com/a/b/pull/1", "status": "reviewed",
         "last_checked_at": _ts_n_days_ago(30), "taken_at": _ts_now()},
    ])
    monkeypatch.setattr(pr_queue_mod, "_task_dir_for_link", lambda link: None)
    args = type("A", (), {"queue": str(q), "all": False, "stale_days": 7, "yes": True})()
    rc = pr_queue_mod.cmd_clean(args)
    assert rc == 0
    assert len(json.loads(q.read_text(encoding="utf-8"))["prs"]) == 1


def test_clean_stale_days_rejects_zero(tmp_path, pr_queue_mod):
    q = tmp_path / "pr-queue.json5"
    _write_queue(q, [{"pr_url": "x", "last_checked_at": _ts_n_days_ago(1)}])
    args = type("A", (), {"queue": str(q), "all": False, "stale_days": 0, "yes": True})()
    rc = pr_queue_mod.cmd_clean(args)
    assert rc == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
