"""_lib_common.py — code_index-specific helpers.

Pure helpers (logging, subprocess, JSON IO, hashing, deep_merge, ADK_HOME,
REPOS_ROOT, repo_dir_for) are re-exported from `scripts/lib/adk_common.py`
— see that file for the canonical source.

This module keeps:
- the lib-specific `load_config` / `get_cfg` that read
  `scripts/lib/code_index/defaults.yaml`.
- `die(msg)` wrapper that uses the `code_index` prefix.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# `scripts/lib/` is already on sys.path because the consumer added the
# code_index dir, and adk_common sits one level up. Add it explicitly so
# this module also works under direct invocation.
_LIB_DIR = Path(__file__).resolve().parent.parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from adk_common import (  # noqa: E402  (sys.path insertion above)
    ADK_HOME,
    REPOS_ROOT,
    deep_merge,
    _deep_merge,  # back-compat alias for the legacy underscore name
    emit_json,
    get_logger,
    read_json,
    repo_dir_for,
    run,
    sha1_hex,
    sha256_hex,
    which,
    write_json,
)
from adk_common import die as _die_core  # noqa: E402


# ----- die ------------------------------------------------------------------

def die(msg: str, code: int = 1) -> None:
    """code_index-prefixed exit. Wraps `adk_common.die` with the lib prefix."""
    _die_core(msg, code, prefix="code_index")


# ----- config ---------------------------------------------------------------

LIB_DIR = Path(__file__).resolve().parent
LIB_DEFAULTS_YAML = LIB_DIR / "defaults.yaml"
USER_OVERRIDE_YAML = ADK_HOME / "config" / "code-index.yaml"


def load_config() -> dict[str, Any]:
    """Lib defaults ⊕ user override (deep merge). YAML loaded lazily."""
    import yaml  # noqa: WPS433

    cfg: dict[str, Any] = {}
    if LIB_DEFAULTS_YAML.exists():
        cfg = yaml.safe_load(LIB_DEFAULTS_YAML.read_text(encoding="utf-8")) or {}
    if USER_OVERRIDE_YAML.exists():
        try:
            user = yaml.safe_load(USER_OVERRIDE_YAML.read_text(encoding="utf-8")) or {}
            cfg = deep_merge(cfg, user)
        except yaml.YAMLError as e:
            die(f"invalid user override {USER_OVERRIDE_YAML}: {e}")
    return cfg


def get_cfg(path: str, default: Any = None, cfg: dict | None = None) -> Any:
    if cfg is None:
        cfg = load_config()
    node: Any = cfg
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node
