"""adk_common.py — pure helpers shared across adk scripts.

Shared by:
- `skills/adk-pr-review/scripts/_common.py` (PR-review skill)
- `scripts/lib/code_index/_lib_common.py` (indexer/query lib)
- `scripts/lib/config/` (config IO)

This module owns the *pure* helpers — logging, subprocess, JSON IO, hashing,
fcntl file locking, dict deep-merge — plus the two adk-level path constants
(`ADK_HOME`, `REPOS_ROOT`) and the shared repo path helper (`repo_dir_for`).

What stays in the domain-specific modules:
- `skills/adk-pr-review/scripts/_common.py`: PR-review path helpers
  (`task_dir_for`, `pr_review_dir`, `pr_lock_for`, `clone_lock_for`, …),
  state-file helpers (`read_state`, `write_state`, `mark_phase`),
  `parse_pr_url`, and the skill-specific `load_config` / `get_cfg` that
  read `skills/adk-pr-review/defaults.yaml`.
- `scripts/lib/code_index/_lib_common.py`: the lib-specific `load_config` /
  `get_cfg` that read `scripts/lib/code_index/defaults.yaml`.
- `scripts/lib/config/`: the canonical config-layout loader.

Each domain-specific module re-exports the shared names it owns for local
callers (`from _common import get_logger, ...`).
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

# Make adk_home importable from this module (it lives alongside us in scripts/lib/).
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from adk_home import adk_config_home, adk_data_home  # noqa: E402


# ----- paths ---------------------------------------------------------------

ADK_HOME = adk_data_home()
CONFIG_HOME = adk_config_home()
REPOS_ROOT = ADK_HOME / "repos"


def repo_dir_for(repo: str) -> Path:
    """Per-repo root: holds original-clone/, branch-*/, docs/, repo-meta.json."""
    return REPOS_ROOT / repo


def repo_clone_for(repo: str) -> Path:
    """Bare clone of the repo. Holds .git/ only; every worktree (per-branch +
    per-PR) is created from here via `git worktree add`."""
    return REPOS_ROOT / repo / "original-clone"


def repo_branch_dir(repo: str, branch_slug: str) -> Path:
    """Per-(repo, branch) folder: holds code/ (worktree), code-index/, branch-meta.json."""
    return REPOS_ROOT / repo / f"branch-{branch_slug}"


def clone_lock_for(repo: str) -> Path:
    """Per-repo lock file. Acquired briefly during clone / fetch / reset / worktree-add.
    Different repos do not contend; same-repo invocations serialize only on this brief window."""
    return REPOS_ROOT / repo / ".clone-lock"


def repo_meta_path_for(repo: str) -> Path:
    """`<repo-dir>/repo-meta.json` — catalog with url + default_branch + tracked_branches[]."""
    return REPOS_ROOT / repo / "repo-meta.json"


def branch_worktree_for(repo: str, branch_slug: str) -> Path:
    """`<repo-dir>/branch-<slug>/code` — `git worktree add` target for that branch."""
    return REPOS_ROOT / repo / f"branch-{branch_slug}" / "code"


def branch_meta_path_for(repo: str, branch_slug: str) -> Path:
    """`<repo-dir>/branch-<slug>/branch-meta.json` — branch index metadata."""
    return REPOS_ROOT / repo / f"branch-{branch_slug}" / "branch-meta.json"


# ----- logging --------------------------------------------------------------

from adk_log import (  # noqa: E402
    RunDashboard,
    RunEvent,
    emit_event,
    encode_event,
    extract_failure_reason,
    format_file_ref,
    format_pr_ref,
    get_logger as _shared_get_logger,
    is_orchestrated,
    is_verbose,
    parse_event_line,
    status_glyph,
    summarize_items,
    terminal_link,
)


def get_logger(name: str, task_dir: Path | None = None):
    return _shared_get_logger(name, task_dir=task_dir)


# ----- subprocess + PATH ----------------------------------------------------

def which(binary: str) -> str | None:
    from shutil import which as _which
    return _which(binary)


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True,
        capture: bool = True, env: dict[str, str] | None = None,
        timeout: float | None = None) -> subprocess.CompletedProcess:
    """Run a command. Stdout/stderr captured by default; raises on non-zero unless check=False."""
    return subprocess.run(
        cmd, cwd=cwd, check=check,
        capture_output=capture, text=True, env=env, timeout=timeout,
    )


def run_ok(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> bool:
    try:
        run(cmd, cwd=cwd, check=True, capture=True, env=env)
        return True
    except subprocess.CalledProcessError:
        return False


# ----- JSON IO --------------------------------------------------------------

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

def die(msg: str, code: int = 1, *, prefix: str = "adk") -> None:
    """Print `<prefix>: <msg>` to stderr and exit `code`.

    Domain modules wrap this with their own prefix:
      - `skills/adk-pr-review/scripts/_common.py` → prefix="adk-pr-review"
      - `scripts/lib/code_index/_lib_common.py`   → prefix="code_index"
    """
    sys.stderr.write(f"{prefix}: {msg}\n")
    raise SystemExit(code)


# ----- file locks -----------------------------------------------------------

@contextlib.contextmanager
def file_lock(path: Path, timeout_s: float = 300.0, poll_s: float = 0.5) -> Iterator[None]:
    """fcntl-based exclusive lock. timeout_s 0 = wait forever; default 5 min.

    Use for short-held mutual exclusion (e.g. the clone-lock around `git fetch`
    + `git worktree add`). For the PR-level long-held lock, prefer
    `try_file_lock` so a duplicate invocation can fail fast with a clear
    diagnostic instead of waiting forever.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        deadline = time.time() + timeout_s if timeout_s > 0 else None
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if deadline and time.time() > deadline:
                    raise TimeoutError(f"file_lock: timed out after {timeout_s}s on {path}")
                time.sleep(poll_s)
        os.write(fd, f"pid={os.getpid()} ts={time.time():.0f}\n".encode())
        try:
            yield
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except Exception:
                pass
    finally:
        os.close(fd)


