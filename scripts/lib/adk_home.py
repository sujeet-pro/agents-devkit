"""adk_home.py — resolve adk home paths from env vars.

Required env vars (set in ~/.zshenv from ~/personal/mac-setup/configs/shell/.zshenv.example):
  ADK_DATA_HOME    machine-local data root (e.g. ~/adk-data)
  ADK_CONFIG_HOME  config root (synced, e.g. ~/user-synced-data/adk/config)
  ADK_MEMORY_HOME  memory root (synced, e.g. ~/user-synced-data/adk/memory)

Hard fails if any required var is unset.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path


_FIX_HINT = (
    "set it in ~/.zshenv (see ~/personal/mac-setup/configs/shell/.zshenv.example), "
    "then `source ~/.zshenv` in a fresh shell."
)


def _require(name: str) -> Path:
    val = os.environ.get(name)
    if not val:
        sys.stderr.write(f"adk: required env var {name} is unset — {_FIX_HINT}\n")
        sys.exit(2)
    return Path(os.path.expanduser(val))


def adk_data_home() -> Path:
    return _require("ADK_DATA_HOME")


def adk_config_home() -> Path:
    return _require("ADK_CONFIG_HOME")


def adk_memory_home() -> Path:
    return _require("ADK_MEMORY_HOME")


def adk_logs_home() -> Path:
    return adk_data_home() / "logs"


def adk_learning_home() -> Path:
    """$ADK_MEMORY_HOME/learning — decisions.jsonl, sessions/, archive/, ..."""
    return adk_memory_home() / "learning"


def adk_metadata_home() -> Path:
    """$ADK_DATA_HOME/metadata — MCP introspection cache (regenerable scratch)."""
    return adk_data_home() / "metadata"


def adk_repos_home() -> Path:
    return adk_data_home() / "repos"


def adk_skill_home(skill_stem: str) -> Path:
    return adk_data_home() / f"skill-{skill_stem}"


__all__ = [
    "adk_data_home", "adk_config_home", "adk_memory_home", "adk_logs_home",
    "adk_learning_home", "adk_metadata_home",
    "adk_repos_home", "adk_skill_home",
]
