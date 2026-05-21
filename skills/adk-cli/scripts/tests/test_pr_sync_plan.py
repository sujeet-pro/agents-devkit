"""Tests for skills/adk-cli/scripts/tui_plan.py (the SyncPlanWriter) and the
pr_sync integration that drives it. Companion to test_pr_sync.py — the
writer is purely additive; pre-existing tests still cover the CLI surface.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import tui_plan
from tui_plan import SyncPlanWriter


# --------------------------------------------------------------------- unit


def test_writer_init_writes_initial_file(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    SyncPlanWriter(
        queue="/tmp/q.json5",
        argv=["--no-scan"],
        step_names=["a", "b"],
        path=plan,
    )
    assert plan.exists()
    raw = json.loads(plan.read_text())
    assert raw["version"] == 1
    assert raw["queue"] == "/tmp/q.json5"
    assert raw["argv"] == ["--no-scan"]
    assert raw["completed_at"] is None
    assert raw["rc"] is None
    assert [s["name"] for s in raw["steps"]] == ["a", "b"]
    assert all(s["status"] == "pending" for s in raw["steps"])
    assert all(s["rc"] is None for s in raw["steps"])
    assert all(s["started_at"] is None for s in raw["steps"])
    assert all(s["completed_at"] is None for s in raw["steps"])


def test_step_start_marks_running(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a", "b"], path=plan)
    w.step_start("a")
    raw = json.loads(plan.read_text())
    a = raw["steps"][0]
    assert a["status"] == "running"
    assert a["started_at"] is not None
    assert a["completed_at"] is None
    # Sibling stays pending.
    assert raw["steps"][1]["status"] == "pending"


def test_step_done_marks_terminal_with_rc(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a"], path=plan)
    w.step_start("a")
    w.step_done("a", status="ok", rc=0)
    raw = json.loads(plan.read_text())
    a = raw["steps"][0]
    assert a["status"] == "ok"
    assert a["rc"] == 0
    assert a["completed_at"] is not None


def test_step_done_warn_and_failed_statuses_persist(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a", "b"], path=plan)
    w.step_done("a", status="warn", rc=1)
    w.step_done("b", status="failed", rc=2)
    raw = json.loads(plan.read_text())
    assert raw["steps"][0]["status"] == "warn"
    assert raw["steps"][0]["rc"] == 1
    assert raw["steps"][1]["status"] == "failed"
    assert raw["steps"][1]["rc"] == 2


def test_finish_sets_top_level_rc_and_completed_at(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a"], path=plan)
    w.finish(rc=0)
    raw = json.loads(plan.read_text())
    assert raw["completed_at"] is not None
    assert raw["rc"] == 0


def test_writer_tolerant_of_unknown_step_name(tmp_path: Path) -> None:
    """SPEC §3.1: unknown step name appends a new step on the fly."""
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a"], path=plan)
    w.step_start("brand-new-step")
    w.step_done("brand-new-step", status="ok", rc=0)
    raw = json.loads(plan.read_text())
    names = [s["name"] for s in raw["steps"]]
    assert names == ["a", "brand-new-step"]
    assert raw["steps"][1]["status"] == "ok"


def test_writer_no_lingering_tmp_file(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    w = SyncPlanWriter(queue="q", argv=[], step_names=["a"], path=plan)
    w.step_start("a")
    w.step_done("a", status="ok", rc=0)
    w.finish(rc=0)
    # The atomic-replace pattern uses plan.json.tmp; it must not linger.
    assert not (tmp_path / "plan.json.tmp").exists()


def test_plan_path_honors_env_var(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "custom" / "plan.json"
    monkeypatch.setenv("ADK_TUI_PLAN_PATH", str(target))
    assert tui_plan.plan_path() == target


def test_plan_path_default_when_env_unset(monkeypatch) -> None:
    monkeypatch.delenv("ADK_TUI_PLAN_PATH", raising=False)
    assert tui_plan.plan_path() == tui_plan.DEFAULT_PLAN_PATH


# ----------------------------------------------------------- integration


def test_pr_sync_emits_plan_with_eight_steps(tmp_path: Path) -> None:
    """End-to-end: spawn pr_sync.py as a subprocess with every `--no-*` flag
    set so it has zero real work to do. The plan file MUST exist after the
    run, with 8 step entries and a top-level rc.
    """
    scripts_dir = Path(__file__).resolve().parent.parent
    queue = tmp_path / "empty.json5"
    queue.write_text('{"filters": null, "prs": []}')
    plan = tmp_path / "plan.json"

    env = dict(os.environ)
    env["ADK_TUI_PLAN_PATH"] = str(plan)
    # Ensure the child's import path resolves sibling scripts.
    env["PYTHONPATH"] = str(scripts_dir) + os.pathsep + env.get("PYTHONPATH", "")

    cmd = [
        sys.executable,
        str(scripts_dir / "pr_sync.py"),
        "--no-scan",
        "--no-clean-orphans",
        "--no-remind",
        "--no-prepare",
        "--no-base-audit",
        "--no-auto-demote",
        "--queue",
        str(queue),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(scripts_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # We don't assert proc.returncode strictly — the two non-skipped steps
    # (pr-queue update --all + pr-queue clean) may warn on the empty queue,
    # but pr_sync returns rc=0 unless a step CRASHED.
    assert plan.exists(), (
        f"plan file missing\nstdout: {proc.stdout!r}\nstderr: {proc.stderr!r}"
    )
    raw = json.loads(plan.read_text())
    assert raw["version"] == 1
    assert raw["completed_at"] is not None
    assert raw["rc"] is not None
    assert len(raw["steps"]) == 8
    names = [s["name"] for s in raw["steps"]]
    assert names == [
        "pr-scan",
        "pr-queue update --all",
        "pr-queue clean (merged)",
        "pr-task clean-orphans",
        "pr-queue remind",
        "base-index audit",
        "auto-base cleanup",
        "pr-task prepare --all",
    ]
    # The 6 --no-* steps must all be marked skipped.
    by_name = {s["name"]: s for s in raw["steps"]}
    for skipped_name in (
        "pr-scan",
        "pr-task clean-orphans",
        "pr-queue remind",
        "base-index audit",
        "auto-base cleanup",
        "pr-task prepare --all",
    ):
        assert by_name[skipped_name]["status"] == "skipped", (
            f"{skipped_name} should be skipped, got {by_name[skipped_name]}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