def _read_lockfile_holder(path: Path) -> str:
    """Best-effort: return the contents of an existing lock file ('pid=… ts=…')."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return "<unknown>"


class LockHeldError(RuntimeError):
    """Raised by try_file_lock when the lock is already held and wait=False."""


@contextlib.contextmanager
def try_file_lock(path: Path, wait: bool = False, timeout_s: float = 0.0,
                  poll_s: float = 0.5) -> Iterator[None]:
    """fcntl-based exclusive lock with a fail-fast option.

    - wait=False (default): if the lock is already held by another process,
      raise LockHeldError immediately with the holder's pid/ts. Best for the
      per-PR lock — two tabs reviewing the SAME PR should not silently queue.
    - wait=True: block until acquired (or timeout). Timeout 0 = no timeout.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    acquired = False
    try:
        if not wait:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                holder = _read_lockfile_holder(path)
                raise LockHeldError(
                    f"{path} is already locked by {holder}. "
                    "Pass --wait to block, or kill the prior process if it's stuck."
                )
        else:
            deadline = (time.time() + timeout_s) if timeout_s > 0 else None
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                    break
                except BlockingIOError:
                    if deadline and time.time() > deadline:
                        raise TimeoutError(f"try_file_lock: timed out after {timeout_s}s on {path}")
                    time.sleep(poll_s)
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            os.ftruncate(fd, 0)
            os.write(fd, f"pid={os.getpid()} ts={time.time():.0f}\n".encode())
        except Exception:
            pass
        yield
    finally:
        if acquired:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except Exception:
                pass
        try:
            os.close(fd)
        except Exception:
            pass


# ----- dict merge -----------------------------------------------------------

def deep_merge(base: dict, over: dict) -> dict:
    """Recursive dict merge — `over` wins on collisions; nested dicts are merged."""
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

