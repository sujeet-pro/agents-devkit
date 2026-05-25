"""Shared pytest config for skills/adk-pr-review/scripts/tests/."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Put the parent scripts/ dir on sys.path so tests can `import validate_findings`,
# `import _common`, etc.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config):
    """Set ADK_*_HOME env vars before any module imports so module-level
    constants (ADK_HOME, REPOS_ROOT, …) resolve without hard-failing."""
    _base = Path(tempfile.mkdtemp(prefix="adk-pr-review-test-"))
    os.environ.setdefault("ADK_DATA_HOME", str(_base / "data"))
    os.environ.setdefault("ADK_CONFIG_HOME", str(_base / "config"))
    os.environ.setdefault("ADK_MEMORY_HOME", str(_base / "memory"))
