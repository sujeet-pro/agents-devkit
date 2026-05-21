"""base_index.py — locate, freshness-check, and seed-copy per-branch
base indexes.

Storage layout (owned by `adk repo {add,update,branch}`):

    ~/.agents-devkit/repos/.indices/<repo>/
      repo-meta.json                            { name, url, clone_path,
                                                  default_branch, tracked_branches: [...] }
      branches/<slug>/
        branch-meta.json                        { branch, slug, last_indexed_oid,
                                                  last_indexed_at, embed_model }
        code-index/
          chunks.jsonl
          chunks.lance/                         LanceDB table dir
          scip/                                 per-language SCIP indices (optional)
          meta.json                             { table_path, model, dim, rows, … }

`<slug>` is the branch name passed through `slugify_branch` (lowercase, `/` →
`__`, FS-unsafe chars stripped). The canonical branch name is stored in
`branch-meta.json.branch`; the slug is only the directory key.

Legacy layout (pre-multi-branch, still readable):

    ~/.agents-devkit/repos/.indices/<repo>/
      repo-meta.json                            (carries last_indexed_oid + last_indexed_at)
      code-index/                               (the default-branch index)

Readers treat the legacy layout as a single index pinned to `default_branch`.
Migration moves it under `branches/<slug(default_branch)>/`; see
`skills/adk-cli/scripts/repo.py`.

`/adk-pr-review` consults this directory before indexing a PR. When a base is
present, fresh, and its embedding model matches the run, the skill copies it
into the per-PR task dir and overlays only the (base_sha → pr_head_oid) diff
via `embedder.py --mode incremental`. Picking the branch index that matches
the PR's target branch (instead of always the default) keeps the overlay
small even when default and target have diverged.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _lib_common import REPO_INDICES_ROOT, get_cfg, get_logger


# ---------------------------------------------------------------- types ----

@dataclass(frozen=True)
class BranchIndex:
    """One (repo, branch) base index. Returned by every discovery helper.

    `BaseIndex` is kept as an alias so legacy callers keep compiling; new
    code should reference `BranchIndex` directly.
    """
    repo: str
    branch: str                   # canonical branch name (e.g. "develop")
    slug: str                     # filesystem slug
    repo_dir: Path                # .indices/<repo>/
    branch_dir: Path              # .indices/<repo>/branches/<slug>/  (or repo_dir for legacy)
    code_index_dir: Path          # branch_dir/code-index/
    indexed_sha: str
    last_refreshed: datetime
    embed_model: str
    dim: int
    rows: int
    default_branch: str = ""      # the REPO's default branch (from repo-meta.json)
    legacy_layout: bool = False   # True when read from the pre-multi-branch layout

    @property
    def age_days(self) -> float:
        delta = datetime.now(timezone.utc) - self.last_refreshed
        return delta.total_seconds() / 86400.0

    @property
    def task_dir(self) -> Path:
        """Back-compat alias for `repo_dir`. query.py derives the clone path
        as `idx.task_dir.parent.parent / repo`; that arithmetic still holds."""
        return self.repo_dir


# Alias retained so existing imports of `BaseIndex` keep working until the
# next deprecation pass removes them.
BaseIndex = BranchIndex


# -------------------------------------------------------------- helpers ----

_SLUG_REPLACE_SLASH = "__"
_SLUG_UNSAFE = re.compile(r"[^a-z0-9_.\-]")


def slugify_branch(name: str) -> str:
    """Branch name → FS-safe directory key.

    `/` becomes `__` (round-trippable when names don't contain literal `__`).
    Spaces collapse to `-`. Anything outside `[a-z0-9_.\\-]` is stripped.
    Lowercased so `Develop` and `develop` collide intentionally — branches
    that differ only in case are rare and not worth keeping separate indexes
    for. The canonical branch name lives in `branch-meta.json.branch`; the
    slug is just the directory key.
    """
    s = (name or "").strip().lower()
    if not s:
        return ""
    s = s.replace("/", _SLUG_REPLACE_SLASH)
    s = re.sub(r"\s+", "-", s)
    s = _SLUG_UNSAFE.sub("", s)
    return s or ""


def _parse_iso8601_utc(s: str) -> datetime:
    """Accept either '…Z' or naive 'YYYY-MM-DDTHH:MM:SS' and treat as UTC."""
    if not s:
        raise ValueError("empty timestamp")
    if s.endswith("Z"):
        return datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _read_default_branch(repo_dir: Path) -> str:
    rm = repo_dir / "repo-meta.json"
    if not rm.exists():
        return ""
    try:
        return json.loads(rm.read_text(encoding="utf-8")).get("default_branch") or ""
    except Exception:
        return ""


def _read_one(repo: str, branch_dir: Path, repo_dir: Path,
              *, legacy: bool) -> BranchIndex | None:
    """Build a BranchIndex from disk. Returns None if any required piece is
    missing or malformed — callers decide whether to fall back to another
    branch or to a cold reindex."""
    code_index = branch_dir / "code-index"
    embed_meta_path = code_index / "meta.json"
    if legacy:
        # Legacy: per-branch fields live in repo-meta.json.
        bm_path = repo_dir / "repo-meta.json"
    else:
        bm_path = branch_dir / "branch-meta.json"
    if not bm_path.exists() or not embed_meta_path.exists():
        return None
    try:
        bm = json.loads(bm_path.read_text(encoding="utf-8"))
        embed_meta = json.loads(embed_meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    indexed_sha = bm.get("last_indexed_oid") or ""
    if not indexed_sha:
        return None
    try:
        last_refreshed = _parse_iso8601_utc(bm.get("last_indexed_at") or "")
    except Exception:
        last_refreshed = datetime.fromtimestamp(0, tz=timezone.utc)

    default_branch = _read_default_branch(repo_dir)
    branch_name = bm.get("branch") or default_branch
    slug = bm.get("slug") or (slugify_branch(branch_name) if legacy else branch_dir.name)

    return BranchIndex(
        repo=repo,
        branch=branch_name,
        slug=slug,
        repo_dir=repo_dir,
        branch_dir=branch_dir,
        code_index_dir=code_index,
        indexed_sha=indexed_sha,
        last_refreshed=last_refreshed,
        embed_model=bm.get("embed_model") or embed_meta.get("model") or "",
        dim=int(embed_meta.get("dim") or 0),
        rows=int(embed_meta.get("rows") or 0),
        default_branch=default_branch,
        legacy_layout=legacy,
    )


# ----------------------------------------------------------- discovery ----

def list_branch_indexes(repo: str) -> list[BranchIndex]:
    """Every branch index discovered under .indices/<repo>/.

    Discovery order:
      1. New layout: `.indices/<repo>/branches/<slug>/`.
      2. Legacy layout: `.indices/<repo>/code-index/`. Only surfaced when no
         new-layout indexes exist (so a partial migration doesn't double-list
         the default branch).
    """
    repo_dir = REPO_INDICES_ROOT / repo
    if not repo_dir.exists():
        return []

    out: list[BranchIndex] = []
    branches_dir = repo_dir / "branches"
    if branches_dir.exists():
        for d in sorted(branches_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            idx = _read_one(repo, d, repo_dir, legacy=False)
            if idx is not None:
                out.append(idx)

    if not out:
        legacy = _read_one(repo, repo_dir, repo_dir, legacy=True)
        if legacy is not None:
            out.append(legacy)
    return out


def get_branch_index(repo: str, branch: str) -> BranchIndex | None:
    """Return the BranchIndex for `branch`, or None.

    Matches by canonical branch name first (from `branch-meta.json.branch`),
    then by slug — so a caller passing the slugified form still finds the
    index even though `branch-meta.json` stores the unslugged name.
    """
    if not branch:
        return None
    target_slug = slugify_branch(branch)
    for idx in list_branch_indexes(repo):
        if idx.branch == branch or idx.slug == target_slug:
            return idx
    return None


def get_default_branch_index(repo: str) -> BranchIndex | None:
    """Return the BranchIndex for the repo's default branch, or None."""
    default = _read_default_branch(REPO_INDICES_ROOT / repo)
    if not default:
        return None
    return get_branch_index(repo, default)


def get_default_branch(repo: str) -> str:
    """Repo's default branch name from `repo-meta.json` (empty if unknown)."""
    return _read_default_branch(REPO_INDICES_ROOT / repo)


# ---------------------------------------------------------- selection ----

def pick_base_index(
    repo: str,
    target_branch: str | None,
    *,
    require_model: str | None = None,
    require_fresh: bool = False,
    max_staleness_days: int | None = None,
) -> BranchIndex | None:
    """Pick the best base index for a PR targeting `target_branch`.

    Fallback chain:
      1. Exact match on `target_branch`.
      2. Repo's default branch.
      3. None.

    Indexes that don't satisfy `require_model` (when set) are skipped; same
    for `require_fresh` (against `max_staleness_days`, or the config default).
    The first remaining candidate wins.
    """
    candidates: list[BranchIndex] = []
    if target_branch:
        match = get_branch_index(repo, target_branch)
        if match is not None:
            candidates.append(match)
    default = get_default_branch_index(repo)
    if default is not None and not any(c.slug == default.slug for c in candidates):
        candidates.append(default)

    for c in candidates:
        if require_model and c.embed_model != require_model:
            continue
        if require_fresh and not is_fresh(c, max_staleness_days):
            continue
        return c
    return None


# ---------------------------------------------------------- back-compat ----

def get_base_index(repo: str) -> BranchIndex | None:
    """Deprecated: use `pick_base_index(repo, target_branch=…)` or
    `get_default_branch_index(repo)`. Retained so callers that still ask for
    "the repo's base" keep working through one release."""
    return get_default_branch_index(repo)


# -------------------------------------------------------- freshness ----

def default_max_staleness_days() -> int:
    """User-configurable via `base_index.max_staleness_days` in
    `~/.agents-devkit/config/code-index.yaml`. Built-in default: 7."""
    try:
        return int(get_cfg("base_index.max_staleness_days", default=7))
    except Exception:
        return 7


def is_fresh(idx: BranchIndex, max_staleness_days: int | None = None) -> bool:
    cap = max_staleness_days if max_staleness_days is not None else default_max_staleness_days()
    return idx.age_days <= cap


# ---------------------------------------------------------- seed copy ----

def seed_copy(idx: BranchIndex, dst_task_dir: Path, *, log=None) -> dict[str, Any]:
    """Copy `idx.code_index_dir` into `dst_task_dir/code-index/` and rewrite
    `meta.json.table_path` so the LanceDB table opens against the COPY (not
    the shared base — the PR's incremental embedder would otherwise mutate
    the base).

    Idempotent: if the destination exists, it is REPLACED so we never leave
    half-merged state behind.
    """
    log = log or get_logger("base-index")
    src_code = idx.code_index_dir
    dst_code = dst_task_dir / "code-index"
    if dst_code.exists():
        log.info("seed_copy: replacing existing %s", dst_code)
        shutil.rmtree(dst_code)
    dst_code.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    shutil.copytree(src_code, dst_code, symlinks=False)
    elapsed = time.time() - t0

    meta_path = dst_code / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["table_path"] = str(dst_code / "chunks.lance")
        meta["seeded_from_base"] = True
        meta["seeded_from"] = str(src_code)
        meta["seeded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        meta["seeded_from_sha"] = idx.indexed_sha
        meta["seeded_from_branch"] = idx.branch
        meta["seeded_from_branch_slug"] = idx.slug
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=False), encoding="utf-8")

    summary = {
        "src": str(src_code),
        "dst": str(dst_code),
        "seeded_from_sha": idx.indexed_sha,
        "seeded_from_branch": idx.branch,
        "rows": idx.rows,
        "embed_model": idx.embed_model,
        "elapsed_s": round(elapsed, 2),
    }
    log.info("seed_copy: copied %d rows from %s @ %s/%s (%.1fs)",
             idx.rows, idx.repo, idx.branch or "<default>",
             idx.indexed_sha[:12], elapsed)
    return summary
