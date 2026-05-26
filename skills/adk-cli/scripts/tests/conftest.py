"""Shared pytest config for skills/adk-cli/scripts/tests/."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Put the parent scripts/ dir on sys.path so tests can `import queue_io` etc.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_LIB_DIR = SCRIPTS_DIR.parent.parent.parent / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
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
    # Reset the ConfigBundle singleton so each test gets a fresh load against
    # its own ADK_CONFIG_HOME rather than reusing a bundle cached by a prior test.
    try:
        from config import reset_bundle
        reset_bundle()
    except Exception:
        pass
    yield
    try:
        from config import reset_bundle
        reset_bundle()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _isolate_tui_plan_path(tmp_path_factory, monkeypatch):
    """Redirect ADK_TUI_PLAN_PATH so pr_sync tests don't clobber the user's
    real synced tui/workers/sync-plan.json."""
    p = tmp_path_factory.mktemp("tui-plan") / "sync-plan.json"
    monkeypatch.setenv("ADK_TUI_PLAN_PATH", str(p))


@pytest.fixture(autouse=True)
def _stub_slack_post_validator(monkeypatch):
    """Default-stub the AI validator so existing tests don't shell out to
    `claude -p` (which would hit a 30s timeout in CI). Tests that specifically
    exercise the validator can override by re-monkey-patching either the
    `validate_slack_post` symbol in the consuming module (e.g. `pr_scan`) or
    the validator's own `_subprocess_run` seam.
    """
    def _passthrough(payload, **kwargs):
        return {"should_post": True, "reason": "stubbed",
                "improved_text": None, "confidence": 1.0}
    # Stub the points where it's imported into consuming modules. We leave
    # `slack_post_validator.validate_slack_post` itself untouched so the
    # validator's own test file can drive it through `_subprocess_run`.
    for mod_name in ("pr_scan", "pr_reminders"):
        try:
            mod = __import__(mod_name)
        except ImportError:
            continue
        if hasattr(mod, "validate_slack_post"):
            monkeypatch.setattr(mod, "validate_slack_post", _passthrough,
                                raising=False)
