"""Tests for the narration helpers in _common.

The orchestrator runs as a single subprocess under `claude -p`, so we use
these to emit a phase-by-phase progress trail to BOTH stdout (visible to
the agent in the Bash tool result) and a sidecar `<task_dir>/narration.log`
the user can `tail -f` in another terminal.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import _common


def test_narrate_banner_emits_paths_and_url(tmp_path, capsys):
    _common.narrate_banner(tmp_path, url="https://bitbucket.org/x/y/pull-requests/1")
    out = capsys.readouterr().out
    assert "Working on bb:y#1" in out
    assert f"task: {tmp_path}" in out
    assert f"full log: {tmp_path / 'review.log'}" in out
    assert f"live trace: {tmp_path / 'narration.log'}" in out
    # Sidecar contains the same content as stdout.
    assert (tmp_path / "narration.log").read_text().count("[narrate]") == 4


def test_narrate_start_and_done_show_phase_id(tmp_path, capsys):
    _common.narrate_start(tmp_path, "1a", "ensure repo clone")
    _common.narrate_done(tmp_path, "1a")
    out = capsys.readouterr().out
    assert "Phase 1a  ensure repo clone" in out
    assert "Phase 1a  ok" in out


def test_narrate_done_records_duration(tmp_path, capsys):
    import time
    _common.narrate_start(tmp_path, "0", "prereq")
    time.sleep(0.02)
    _common.narrate_done(tmp_path, "0", note="embed=nomic-embed-text")
    out = capsys.readouterr().out
    # Some duration token appears (either Nms or Ns), followed by the note.
    assert "(embed=nomic-embed-text)" in out
    # And the duration is non-empty (at least one digit followed by ms or s).
    import re
    assert re.search(r"\b\d+(ms|s)\b", out), out


def test_narrate_done_failed_status(tmp_path, capsys):
    _common.narrate_start(tmp_path, "1b", "worktree at abc123")
    _common.narrate_done(tmp_path, "1b", status="failed", note="sha not reachable")
    out = capsys.readouterr().out
    assert "Phase 1b  failed" in out
    assert "sha not reachable" in out


def test_narrate_summary_includes_log_path(tmp_path, capsys):
    _common.narrate_summary(tmp_path, status="ready for review",
                            head_sha="a2ab692a4db6", incremental=True)
    out = capsys.readouterr().out
    assert "ready for review" in out
    assert "head: a2ab692a4db6" in out
    assert "index: incremental" in out
    assert f"log: {tmp_path / 'review.log'}" in out


def test_narrate_sidecar_log_is_appendable(tmp_path, capsys):
    """Sidecar should append, not truncate — the user might tail -f it
    across multiple narrate_* calls in the same run."""
    _common.narrate_banner(tmp_path, url="x")
    _common.narrate_start(tmp_path, "0", "first")
    _common.narrate_done(tmp_path, "0")
    body1 = (tmp_path / "narration.log").read_text()
    _common.narrate_start(tmp_path, "1", "second")
    _common.narrate_done(tmp_path, "1")
    body2 = (tmp_path / "narration.log").read_text()
    assert body2.startswith(body1)
    assert len(body2) > len(body1)


def test_narrate_done_without_start_does_not_raise(tmp_path, capsys):
    """If the user runs narrate_done before narrate_start (e.g. error path
    that skipped the start), we should not raise — just emit with a blank
    duration."""
    _common.narrate_done(tmp_path, "9z", status="skipped")
    out = capsys.readouterr().out
    assert "Phase 9z" in out
    assert "skipped" in out


def test_narrate_handles_missing_task_dir_gracefully(capsys):
    """Sidecar is best-effort — if task_dir doesn't exist and can't be
    created, we still print to stdout."""
    bogus = Path("/nonexistent-root/that/should-never-exist/task")
    # Should not raise.
    _common.narrate_banner(bogus, url="x")
    out = capsys.readouterr().out
    assert "Working on x" in out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
