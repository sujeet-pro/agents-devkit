"""adk pr-review-all — headless review orchestrator tests."""
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


def test_eligible_rows_preserves_queue_order(tmp_path):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u-newer", "status": "pending", "head_sha": "abc",
         "last_checked_at": "2026-05-21T17:15:00Z"},
        {"pr_url": "u-older", "status": "pending", "head_sha": "def",
         "last_checked_at": "2026-05-21T15:00:00Z"},
    ])
    rows = auto_run._eligible_rows(qp, exclude=set())
    assert [r["pr_url"] for r in rows] == ["u-newer", "u-older"]


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
    assert rows[0]["_adk_work_mode"] == "code"


def test_eligible_rows_includes_comment_only_change(tmp_path):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "comments", "head_sha": "abc",
         "last_reviewed_head_sha": "abc",
         "comment_activity_hash": "new",
         "last_reviewed_comment_activity_hash": "old"},
    ])
    rows = auto_run._eligible_rows(qp, exclude=set())
    assert [r["pr_url"] for r in rows] == ["u1"]
    assert rows[0]["_adk_work_mode"] == "comments"


def test_eligible_rows_includes_failed_attempt_resume(tmp_path):
    qp = _write_queue(tmp_path / "q.json5", [
        {"pr_url": "u1", "status": "comments", "head_sha": "abc",
         "last_reviewed_head_sha": "abc",
         "last_review_attempt_status": "failed",
         "last_review_attempt_at": "2026-05-25T00:00:00Z"},
    ])
    rows = auto_run._eligible_rows(qp, exclude=set())
    assert [r["pr_url"] for r in rows] == ["u1"]
    assert rows[0]["_adk_work_mode"] == "resume"


def test_parse_phase_marker_accepts_agent_prefixed_lines():
    assert auto_run._parse_phase_marker("[claude] phase 3: feature-flow") == (
        "phase 3: feature-flow"
    )
    assert auto_run._parse_phase_marker("ordinary log line") is None


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
    out = captured.getvalue()
    assert "Dry run" in out
    assert "u1" in out and "u2" in out


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
    out = captured.getvalue()
    assert "u1" in out and "u2" in out
    assert "u3" not in out


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
    out = captured.getvalue()
    assert "No eligible PRs" in out
    assert rc == 0


def test_cfg_reads_pr_review_all_from_adk_cli_json5(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"pr_review_all": {"runner": "cursor"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    sys.modules.pop("config_io", None)

    try:
        assert auto_run._cfg("runner", "claude") == "cursor"
    finally:
        sys.modules.pop("config_io", None)


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


def test_build_agent_cmd_claude_uses_print_prompt_shape():
    cmd = auto_run._build_agent_cmd("https://example/pr/1", runner="claude", agent=None)

    assert cmd == [
        "claude", "-p", "/adk-pr-review https://example/pr/1",
        "--model", "sonnet",
    ]


def test_build_agent_cmd_cursor_uses_cursor_agent_print_composer_model():
    cmd = auto_run._build_agent_cmd("https://example/pr/1", runner="cursor", agent=None)

    assert cmd[:7] == [
        "cursor", "agent", "--print", "--output-format", "text", "--force", "--trust",
    ]
    assert "--approve-mcps" in cmd
    assert "--sandbox" in cmd
    assert "disabled" in cmd
    assert "--model" in cmd
    assert "composer-2.5-fast" in cmd
    assert cmd[-1] == "/adk-pr-review https://example/pr/1"


def test_build_agent_cmd_cursor_can_pin_model():
    cmd = auto_run._build_agent_cmd(
        "https://example/pr/1",
        runner="cursor",
        agent=None,
        model="gpt-5",
    )

    assert "--model" in cmd
    assert "gpt-5" in cmd


def test_build_agent_cmd_deep_adds_prompt_flag_and_opus_model():
    cmd = auto_run._build_agent_cmd(
        "https://example/pr/1",
        runner="claude",
        agent=None,
        deep=True,
    )

    assert cmd == [
        "claude", "-p", "/adk-pr-review https://example/pr/1 --deep",
        "--model", "opus",
    ]


def test_build_agent_cmd_detailed_only_controls_prompt_embedding_flag():
    cmd = auto_run._build_agent_cmd(
        "https://example/pr/1",
        runner="claude",
        agent=None,
        detailed=True,
    )

    assert cmd == [
        "claude", "-p", "/adk-pr-review https://example/pr/1 --detailed",
        "--model", "sonnet",
    ]


def test_build_agent_cmd_rebuild_adds_prompt_flag():
    cmd = auto_run._build_agent_cmd(
        "https://example/pr/1",
        runner="claude",
        agent=None,
        rebuild=True,
    )

    assert cmd == [
        "claude", "-p", "/adk-pr-review https://example/pr/1 --rebuild",
        "--model", "sonnet",
    ]


def test_build_agent_cmd_comments_only_adds_prompt_flag():
    cmd = auto_run._build_agent_cmd(
        "https://example/pr/1",
        runner="claude",
        agent=None,
        work_mode="comments",
    )

    assert cmd == [
        "claude", "-p", "/adk-pr-review https://example/pr/1 --comments-only",
        "--model", "sonnet",
    ]


def test_auto_deep_complexity_uses_prepared_pr_stats():
    args = argparse.Namespace(deep=False, auto_deep=True)
    row = {"pr_url": "https://example/pr/1", "changed_files": 25}

    auto_run._annotate_depth([row], args)

    assert row["_adk_deep"] is True
    assert "25 files" in row["_adk_deep_reason"]


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


def test_review_result_prints_failure_reason(capsys):
    auto_run._print_review_result({
        "pr_url": "https://github.com/acme/foo/pull/42",
        "status": "failed",
        "exit_code": 1,
        "elapsed_s": 3.0,
        "reason": "RuntimeError: missing model",
        "log": "/tmp/foo.log",
    })

    out = capsys.readouterr().out
    assert "gh:foo#42" in out
    assert "RuntimeError: missing model" in out
