"""Tests for generic `adk skill-run` harness selection."""
from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import agent_harness
import skill_run


def test_resolve_runner_model_defaults():
    assert agent_harness.resolve_runner_model(runner="claude") == "sonnet"
    assert agent_harness.resolve_runner_model(runner="claude", deep=True) == "opus"
    assert agent_harness.resolve_runner_model(runner="cursor") == "composer-2.5-fast"
    assert agent_harness.resolve_runner_model(runner="cursor", deep=True) == "gpt-5.5-extra-high"
    assert agent_harness.resolve_runner_model(runner="cursor", explicit_model="inherit") is None


def test_skill_prompt_forwards_depth_flags():
    prompt = skill_run._prompt_for(
        "implement",
        ["build", "x"],
        detailed=True,
        deep=True,
    )

    assert prompt == "/adk-implement build x --detailed --deep"


def test_skill_run_dry_run_inherits_cursor_model_by_default(capsys):
    rc = skill_run.main([
        "--runner", "cursor",
        "--dry-run",
        "review",
        "--",
        ".",
    ])

    assert rc == 0
    out = capsys.readouterr().out
    assert "cursor agent" in out
    assert "--model" not in out
    assert "'/adk-review .'" in out or "/adk-review ." in out
