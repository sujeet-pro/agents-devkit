"""Shared pytest config for scripts/lib/pr_pipeline/tests/."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Put pr_pipeline's parent (scripts/lib/) on sys.path so tests can
# `import pr_pipeline.state` etc. without installing the package.
_LIB_DIR = Path(__file__).resolve().parents[2]
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))


def pytest_configure(config):
    """Set ADK_*_HOME env vars before any module imports."""
    _base = Path(tempfile.mkdtemp(prefix="adk-pipeline-test-"))
    os.environ.setdefault("ADK_DATA_HOME", str(_base / "data"))
    os.environ.setdefault("ADK_CONFIG_HOME", str(_base / "config"))
    os.environ.setdefault("ADK_MEMORY_HOME", str(_base / "memory"))
