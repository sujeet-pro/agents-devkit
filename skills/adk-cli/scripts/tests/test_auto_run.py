"""adk auto — headless review orchestrator tests."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest

import auto_run


def _write_queue(path: Path, prs: list[dict]) -> Path:
    path.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return path


def test_eligible_rows_filters_terminal_states(tmp_path):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "merged", "head_sha": "abc"},
        {"pr_url": "u2", "status": "closed", "head_sha": "def"},
        {"pr_url": "u3", "status": "pending", "head_sha": "ghi"},
    ])
    rows = auto_run._eligible_rows(qp, exclude=set())
    assert len(rows) == 1
    assert rows[0]["pr_url"] == "u3"


def test_eligible_rows_filters_excluded_urls(tmp_path):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc"},
        {"pr_url": "u2", "status": "pending", "head_sha": "def"},
    ])
    rows = auto_run._eligible_rows(qp, exclude={"u1"})
    assert [r["pr_url"] for r in rows] == ["u2"]


def test_eligible_rows_filters_already_reviewed_at_head(tmp_path):
    """When head_sha == last_reviewed_head_sha, the row is excluded."""
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "reviewed", "head_sha": "abc",
         "last_reviewed_head_sha": "abc"},  # same → not ready
        {"pr_url": "u2", "status": "reviewed", "head_sha": "new",
         "last_reviewed_head_sha": "old"},  # new commits → ready
    ])
    rows = auto_run._eligible_rows(qp, exclude=set())
    assert [r["pr_url"] for r in rows] == ["u2"]


def test_dry_run_lists_eligible_without_spawning(tmp_path, monkeypatch):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc"},
        {"pr_url": "u2", "status": "pending", "head_sha": "def"},
    ])
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    # capture stdout
    import io
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main(["--queue", str(qp), "--dry-run", "--no-sync"])
    monkeypatch.undo()
    assert rc == 0
    out = json.loads(captured.getvalue())
    assert out["action"] == "dry_run"
    assert set(out["would_review"]) == {"u1", "u2"}
    assert out["count"] == 2


def test_max_reviews_caps_eligible_set(tmp_path, monkeypatch):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc"},
        {"pr_url": "u2", "status": "pending", "head_sha": "def"},
        {"pr_url": "u3", "status": "pending", "head_sha": "ghi"},
    ])
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    import io
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main(["--queue", str(qp), "--dry-run", "--no-sync",
                        "--max-reviews", "2"])
    monkeypatch.undo()
    out = json.loads(captured.getvalue())
    assert out["count"] == 2


def test_no_eligible_returns_noop(tmp_path, monkeypatch):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "merged", "head_sha": "abc"},
    ])
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    import io
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main(["--queue", str(qp), "--no-sync"])
    monkeypatch.undo()
    out = json.loads(captured.getvalue())
    assert out["action"] == "noop"
    assert rc == 0


def test_missing_agent_binary_records_failure(tmp_path, monkeypatch):
    """When the agent binary isn't on PATH, _spawn_review returns failed."""
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    import logging
    log = logging.getLogger("test")
    result = auto_run._spawn_review(
        "u1", "this-binary-does-not-exist-9999",
        tmp_path / "run", log,
    )
    assert result["status"] == "failed"
    assert "not found" in result.get("error", "")


def test_report_md_written(tmp_path):
    """_write_report produces a markdown summary with one bullet per result."""
    results = [
        {"pr_url": "u1", "status": "ok", "exit_code": 0, "elapsed_s": 12.3},
        {"pr_url": "u2", "status": "failed", "exit_code": 1,
         "elapsed_s": 5.0, "error": "boom"},
    ]
    md = auto_run._write_report(tmp_path, results,
                                started="2026-05-21T00:00:00Z",
                                ended="2026-05-21T00:10:00Z",
                                ran_sync=True, dry_run=False)
    assert md.exists()
    body = md.read_text()
    assert "u1" in body and "u2" in body
    assert "ok: 1" in body and "failed: 1" in body
    assert "boom" in body
