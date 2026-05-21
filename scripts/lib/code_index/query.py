"""query.py — public Python API for skills that consume the code index.

Stable surface (skills can rely on this across minor versions):

    from scripts.lib.code_index.query import (
        open_index, similar, callers, defs, by_symbol, feature_flag,
        Hit, Index,
        IndexNotBuilt, IndexStale, ModelMismatch,
    )

Two roots are supported:

    open_index("ecomm-ssr")                            # kind="repo"  → ~/.agents-devkit/repos/.indices/<name>/code-index/
    open_index(Path(".../pr-reviews/foo_pr-42"), kind="task")  # → <path>/code-index/

When the index is absent, callers get `IndexNotBuilt(repo)`. When the
index is too old, callers get `IndexStale(age_days, last_refreshed)`
(unless they passed `require_fresh=False`, which is the default).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

# In-tree imports — query.py lives beside _common.py + base_index.py.
from _lib_common import (
    REPO_INDICES_ROOT,
    get_cfg,
    get_logger,
    which,
)
from base_index import (
    BaseIndex,
    BranchIndex,
    default_max_staleness_days,
    get_base_index,
    pick_base_index,
)

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
_DECISION_LOG = (
    Path(os.environ.get("ADK_HOME") or (Path.home() / ".agents-devkit"))
    / "improve" / "learning" / "decisions.jsonl"
)


# ----- errors --------------------------------------------------------------

class CodeIndexError(Exception):
    """Base for everything raised by this module."""


class IndexNotBuilt(CodeIndexError):
    """The repo / task index does not exist on disk.

    Callers should prompt: `adk repo add <git-url>` or
    `adk repo update <repo>`.
    """
    def __init__(self, target: str):
        super().__init__(f"code index not built for: {target}")
        self.target = target


class IndexStale(CodeIndexError):
    """The base index is older than `max_staleness_days`.

    The caller can still proceed by re-calling `open_index(require_fresh=False)`.
    """
    def __init__(self, age_days: float, last_refreshed: datetime, cap_days: int):
        super().__init__(
            f"code index is {age_days:.1f} days old (cap={cap_days}); refresh with "
            "`adk repo update <repo>` or pass require_fresh=False to use anyway"
        )
        self.age_days = age_days
        self.last_refreshed = last_refreshed
        self.cap_days = cap_days


class ModelMismatch(CodeIndexError):
    """The index was built with a different embedding model than the caller wants.

    Querying across embed models returns nonsense. Hard-fail rather than
    silently degrading.
    """
    def __init__(self, expected: str, found: str):
        super().__init__(f"embed-model mismatch: expected {expected!r}, found {found!r}")
        self.expected = expected
        self.found = found


# ----- dataclasses ---------------------------------------------------------

@dataclass(frozen=True)
class Hit:
    """A single retrieval result.

    Stable fields across minor versions. New fields go in `extras` (dict).
    """
    path: str
    line_start: int
    line_end: int
    score: float
    snippet: str
    symbol: str | None
    source: Literal["vector", "bm25", "hybrid", "scip", "grep"]
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class Index:
    """A handle to a code index on disk.

    Open via `open_index(repo, ...)` or `open_index(task_dir, kind="task")`.
    Carries enough metadata for the caller to surface "your index is N days
    old" lines back to the user.
    """
    repo: str
    code_index_dir: Path
    embed_model: str
    dim: int
    rows: int
    indexed_sha: str | None
    last_refreshed: datetime | None
    kind: Literal["repo", "task"]
    # Worktree associated with the index. For kind="task" this is the PR
    # checkout; for kind="repo" this is ~/.agents-devkit/repos/<name>/.
    worktree: Path | None = None
    # The branch this index was built against (empty for legacy/seedless
    # cases). For kind="task" indexes that were seeded from a base, this is
    # the source branch — visible to consumers via `meta.json.seeded_from_branch`.
    branch: str = ""
    branch_slug: str = ""

    @property
    def age_days(self) -> float | None:
        if self.last_refreshed is None:
            return None
        return (datetime.now(timezone.utc) - self.last_refreshed).total_seconds() / 86400.0

    @property
    def table_path(self) -> Path:
        return self.code_index_dir / "chunks.lance"


# ----- decision log (lightweight, fail-open) -------------------------------

def _log_decision(skill: str, fork_id: str, **extra: Any) -> None:
    """Append one JSONL line to the decision log. Never raises.

    Reads happen in hot paths (e.g. several `similar()` calls per skill
    invocation); skills can opt out via `_log=False` per call.
    """
    try:
        _DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill": skill,
            "fork_id": fork_id,
            "fork_type": "inferred",
            **extra,
        }
        with _DECISION_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
    except Exception:
        # Decision-logging must NEVER block an actual skill run.
        pass


# ----- open_index ----------------------------------------------------------

def open_index(target: str | Path,
               *,
               kind: Literal["repo", "task"] = "repo",
               branch: str | None = None,
               max_staleness_days: int | None = None,
               require_fresh: bool = False,
               require_model: str | None = None,
               skill: str = "code_index",
               _log: bool = True) -> Index:
    """Open the code index for `target`.

    Args:
        target: repo name (kind="repo") or task-dir path (kind="task").
        kind:   "repo" or "task" — see module docstring.
        branch: (kind="repo" only) name of a specific branch index to open.
                Defaults to the repo's default branch. Pass e.g. "develop" to
                query against a non-default branch index.
        max_staleness_days: override config default (kind="repo" only).
        require_fresh: raise IndexStale if the base is older than the cap.
                       Default False — many consumers want to warn, not fail.
        require_model: raise ModelMismatch if the index was built with a
                       different model. Default None (accept any).
        skill: identifier for the decision log (default "code_index").
        _log:  set False to skip the decision-log write (hot paths).

    Raises:
        IndexNotBuilt:  index files missing.
        IndexStale:     index too old AND require_fresh=True.
        ModelMismatch:  embed-model differs AND require_model is set.
    """
    if kind == "repo":
        repo = str(target)
        # Pass-through: when `branch` is set, we use pick_base_index so a
        # caller asking for "develop" gets it (or falls back to default).
        # When `branch` is None, the back-compat shim returns the default
        # branch — exactly today's behavior.
        base: BranchIndex | None = (
            pick_base_index(repo, target_branch=branch)
            if branch is not None
            else get_base_index(repo)
        )
        if base is None:
            raise IndexNotBuilt(repo)
        idx = Index(
            repo=repo,
            code_index_dir=base.code_index_dir,
            embed_model=base.embed_model,
            dim=base.dim,
            rows=base.rows,
            indexed_sha=base.indexed_sha,
            last_refreshed=base.last_refreshed,
            kind="repo",
            worktree=base.task_dir.parent.parent / repo  # ~/.agents-devkit/repos/<name>/
                if (base.task_dir.parent.parent / repo).exists() else None,
            branch=base.branch,
            branch_slug=base.slug,
        )
        cap = max_staleness_days if max_staleness_days is not None else default_max_staleness_days()
        if require_fresh and idx.age_days is not None and idx.age_days > cap:
            raise IndexStale(idx.age_days, idx.last_refreshed, cap)
    elif kind == "task":
        task_dir = Path(target)
        code_index = task_dir / "code-index"
        meta_path = code_index / "meta.json"
        if not meta_path.exists():
            raise IndexNotBuilt(str(task_dir))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        idx = Index(
            repo=task_dir.name,
            code_index_dir=code_index,
            embed_model=meta.get("model", ""),
            dim=int(meta.get("dim") or 0),
            rows=int(meta.get("rows") or 0),
            indexed_sha=meta.get("seeded_from_sha"),
            last_refreshed=None,
            kind="task",
            worktree=(task_dir / "code") if (task_dir / "code").exists() else None,
            branch=meta.get("seeded_from_branch") or "",
            branch_slug=meta.get("seeded_from_branch_slug") or "",
        )
    else:
        raise ValueError(f"unknown kind: {kind!r}")

    if require_model and idx.embed_model and idx.embed_model != require_model:
        raise ModelMismatch(expected=require_model, found=idx.embed_model)

    if _log:
        _log_decision(
            skill=skill, fork_id="open_index",
            target=str(target), kind=kind,
            embed_model=idx.embed_model,
            rows=idx.rows,
            age_days=round(idx.age_days, 2) if idx.age_days is not None else None,
        )
    return idx


# ----- lazy backend imports ------------------------------------------------

def _open_table(idx: Index):
    try:
        import lancedb  # type: ignore
    except ImportError as e:
        raise CodeIndexError(
            "lancedb not installed. pip install -r scripts/lib/code_index/requirements.txt"
        ) from e
    db = lancedb.connect(str(idx.code_index_dir))
    if "chunks" not in db.list_tables().tables:
        raise CodeIndexError(f"table 'chunks' not present in {idx.code_index_dir}")
    return db.open_table("chunks")


def _embed_text(text: str, model: str) -> list[float]:
    try:
        import requests  # type: ignore
    except ImportError as e:
        raise CodeIndexError("`requests` not installed.") from e
    r = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": model, "input": text, "keep_alive": "30s"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["embeddings"][0]


# ----- internal: row → Hit -------------------------------------------------

def _snippet(row: dict, max_chars: int = 800) -> str:
    s = row.get("content") or ""
    return s if len(s) <= max_chars else s[:max_chars - 1] + "…"


def _to_hit(row: dict, score: float, source: str, extras: dict | None = None) -> Hit:
    return Hit(
        path=row.get("file") or "",
        line_start=int(row.get("line_start") or 0),
        line_end=int(row.get("line_end") or 0),
        score=float(score),
        snippet=_snippet(row),
        symbol=(row.get("parent_symbol") if row.get("parent_symbol") not in (None, "<module>") else None),
        source=source,  # type: ignore[arg-type]
        extras=extras or {},
    )


def _minmax(values: Sequence[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [1.0 if v else 0.0 for v in values]
    return [(v - lo) / (hi - lo) for v in values]


# ----- similar -------------------------------------------------------------

def similar(idx: Index,
            query: str,
            *,
            top_k: int = 8,
            mode: Literal["hybrid", "vector", "bm25"] = "hybrid",
            file_glob: str | None = None) -> list[Hit]:
    """Retrieve top-k chunks similar to `query`.

    Modes:
        hybrid  — dense vector + BM25 weighted merge (default).
        vector  — dense only (cosine).
        bm25    — keyword only.

    file_glob: optional repo-relative glob like 'src/auth/**'. Applied as a
    server-side filter on the `file` column (no shell expansion).
    """
    if not query.strip():
        return []
    table = _open_table(idx)
    where = None
    if file_glob:
        # LanceDB supports SQL LIKE; translate a simple glob.
        like = file_glob.replace("**", "%").replace("*", "%")
        where = f"file LIKE '{like.replace(chr(39), chr(39)+chr(39))}'"

    if mode == "bm25":
        try:
            search = table.search(query, query_type="fts").limit(top_k)
            if where:
                search = search.where(where)
            hits = search.to_list()
        except Exception as e:
            raise CodeIndexError(f"BM25 search failed: {e}") from e
        return [_to_hit(h, h.get("_score", 0.0), "bm25") for h in hits]

    vec = _embed_text(query, idx.embed_model)
    if mode == "vector":
        search = table.search(vec).metric("cosine").limit(top_k)
        if where:
            search = search.where(where)
        hits = search.to_list()
        return [_to_hit(h, 1.0 - float(h.get("_distance", 1.0)), "vector") for h in hits]

    # hybrid (default)
    k_dense = int(get_cfg("retrieval.top_k_dense", default=50))
    k_fts = int(get_cfg("retrieval.top_k_fts", default=50))
    v_weight = float(get_cfg("retrieval.vector_weight", default=0.6))
    f_weight = float(get_cfg("retrieval.fts_weight", default=0.4))

    search_v = table.search(vec).metric("cosine").limit(k_dense)
    if where:
        search_v = search_v.where(where)
    vector_hits = search_v.to_list()

    try:
        search_f = table.search(query, query_type="fts").limit(k_fts)
        if where:
            search_f = search_f.where(where)
        fts_hits = search_f.to_list()
    except Exception:
        # No FTS index — fall back to vector-only.
        return [_to_hit(h, 1.0 - float(h.get("_distance", 1.0)), "vector",
                        {"fts_fallback": True})
                for h in vector_hits[:top_k]]

    v_norm = _minmax([1.0 - float(h.get("_distance", 1.0)) for h in vector_hits])
    f_norm = _minmax([float(h.get("_score", 0.0)) for h in fts_hits])
    merged: dict[str, dict] = {}
    for h, vs in zip(vector_hits, v_norm):
        cid = h["id"]
        merged[cid] = {"row": h, "v": vs, "f": 0.0}
    for h, fs in zip(fts_hits, f_norm):
        cid = h["id"]
        if cid in merged:
            merged[cid]["f"] = fs
        else:
            merged[cid] = {"row": h, "v": 0.0, "f": fs}

    ranked = sorted(
        merged.values(),
        key=lambda rec: v_weight * rec["v"] + f_weight * rec["f"],
        reverse=True,
    )
    out = []
    for rec in ranked[:top_k]:
        score = v_weight * rec["v"] + f_weight * rec["f"]
        out.append(_to_hit(rec["row"], score, "hybrid",
                           {"v_norm": round(rec["v"], 4), "f_norm": round(rec["f"], 4)}))
    return out


# ----- by_symbol / defs / callers -----------------------------------------

def by_symbol(idx: Index, symbol: str, *, limit: int = 20) -> list[Hit]:
    """Return chunks whose `parent_symbol` equals `symbol`. (Exact match.)"""
    if not symbol:
        return []
    table = _open_table(idx)
    safe = symbol.replace("'", "''")
    rows = table.search().where(f"parent_symbol = '{safe}'").limit(limit).to_list()
    return [_to_hit(r, 1.0, "vector") for r in rows]


def defs(idx: Index, symbol: str) -> list[Hit]:
    """Return definition sites for a symbol — currently by_symbol; SCIP TODO."""
    return by_symbol(idx, symbol)


def callers(idx: Index, symbol: str, *, limit: int = 50) -> list[Hit]:
    """Return code locations that call `symbol`. Uses ripgrep over the worktree.

    SCIP-backed lookup is on the roadmap; today this is grep with a quoted
    identifier boundary so the false-positive rate is low.
    """
    if not symbol or idx.worktree is None or not idx.worktree.exists():
        return []
    pattern = rf"\b{re.escape(symbol)}\s*\("
    use_rg = which("rg") is not None
    if use_rg:
        cmd = ["rg", "--json", "-n", pattern]
    else:
        cmd = ["grep", "-rn", pattern, "."]
    try:
        cp = subprocess.run(cmd, cwd=idx.worktree, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return []
    out: list[Hit] = []
    if use_rg:
        for line in cp.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "match":
                continue
            data = ev["data"]
            out.append(Hit(
                path=data["path"]["text"],
                line_start=data["line_number"],
                line_end=data["line_number"],
                score=1.0,
                snippet=data["lines"]["text"].rstrip(),
                symbol=symbol,
                source="grep",
            ))
    else:
        for line in cp.stdout.splitlines():
            m = re.match(r"^([^:]+):(\d+):(.*)$", line)
            if not m:
                continue
            out.append(Hit(
                path=m.group(1), line_start=int(m.group(2)), line_end=int(m.group(2)),
                score=1.0, snippet=m.group(3), symbol=symbol, source="grep",
            ))
        out = out[:limit]
    return out[:limit]


# ----- feature_flag --------------------------------------------------------

def feature_flag(idx: Index, key: str) -> list[Hit]:
    """Return code sites that reference a feature flag / experiment key.

    Today this is grep over the worktree (same as `callers` with the flag
    key as the symbol). Statsig MCP correlation happens in the caller.
    """
    if not key or idx.worktree is None or not idx.worktree.exists():
        return []
    pattern = re.escape(key)
    use_rg = which("rg") is not None
    cmd = (["rg", "--json", "-n", pattern]
           if use_rg else ["grep", "-rn", pattern, "."])
    try:
        cp = subprocess.run(cmd, cwd=idx.worktree, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return []
    out: list[Hit] = []
    if use_rg:
        for line in cp.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "match":
                continue
            data = ev["data"]
            out.append(Hit(
                path=data["path"]["text"], line_start=data["line_number"],
                line_end=data["line_number"], score=1.0,
                snippet=data["lines"]["text"].rstrip(),
                symbol=key, source="grep",
            ))
    else:
        for line in cp.stdout.splitlines():
            m = re.match(r"^([^:]+):(\d+):(.*)$", line)
            if not m:
                continue
            out.append(Hit(
                path=m.group(1), line_start=int(m.group(2)), line_end=int(m.group(2)),
                score=1.0, snippet=m.group(3), symbol=key, source="grep",
            ))
    return out[:50]


__all__ = [
    "Hit", "Index",
    "IndexNotBuilt", "IndexStale", "ModelMismatch", "CodeIndexError",
    "open_index", "similar", "by_symbol", "defs", "callers", "feature_flag",
]
