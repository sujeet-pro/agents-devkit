"""Tests for the _handle_dashboard_event function promoted to module level in
auto_run.py.

Verifies that each scheduler event kind (stage_start, stage_done, stage_fail,
pr_done) appends exactly one line to pipeline.log with the expected glyph.

The test imports _handle_dashboard_event directly and constructs minimal stub
objects for the dashboard and append_log arguments, so no real subprocess or
network calls happen.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# sys.path bootstrap
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent

for _p in [str(SCRIPTS_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from auto_run import _handle_dashboard_event  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

_STUB_URL = "https://github.com/foo/bar/pull/42"
_STUB_STAGE = "index"


def _stub_dashboard() -> MagicMock:
    """Return a mock with apply() and print_snapshot() so nothing actually renders."""
    d = MagicMock()
    d.apply = MagicMock()
    d.print_snapshot = MagicMock()
    return d


@pytest.fixture
def pipeline_log(tmp_path) -> Path:
    """A fresh pipeline.log file under tmp_path (not yet existing)."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True)
    return logs_dir / "pipeline.log"


def _make_append_log(log_path: Path):
    """Return a callable that appends a line (prefixed with a fake timestamp) to log_path."""
    def _append(line: str) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"2026-01-01T00:00:00Z {line}\n")
    return _append


def _read_log_lines(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [ln.strip() for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_stage_start_writes_start_glyph(pipeline_log):
    """stage_start events tee a line starting with ▶ to pipeline.log."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "stage_start", "pr_url": _STUB_URL, "stage": _STUB_STAGE}
    _handle_dashboard_event(dashboard, append_log, ev)

    lines = _read_log_lines(pipeline_log)
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}: {lines}"
    assert "▶" in lines[0], f"Expected ▶ glyph in line: {lines[0]!r}"
    assert _STUB_STAGE in lines[0]
    assert _STUB_URL in lines[0]


def test_stage_done_writes_checkmark_glyph(pipeline_log):
    """stage_done events tee a line containing ✓ to pipeline.log."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "stage_done", "pr_url": _STUB_URL, "stage": _STUB_STAGE,
          "elapsed_s": 3.14}
    _handle_dashboard_event(dashboard, append_log, ev)

    lines = _read_log_lines(pipeline_log)
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}: {lines}"
    assert "✓" in lines[0], f"Expected ✓ glyph in line: {lines[0]!r}"
    assert _STUB_STAGE in lines[0]
    assert _STUB_URL in lines[0]


def test_stage_fail_writes_cross_glyph(pipeline_log):
    """stage_fail events tee a line containing ✗ to pipeline.log."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "stage_fail", "pr_url": _STUB_URL, "stage": _STUB_STAGE,
          "reason": "boom", "elapsed_s": 1.5}
    _handle_dashboard_event(dashboard, append_log, ev)

    lines = _read_log_lines(pipeline_log)
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}: {lines}"
    assert "✗" in lines[0], f"Expected ✗ glyph in line: {lines[0]!r}"
    assert "boom" in lines[0]


def test_pr_done_writes_bullet_glyph(pipeline_log):
    """pr_done events tee a line containing ● to pipeline.log."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "pr_done", "pr_url": _STUB_URL, "stage": "post"}
    _handle_dashboard_event(dashboard, append_log, ev)

    lines = _read_log_lines(pipeline_log)
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}: {lines}"
    assert "●" in lines[0], f"Expected ● glyph in line: {lines[0]!r}"
    assert _STUB_URL in lines[0]


def test_four_events_write_four_lines(pipeline_log):
    """Each event kind writes exactly one line; four events → four lines."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    events = [
        {"kind": "stage_start", "pr_url": _STUB_URL, "stage": "import"},
        {"kind": "stage_done",  "pr_url": _STUB_URL, "stage": "import", "elapsed_s": 0.5},
        {"kind": "stage_fail",  "pr_url": _STUB_URL, "stage": "sync", "reason": "net err", "elapsed_s": 0.1},
        {"kind": "pr_done",     "pr_url": _STUB_URL, "stage": "post"},
    ]
    for ev in events:
        _handle_dashboard_event(dashboard, append_log, ev)

    lines = _read_log_lines(pipeline_log)
    assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}: {lines}"


def test_stage_start_calls_dashboard_apply(pipeline_log):
    """stage_start must call dashboard.apply() and dashboard.print_snapshot()."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "stage_start", "pr_url": _STUB_URL, "stage": "sync"}
    _handle_dashboard_event(dashboard, append_log, ev)

    dashboard.apply.assert_called_once()
    dashboard.print_snapshot.assert_called_once()


def test_stage_fail_calls_dashboard_apply(pipeline_log):
    """stage_fail must call dashboard.apply() and dashboard.print_snapshot()."""
    dashboard = _stub_dashboard()
    append_log = _make_append_log(pipeline_log)

    ev = {"kind": "stage_fail", "pr_url": _STUB_URL, "stage": "review",
          "reason": "timeout"}
    _handle_dashboard_event(dashboard, append_log, ev)

    dashboard.apply.assert_called_once()
    dashboard.print_snapshot.assert_called_once()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
