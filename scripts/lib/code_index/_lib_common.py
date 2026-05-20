"""_common.py — focused helpers for the code_index shared library.

Intentionally smaller than skills/adk-pr-review/scripts/_common.py — this
module only carries what the indexer + query code actually need (logging,
error exit, file IO, hashing, PATH check, config). State / lock / queue /
PR-URL helpers stay in the skill because they're not part of the index
contract.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


# ----- paths ---------------------------------------------------------------

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
REPOS_ROOT = ADK_HOME / "repos"
REPO_INDICES_ROOT = REPOS_ROOT / ".indices"


def repo_index_dir(repo: str) -> Path:
    """Per-repo base index location (default branch). Owned by `adk repo {add,update}`."""
    return REPO_INDICES_ROOT / repo


# ----- logging --------------------------------------------------------------

def get_logger(name: str, task_dir: Path | None = None) -> logging.Logger:
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    log.addHandler(sh)
    if task_dir:
        task_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(task_dir / "review.log")
        fh.setFormatter(fmt)
        log.addHandler(fh)
    return log


# ----- subprocess + path ----------------------------------------------------

def which(binary: str) -> str | None:
    from shutil import which as _which
    return _which(binary)


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True,
        capture: bool = True, env: dict[str, str] | None = None,
        timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd, check=check,
        capture_output=capture, text=True, env=env, timeout=timeout,
    )


# ----- IO -------------------------------------------------------------------

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def emit_json(obj: Any) -> int:
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0


# ----- hashing --------------------------------------------------------------

def sha256_hex(s: str | bytes) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def sha1_hex(s: str | bytes) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha1(s).hexdigest()


# ----- die ------------------------------------------------------------------

def die(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"code_index: {msg}\n")
    raise SystemExit(code)


# ----- config ---------------------------------------------------------------

LIB_DIR = Path(__file__).resolve().parent
LIB_DEFAULTS_YAML = LIB_DIR / "defaults.yaml"
USER_OVERRIDE_YAML = ADK_HOME / "config" / "code-index.yaml"

# Back-compat: the skill's defaults still ship the same indexer keys.
# When LIB_DEFAULTS_YAML exists we ignore this path; only consulted as a
# last-resort fallback for upgrade scenarios where the skill ships values
# the lib doesn't yet ship.
_SKILL_DEFAULTS_FALLBACK = (
    LIB_DIR.parent.parent.parent / "skills" / "adk-pr-review" / "defaults.yaml"
)


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> dict[str, Any]:
    """Lib defaults ⊕ user override (deep merge). YAML loaded lazily."""
    import yaml  # noqa: WPS433

    cfg: dict[str, Any] = {}
    if LIB_DEFAULTS_YAML.exists():
        cfg = yaml.safe_load(LIB_DEFAULTS_YAML.read_text(encoding="utf-8")) or {}
    elif _SKILL_DEFAULTS_FALLBACK.exists():
        # Upgrade fallback — skills/adk-pr-review/defaults.yaml is the legacy
        # location for these keys. Once Phase 2 lands everywhere, the skill's
        # defaults.yaml stops carrying indexer keys.
        cfg = yaml.safe_load(_SKILL_DEFAULTS_FALLBACK.read_text(encoding="utf-8")) or {}
    if USER_OVERRIDE_YAML.exists():
        try:
            user = yaml.safe_load(USER_OVERRIDE_YAML.read_text(encoding="utf-8")) or {}
            cfg = _deep_merge(cfg, user)
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
