"""Tests for shared adk_log formatting helpers."""
from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import adk_log  # noqa: E402


def test_plain_formatter_scrubs_secret_values():
    formatter = adk_log._PlainFormatter()
    rec = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="loaded API_TOKEN=secret123", args=(), exc_info=None,
    )

    out = formatter.format(rec)

    assert "secret123" not in out
    assert "API_TOKEN=<redacted>" in out


def test_modern_formatter_indents_multiline_body():
    formatter = adk_log._ModernFormatter(color=False)
    rec = logging.LogRecord(
        name="pr-sync", level=logging.INFO, pathname="", lineno=0,
        msg="step\nsecond line", args=(), exc_info=None,
    )

    out = formatter.format(rec)

    assert "pr-sync" in out
    assert "step" in out
    assert "\n            ↳ second line" in out


def test_summary_box_plain_mode_for_non_tty(monkeypatch):
    monkeypatch.setenv("ADK_AGENT_MODE", "1")
    buf = io.StringIO()

    adk_log.print_summary_box("adk pr-sync", [("rows", 3)], stream=buf)

    assert "adk pr-sync" in buf.getvalue()
    assert "rows: 3" in buf.getvalue()


def test_run_event_round_trips():
    line = adk_log.encode_event(adk_log.RunEvent(
        kind="pr_active",
        pr_url="https://github.com/acme/foo/pull/42",
        status="run",
        stage="review agent",
    ))

    event = adk_log.parse_event_line(line)

    assert event["kind"] == "pr_active"
    assert event["pr_url"].endswith("/42")


def test_dashboard_moves_pr_between_sections():
    buf = io.StringIO()
    dashboard = adk_log.RunDashboard(
        run_id="run1", queue="/tmp/q.json5", runner="claude",
        parallel=1, selected=1, stream=buf,
    )

    dashboard.apply({"kind": "pr_wait", "pr_url": "https://github.com/acme/foo/pull/42"})
    dashboard.apply({"kind": "pr_active", "pr_url": "https://github.com/acme/foo/pull/42",
                     "stage": "review agent"})
    dashboard.apply({"kind": "pr_fail", "pr_url": "https://github.com/acme/foo/pull/42",
                     "stage": "review agent", "reason": "boom",
                     "log_path": "/tmp/foo.log"})
    out = dashboard.render()

    assert "gh:foo#42" in out
    assert "Active\n    wait  none" in out
    assert "fail" in out
    assert "boom" in out


def test_extract_failure_reason_prefers_exception_line(tmp_path):
    log = tmp_path / "child.log"
    log.write_text("noise\nRuntimeError: model missing\nlast line\n", encoding="utf-8")

    assert adk_log.extract_failure_reason(log) == "RuntimeError: model missing"
