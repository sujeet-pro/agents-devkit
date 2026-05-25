"""Shared pytest config for skills/adk-cli/scripts/tests/."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Put the parent scripts/ dir on sys.path so tests can `import queue_io` etc.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config):
    """Set ADK_*_HOME env vars before any module imports so module-level
    constants (ADK_HOME, REPOS_ROOT, …) resolve without hard-failing."""
    _base = Path(tempfile.mkdtemp(prefix="adk-test-"))
    os.environ.setdefault("ADK_DATA_HOME", str(_base / "data"))
    os.environ.setdefault("ADK_CONFIG_HOME", str(_base / "config"))
    os.environ.setdefault("ADK_MEMORY_HOME", str(_base / "memory"))


@pytest.fixture(autouse=True)
def _adk_home_env(tmp_path_factory, monkeypatch):
    """Redirect ADK_*_HOME to tmp dirs so every test gets an isolated data dir.

    Uses tmp_path_factory.mktemp() with short neutral names rather than tmp_path
    so the resolved paths don't contain test-function names (which could cause
    false pattern-matches in scripts that grep their own argv).
    """
    base = tmp_path_factory.mktemp("adk")
    monkeypatch.setenv("ADK_DATA_HOME", str(base / "d"))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(base / "c"))
    monkeypatch.setenv("ADK_MEMORY_HOME", str(base / "m"))


@pytest.fixture(autouse=True)
def _isolate_tui_plan_path(tmp_path_factory, monkeypatch):
    """Redirect ADK_TUI_PLAN_PATH so pr_sync tests don't clobber the user's
    real synced tui/workers/sync-plan.json."""
    p = tmp_path_factory.mktemp("tui-plan") / "sync-plan.json"
    monkeypatch.setenv("ADK_TUI_PLAN_PATH", str(p))
