"""Path resolution for adk config v5.

Wraps ``adk_home`` and adds the new learning-home path (under $ADK_MEMORY_HOME).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Self-bootstrap: make ``adk_home`` importable without callers having to set
# sys.path first. scripts/lib/ is the parent of this directory.
_LIB_DIR = Path(__file__).resolve().parent.parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from adk_home import (
    adk_config_home,
    adk_data_home,
    adk_logs_home,
    adk_memory_home,
    adk_repos_home,
    adk_skill_home,
)


def adk_learning_home() -> Path:
    """$ADK_MEMORY_HOME/learning — decisions.jsonl, sessions/, archive/, ..."""
    return adk_memory_home() / "learning"


def adk_metadata_home() -> Path:
    """$ADK_DATA_HOME/metadata — MCP introspection cache (regenerable scratch).

    Replaces the v4 ``$ADK_DATA_HOME/improve/metadata`` location.
    """
    return adk_data_home() / "metadata"


def config_path(*parts: str) -> Path:
    """Convenience: $ADK_CONFIG_HOME / part1 / part2 / ..."""
    return adk_config_home().joinpath(*parts)


def schema_dir() -> Path:
    """$ADK_CONFIG_HOME/schema — generated JSON Schema files."""
    return adk_config_home() / "schema"


__all__ = [
    "adk_config_home", "adk_data_home", "adk_memory_home",
    "adk_logs_home", "adk_repos_home", "adk_skill_home",
    "adk_learning_home", "adk_metadata_home",
    "config_path", "schema_dir",
]
