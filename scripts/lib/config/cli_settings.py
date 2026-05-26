"""adk-cli.json5 + tui-prefs.json + identity.json — small unschemaed configs.

These files hold CLI behavior knobs / tiny caches, not entity data. They don't
need the full ConfigBundle treatment — but they DO need to live alongside it,
so callers have one import for "all config under $ADK_CONFIG_HOME".

Public API:
    from scripts.lib.config import get_adk_cli, load_adk_cli
    from scripts.lib.config import load_tui_prefs, save_tui_prefs
    from scripts.lib.config import load_identity_cache, save_identity_cache

`get_adk_cli(*path, default=None)` — dotted-path lookup into adk-cli.json5,
preserving the v4 API exactly so all skill scripts can switch their import line
without changing the call sites.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import json5

from .paths import adk_config_home


# ---------------------------------------------------------------------------
# adk-cli.json5 — CLI/TUI behavior knobs
# ---------------------------------------------------------------------------


def _adk_cli_path() -> Path:
    return adk_config_home() / "adk-cli.json5"


def load_adk_cli() -> dict:
    """Return adk-cli.json5 as a dict, or {} if absent."""
    p = _adk_cli_path()
    if not p.exists():
        return {}
    try:
        return json5.loads(p.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise RuntimeError(f"{p}: failed to parse JSON5: {e}") from e


def get_adk_cli(*path: str, default: Any = None) -> Any:
    """Dotted-path lookup into adk-cli.json5.

    Example:
        get_adk_cli("pr_sync", "audit_mode", default="act")
    """
    cfg: Any = load_adk_cli()
    for key in path:
        if not isinstance(cfg, dict) or key not in cfg:
            return default
        cfg = cfg[key]
    return cfg


# ---------------------------------------------------------------------------
# tui-prefs.json — small TUI preferences sidecar
# ---------------------------------------------------------------------------


def _tui_prefs_path() -> Path:
    return adk_config_home() / "tui-prefs.json"


def load_tui_prefs() -> dict:
    p = _tui_prefs_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def save_tui_prefs(prefs: dict) -> None:
    p = _tui_prefs_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# identity.json — cached github_login (small TUI cache)
# ---------------------------------------------------------------------------


def _identity_path() -> Path:
    return adk_config_home() / "identity.json"


def load_identity_cache() -> dict:
    p = _identity_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def save_identity_cache(data: dict) -> None:
    p = _identity_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


__all__ = [
    "load_adk_cli", "get_adk_cli",
    "load_tui_prefs", "save_tui_prefs",
    "load_identity_cache", "save_identity_cache",
]
