"""Shared pytest config for skills/adk-cli/scripts/tests/."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Put the parent scripts/ dir on sys.path so tests can `import queue_io` etc.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture(autouse=True)
def _isolate_tui_plan_path(tmp_path_factory, monkeypatch):
    """Redirect ADK_TUI_PLAN_PATH so pr_sync tests don't clobber the user's
    real ~/.agents-devkit/tui/workers/sync-plan.json."""
    p = tmp_path_factory.mktemp("tui-plan") / "sync-plan.json"
    monkeypatch.setenv("ADK_TUI_PLAN_PATH", str(p))
