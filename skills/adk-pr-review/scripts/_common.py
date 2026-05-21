"""_common.py — shared helpers for adk-pr-review scripts.

Imported by every other script in this folder. Keep it small and dependency-light.
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator

# ----- paths -----------------------------------------------------------------

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
REPOS_ROOT = ADK_HOME / "repos"

PR_REVIEW_ROOT = ADK_HOME / "skill-pr-review"


def task_dir_for(repo: str, pr_number: int) -> Path:
    """Resolve the task folder for a PR: `skill-pr-review/<repo>_pr-<n>/`."""
    return PR_REVIEW_ROOT / f"{repo}_pr-{pr_number}"


def repo_clone_for(repo: str) -> Path:
    """Bare clone of the repo. Holds .git/ only; every worktree (per-branch +
    per-PR) is created from here via `git worktree add`."""
    return REPOS_ROOT / repo / "original-clone"


def repo_dir_for(repo: str) -> Path:
    """Per-repo root: holds original-clone/, branch-*/, docs/, repo-meta.json."""
    return REPOS_ROOT / repo


def repo_branch_dir(repo: str, branch_slug: str) -> Path:
    """Per-(repo, branch) folder: holds code/ (worktree), code-index/, branch-meta.json."""
    return REPOS_ROOT / repo / f"branch-{branch_slug}"


def clone_lock_for(repo: str) -> Path:
    """Per-repo lock file. Acquired briefly during clone / fetch / reset / worktree-add.
    Different repos do not contend; same-repo invocations serialize only on this brief window."""
    return REPOS_ROOT / repo / ".clone-lock"


def pr_lock_for(repo: str, pr_number: int) -> Path:
    """Per-PR lock file. Held for the full duration of a single /adk-pr-review invocation,
    so two simultaneous reviews of the same PR cannot stomp on each other's state.json /
    findings.json / posted comments. Parallel reviews of DIFFERENT PRs (same repo) do
    NOT contend on this lock."""
    return task_dir_for(repo, pr_number) / ".adk-pr-lock"


# v4 P4: PR-review-specific files live in a `pr-review/` subfolder of the
# task dir, alongside `code/`, `code-index/`, `scip/`, `docs/`. This mirrors
# the shape of a branch dir under repos/<name>/branch-<NAME>/ — a clean
# separation of shared-with-other-skills folders from skill-specific ones.

# The set of file names that belong in the pr-review/ subfolder (everything
# the /adk-pr-review skill writes during a review).
PR_REVIEW_FILES = frozenset({
    "pr.json", "pr-comments.json", "diff.patch", "precis.md",
    "findings.json", "validated-findings.json", "initial-findings.json",
    "findings-final.json", "validation-report.json",
    "triage.json", "triage-state.json",
    "posting-plan.json", "post-result.json", "comment-actions.json",
    "findings.md", "report.md",
    "state.json", "queue-context.json",
    "review.log",
})


def pr_review_dir(task_dir: Path) -> Path:
    """Return the per-PR `pr-review/` subfolder, creating it on demand.

    v4 layout (§3 architecture):
      <task_dir>/
        code/          (worktree at PR head)
        code-index/    (chunks + LanceDB)
        scip/          (optional)
        docs/          (supporting docs)
        pr-review/     ← THIS — review-specific files (pr.json, findings.json, ...)
    """
    d = task_dir / "pr-review"
    d.mkdir(parents=True, exist_ok=True)
    return d


def pr_review_file(task_dir: Path, name: str) -> Path:
    """Resolve a PR-review-specific file path: `task_dir/pr-review/<name>`.

    The parent directory is created on demand so `open(pr_review_file(td, "foo.json"), "w")`
    works without a separate mkdir.
    """
    path = task_dir / "pr-review" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ensure_dirs() -> None:
    for p in (REPOS_ROOT, PR_REVIEW_ROOT):
        p.mkdir(parents=True, exist_ok=True)


# ----- logging --------------------------------------------------------------

def get_logger(name: str, task_dir: Path | None = None) -> logging.Logger:
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    # stderr
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    log.addHandler(sh)

    # file
    if task_dir:
        task_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(task_dir / "review.log")
        fh.setFormatter(fmt)
        log.addHandler(fh)
    return log


# ----- state file -----------------------------------------------------------

def read_state(task_dir: Path) -> dict[str, Any]:
    p = task_dir / "state.json"
    if not p.exists():
        return {"task_dir": str(task_dir), "phases": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def write_state(task_dir: Path, state: dict[str, Any]) -> None:
    p = task_dir / "state.json"
    p.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def mark_phase(task_dir: Path, phase: str, status: str, **extra: Any) -> None:
    state = read_state(task_dir)
    phases = state.setdefault("phases", {})
    entry = phases.get(phase, {})
    entry["status"] = status
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry.update(extra)
    phases[phase] = entry
    write_state(task_dir, state)


# ----- file lock ------------------------------------------------------------

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
        # Record the holder so a parallel run can produce a useful diagnostic.
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


# ----- subprocess helpers ---------------------------------------------------

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


def which(binary: str) -> str | None:
    from shutil import which as _which
    return _which(binary)


# ----- misc -----------------------------------------------------------------

def sha256_hex(s: str | bytes) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def sha1_hex(s: str | bytes) -> str:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha1(s).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def emit_json(obj: Any) -> int:
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0


def die(msg: str, code: int = 1) -> None:
    sys.stderr.write(f"adk-pr-review: {msg}\n")
    raise SystemExit(code)


# ----- config loader -------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_DEFAULTS_YAML = SKILL_DIR / "defaults.yaml"
USER_OVERRIDE_YAML = ADK_HOME / "config" / "adk-pr-review.yaml"


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config() -> dict[str, Any]:
    """Skill defaults ⊕ user override (deep merge). CLI flags layer on top
    in the caller. Loads PyYAML lazily so import-time cost is zero when no
    script needs config."""
    import yaml  # noqa: WPS433 — lazy

    if not SKILL_DEFAULTS_YAML.exists():
        die(f"missing skill defaults: {SKILL_DEFAULTS_YAML}")
    cfg = yaml.safe_load(SKILL_DEFAULTS_YAML.read_text(encoding="utf-8")) or {}
    if USER_OVERRIDE_YAML.exists():
        try:
            user = yaml.safe_load(USER_OVERRIDE_YAML.read_text(encoding="utf-8")) or {}
            cfg = _deep_merge(cfg, user)
        except yaml.YAMLError as e:
            die(f"invalid user override {USER_OVERRIDE_YAML}: {e}")
    return cfg


def get_cfg(path: str, default: Any = None, cfg: dict | None = None) -> Any:
    """Dotted-path lookup: get_cfg('embed.default_model')."""
    if cfg is None:
        cfg = load_config()
    node: Any = cfg
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


# ----- discriminators ------------------------------------------------------

GH_PR_RE = re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<n>\d+)", re.I)
BB_PR_RE = re.compile(r"bitbucket\.org/(?P<ws>[^/]+)/(?P<repo>[^/]+)/pull-requests/(?P<n>\d+)", re.I)


def parse_pr_url(url: str) -> dict[str, Any]:
    """Returns {host, owner, repo, pr_number} or raises."""
    url = url.strip().rstrip("/")
    m = GH_PR_RE.search(url)
    if m:
        return {"host": "github", "owner": m.group("owner"), "repo": m.group("repo"), "pr_number": int(m.group("n"))}
    m = BB_PR_RE.search(url)
    if m:
        return {"host": "bitbucket", "owner": m.group("ws"), "repo": m.group("repo"), "pr_number": int(m.group("n"))}
    raise ValueError(
        f"Unsupported PR URL: {url}. "
        "Only github.com/<owner>/<repo>/pull/<n> and bitbucket.org/<ws>/<repo>/pull-requests/<n> are supported."
    )
