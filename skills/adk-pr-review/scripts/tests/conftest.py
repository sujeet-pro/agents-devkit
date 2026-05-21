"""Shared pytest config for skills/adk-pr-review/scripts/tests/."""
from __future__ import annotations

import sys
from pathlib import Path

# Put the parent scripts/ dir on sys.path so tests can `import validate_findings`,
# `import _common`, etc.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
