"""_common.py — adk-pr-review skill helpers.

Pure helpers (logging, subprocess, JSON IO, hashing, file_lock, deep_merge,
ADK_HOME, REPOS_ROOT, repo_dir_for) are re-exported from
`scripts/lib/adk_common.py` — see that file for the canonical source.

This module keeps the skill-specific helpers:
- per-PR / per-repo path resolvers (task_dir_for, pr_review_dir, pr_lock_for, …)
- the state-file layer (read_state / write_state / mark_phase)
- `parse_pr_url`
- the skill's config loader (reads `skills/adk-pr-review/defaults.yaml`)
- `die(msg)` wrapper that uses the skill's prefix
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# Make `scripts/lib/` importable so the re-exports below work regardless of
# which entry point loaded this module.
_REPO_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if str(_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_REPO_LIB))

from adk_common import (  # noqa: E402  (sys.path insertion above)
    ADK_HOME,
    REPOS_ROOT,
    LockHeldError,
    branch_meta_path_for,
    branch_worktree_for,
    clone_lock_for,
    deep_merge,
    _deep_merge,  # back-compat alias for the legacy underscore name
    emit_json,
    file_lock,
    get_logger,
    read_json,
    repo_branch_dir,
    repo_clone_for,
    repo_dir_for,
    repo_meta_path_for,
    run,
    run_ok,
    sha1_hex,
    sha256_hex,
    try_file_lock,
    which,
    write_json,
)
from adk_common import die as _die_core  # noqa: E402


# ----- paths (PR-review specific) ------------------------------------------

PR_REVIEW_ROOT = ADK_HOME / "skill-pr-review"


def task_dir_for(repo: str, pr_number: int) -> Path:
    """Resolve the task folder for a PR: `skill-pr-review/<repo>_pr-<n>/`."""
    return PR_REVIEW_ROOT / f"{repo}_pr-{pr_number}"


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


# ----- die ------------------------------------------------------------------

def die(msg: str, code: int = 1) -> None:
    """Skill-prefixed exit. Wraps `adk_common.die` with the adk-pr-review prefix."""
    _die_core(msg, code, prefix="adk-pr-review")


# ----- config loader -------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_DEFAULTS_YAML = SKILL_DIR / "defaults.yaml"
USER_OVERRIDE_YAML = ADK_HOME / "config" / "adk-pr-review.yaml"


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
            cfg = deep_merge(cfg, user)
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
