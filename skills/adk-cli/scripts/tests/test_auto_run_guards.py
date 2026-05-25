"""P9 safety guards: --quiet-hours, --max-cost-usd, --report-to-slack."""
from __future__ import annotations

import datetime
import io
import json
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import pytest
import auto_run


def test_parse_quiet_hours_simple():
    assert auto_run._parse_quiet_hours("00-08") == (0, 8)
    assert auto_run._parse_quiet_hours("22-06") == (22, 6)
    assert auto_run._parse_quiet_hours("9-17") == (9, 17)


def test_parse_quiet_hours_invalid():
    with pytest.raises(ValueError):
        auto_run._parse_quiet_hours("not-a-range")
    with pytest.raises(ValueError):
        auto_run._parse_quiet_hours("25-30")


def test_in_quiet_hours_simple_window():
    """'00-08' includes 02:00, excludes 08:00 and 14:00."""
    inside = datetime.datetime(2026, 5, 21, 2, 0)
    on_edge = datetime.datetime(2026, 5, 21, 8, 0)
    outside = datetime.datetime(2026, 5, 21, 14, 0)
    assert auto_run._in_quiet_hours("00-08", now=inside) is True
    assert auto_run._in_quiet_hours("00-08", now=on_edge) is False
    assert auto_run._in_quiet_hours("00-08", now=outside) is False


def test_in_quiet_hours_wrap_around():
    """'22-06' covers 23:00, 02:00; excludes 12:00."""
    late = datetime.datetime(2026, 5, 21, 23, 0)
    early = datetime.datetime(2026, 5, 22, 2, 0)
    midday = datetime.datetime(2026, 5, 21, 12, 0)
    assert auto_run._in_quiet_hours("22-06", now=late) is True
    assert auto_run._in_quiet_hours("22-06", now=early) is True
    assert auto_run._in_quiet_hours("22-06", now=midday) is False


def test_quiet_hours_empty_spec_returns_false():
    assert auto_run._in_quiet_hours("", now=datetime.datetime(2026, 5, 21, 2)) is False
    assert auto_run._in_quiet_hours(None, now=datetime.datetime(2026, 5, 21, 2)) is False


def test_dry_run_includes_guard_flags_in_output(tmp_path, monkeypatch):
    qp = tmp_path / "q.json5"
    qp.write_text(json.dumps({"prs": [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc"},
    ]}))
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main([
        "--queue", str(qp), "--dry-run", "--no-sync",
        "--runner", "claude",
        "--quiet-hours", "00-01",  # very narrow; unlikely to trigger
        "--max-cost-usd", "100",
        "--report-to-slack", "#test",
    ])
    monkeypatch.undo()
    # Either it returned 2 (we were in 00-01) OR 0 with the flags echoed.
    if rc == 0:
        out = json.loads(captured.getvalue())
        assert out["action"] == "dry_run"
        assert out["quiet_hours"] == "00-01"
        assert out["max_cost_usd"] == 100
        assert out["report_to_slack"] == "#test"
        assert out["runner"] in {"claude", "cursor", "codex", "custom"}


def test_max_cost_aborts_when_estimate_exceeds(tmp_path, monkeypatch):
    """3 eligible × $0.50/claude = $1.50; --max-cost-usd 1 aborts."""
    qp = tmp_path / "q.json5"
    qp.write_text(json.dumps({"prs": [
        {"pr_url": f"u{i}", "status": "pending", "head_sha": f"s{i}"}
        for i in range(3)
    ]}))
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main([
        "--queue", str(qp), "--no-sync",
        "--runner", "claude",
        "--max-cost-usd", "1.00",
    ])
    monkeypatch.undo()
    assert rc == 2
    out = json.loads(captured.getvalue())
    assert out["action"] == "aborted"
    assert "max-cost-usd" in out["reason"]


def test_max_cost_passes_when_estimate_below(tmp_path, monkeypatch):
    """3 eligible × $0.50 = $1.50; --max-cost-usd 2 passes (proceeds to dry-run)."""
    qp = tmp_path / "q.json5"
    qp.write_text(json.dumps({"prs": [
        {"pr_url": f"u{i}", "status": "pending", "head_sha": f"s{i}"}
        for i in range(3)
    ]}))
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main([
        "--queue", str(qp), "--no-sync", "--dry-run",
        "--max-cost-usd", "2.00",
    ])
    monkeypatch.undo()
    assert rc == 0


def test_max_cost_uses_runner_cost_for_cursor(tmp_path, monkeypatch):
    """3 eligible × $0.30/cursor = $0.90; --max-cost-usd 1 passes."""
    qp = tmp_path / "q.json5"
    qp.write_text(json.dumps({"prs": [
        {"pr_url": f"u{i}", "status": "pending", "head_sha": f"s{i}"}
        for i in range(3)
    ]}))
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main([
        "--queue", str(qp), "--no-sync", "--dry-run",
        "--runner", "cursor",
        "--max-cost-usd", "1.00",
    ])
    monkeypatch.undo()
    assert rc == 0
    out = json.loads(captured.getvalue())
    assert out["runner"] == "cursor"


def test_quiet_hours_aborts_inside_window(tmp_path, monkeypatch):
    """Force the window to be 'in effect' → main() aborts with rc=2."""
    qp = tmp_path / "q.json5"
    qp.write_text(json.dumps({"prs": [{"pr_url": "u1", "status": "pending"}]}))
    monkeypatch.setattr(auto_run, "AUTO_RUNS_ROOT", tmp_path / "auto-runs")
    monkeypatch.setattr(auto_run, "_in_quiet_hours", lambda spec, now=None: True)
    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    rc = auto_run.main([
        "--queue", str(qp), "--no-sync",
        "--quiet-hours", "00-08",
    ])
    monkeypatch.undo()
    assert rc == 2
    out = json.loads(captured.getvalue())
    assert out["action"] == "aborted"
    assert "quiet-hours" in out["reason"]
