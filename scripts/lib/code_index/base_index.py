"""base_index.py — locate, freshness-check, and seed-copy the repo-level
base index.

Storage layout (owned by `adk repo add` + `adk repo update`):

    ~/.agents-devkit/repos/.indices/<repo>/
      repo-meta.json            last_indexed_oid + last_indexed_at + default_branch
      code-index/
        chunks.jsonl
        chunks.lance/           LanceDB table dir
        scip/                   per-language SCIP indices (optional)
        meta.json               { table_path: <abs>, model, dim, rows, … }

Phase 3 of refactor-a: `/adk-pr-review` consults this directory before
indexing a PR. When the base is present and fresh (and its embedding model
matches what the run is using), the PR-review skill copies the index into
its own task dir and overlays only the PR's diff chunks via `embedder.py
--mode incremental`. This turns the cold 9-minute reindex into a warm
~30-second overlay.

`open_index` (used by /adk-implement, /adk-investigate, /adk-document, etc.)
also reads from here.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _lib_common import REPO_INDICES_ROOT, get_cfg, get_logger


@dataclass(frozen=True)
class BaseIndex:
    repo: str
    task_dir: Path                # the .indices/<repo>/ dir
    code_index_dir: Path          # .indices/<repo>/code-index/
    indexed_sha: str              # last_indexed_oid from repo-meta.json
    last_refreshed: datetime      # UTC
    default_branch: str
    embed_model: str              # from code-index/meta.json
    dim: int
    rows: int

    @property
    def age_days(self) -> float:
        delta = datetime.now(timezone.utc) - self.last_refreshed
        return delta.total_seconds() / 86400.0


def _parse_iso8601_utc(s: str) -> datetime:
    """Accept either '…Z' or naive 'YYYY-MM-DDTHH:MM:SS' and treat as UTC."""
    if not s:
        raise ValueError("empty timestamp")
    if s.endswith("Z"):
        return datetime.fromisoformat(s[:-1]).replace(tzinfo=timezone.utc)
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def get_base_index(repo: str) -> BaseIndex | None:
    """Return a BaseIndex if the repo-level index exists and is well-formed.

    Returns None if either repo-meta.json or code-index/meta.json is missing
    or unreadable — caller decides whether to fall back to a full reindex.
    """
    task_dir = REPO_INDICES_ROOT / repo
    code_index_dir = task_dir / "code-index"
    repo_meta_path = task_dir / "repo-meta.json"
    embed_meta_path = code_index_dir / "meta.json"
    if not repo_meta_path.exists() or not embed_meta_path.exists():
        return None
    try:
        repo_meta = json.loads(repo_meta_path.read_text(encoding="utf-8"))
        embed_meta = json.loads(embed_meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    indexed_sha = repo_meta.get("last_indexed_oid") or ""
    last_at_raw = repo_meta.get("last_indexed_at") or ""
    if not indexed_sha:
        return None
    try:
        last_refreshed = _parse_iso8601_utc(last_at_raw)
    except Exception:
        last_refreshed = datetime.fromtimestamp(0, tz=timezone.utc)
    return BaseIndex(
        repo=repo,
        task_dir=task_dir,
        code_index_dir=code_index_dir,
        indexed_sha=indexed_sha,
        last_refreshed=last_refreshed,
        default_branch=repo_meta.get("default_branch") or "",
        embed_model=embed_meta.get("model") or "",
        dim=int(embed_meta.get("dim") or 0),
        rows=int(embed_meta.get("rows") or 0),
    )


def default_max_staleness_days() -> int:
    """User-configurable via base_index.max_staleness_days in core.yaml /
    code-index.yaml. Built-in default: 7."""
    try:
        return int(get_cfg("base_index.max_staleness_days", default=7))
    except Exception:
        return 7


def is_fresh(idx: BaseIndex, max_staleness_days: int | None = None) -> bool:
    cap = max_staleness_days if max_staleness_days is not None else default_max_staleness_days()
    return idx.age_days <= cap


def seed_copy(idx: BaseIndex, dst_task_dir: Path, *, log=None) -> dict[str, Any]:
    """Copy the base index into dst_task_dir/code-index/ and rewrite paths.

    Returns a dict summarising what landed (rows, model, dim, source_sha,
    bytes copied). Idempotent: if the destination already exists, it is
    REPLACED so we never leave half-merged state behind.

    Why a copy not a symlink: the PR-review overlay phase runs
    `embedder.py --mode incremental` against the destination, which mutates
    the LanceDB table. A symlink would mutate the shared base — wrong.
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

    # Rewrite the absolute table_path in meta.json so query_index.py opens
    # the COPIED table, not the source.
    meta_path = dst_code / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["table_path"] = str(dst_code / "chunks.lance")
        meta["seeded_from_base"] = True
        meta["seeded_from"] = str(src_code)
        meta["seeded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        meta["seeded_from_sha"] = idx.indexed_sha
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=False), encoding="utf-8")

    summary = {
        "src": str(src_code),
        "dst": str(dst_code),
        "seeded_from_sha": idx.indexed_sha,
        "rows": idx.rows,
        "embed_model": idx.embed_model,
        "elapsed_s": round(elapsed, 2),
    }
    log.info("seed_copy: copied %d rows from %s @ %s (%.1fs)",
             idx.rows, idx.repo, idx.indexed_sha[:12], elapsed)
    return summary
