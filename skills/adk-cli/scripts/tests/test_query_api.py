"""Tests for scripts.lib.code_index.query — Phase 4 of refactor-a.

Covers the public API surface: error model (IndexNotBuilt, IndexStale,
ModelMismatch), Index dataclass field stability, open_index() for both
"repo" and "task" kinds.

We don't spin up LanceDB / ollama here — those are exercised end-to-end
by the live PR-review run. These tests pin the contract.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def query_mod():
    lib = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "lib" / "code_index"
    sys.path.insert(0, str(lib))
    import importlib
    import base_index, query
    importlib.reload(base_index)
    importlib.reload(query)
    return query


@pytest.fixture(scope="module")
def base_index_mod():
    lib = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "lib" / "code_index"
    sys.path.insert(0, str(lib))
    import importlib
    import base_index
    importlib.reload(base_index)
    return base_index


def _write_base(tmp_path: Path, repo: str, *,
                indexed_sha: str = "deadbeef" * 5,
                model: str = "nomic-embed-text",
                rows: int = 1000,
                dim: int = 768,
                age_days: int = 0) -> Path:
    base = tmp_path / ".indices" / repo
    code_index = base / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    indexed_at = (datetime.now(timezone.utc) - timedelta(days=age_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    (base / "repo-meta.json").write_text(json.dumps({
        "name": repo,
        "default_branch": "main",
        "last_indexed_oid": indexed_sha,
        "last_indexed_at": indexed_at,
    }), encoding="utf-8")
    (code_index / "meta.json").write_text(json.dumps({
        "table": "chunks", "model": model, "dim": dim, "rows": rows,
        "table_path": str(code_index / "chunks.lance"),
    }), encoding="utf-8")
    (code_index / "chunks.lance").mkdir(parents=True, exist_ok=True)
    return base


def test_open_index_not_built(tmp_path, monkeypatch, query_mod, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    with pytest.raises(query_mod.IndexNotBuilt) as ei:
        query_mod.open_index("does-not-exist", _log=False)
    assert ei.value.target == "does-not-exist"


def test_open_index_repo_returns_populated(tmp_path, monkeypatch, query_mod, base_index_mod):
    _write_base(tmp_path, "myrepo", rows=42)
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = query_mod.open_index("myrepo", _log=False)
    assert idx.repo == "myrepo"
    assert idx.kind == "repo"
    assert idx.rows == 42
    assert idx.embed_model == "nomic-embed-text"
    assert idx.last_refreshed is not None
    assert idx.age_days is not None and idx.age_days >= 0


def test_open_index_stale_raises_when_require_fresh(tmp_path, monkeypatch, query_mod, base_index_mod):
    _write_base(tmp_path, "myrepo", age_days=30)
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    with pytest.raises(query_mod.IndexStale) as ei:
        query_mod.open_index("myrepo", require_fresh=True, max_staleness_days=7, _log=False)
    assert ei.value.age_days > 7
    assert ei.value.cap_days == 7


def test_open_index_stale_warns_not_fails_by_default(tmp_path, monkeypatch, query_mod, base_index_mod):
    """The whole point of `require_fresh=False` (default) is to surface staleness
    via Index.age_days without failing — callers decide whether to skip / warn."""
    _write_base(tmp_path, "myrepo", age_days=30)
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = query_mod.open_index("myrepo", _log=False)  # default require_fresh=False
    assert idx.age_days > 20


def test_open_index_model_mismatch(tmp_path, monkeypatch, query_mod, base_index_mod):
    _write_base(tmp_path, "myrepo", model="nomic-embed-text")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    with pytest.raises(query_mod.ModelMismatch) as ei:
        query_mod.open_index("myrepo", require_model="bge-m3", _log=False)
    assert ei.value.expected == "bge-m3"
    assert ei.value.found == "nomic-embed-text"


def test_open_index_task_kind(tmp_path, query_mod):
    """kind='task' resolves to <path>/code-index/ (used by /adk-pr-review)."""
    task_dir = tmp_path / "ecomm-ssr_pr-42"
    code_index = task_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    (code_index / "meta.json").write_text(json.dumps({
        "model": "nomic-embed-text", "dim": 768, "rows": 12345,
        "seeded_from_sha": "abc123" * 4,
    }), encoding="utf-8")
    idx = query_mod.open_index(task_dir, kind="task", _log=False)
    assert idx.kind == "task"
    assert idx.rows == 12345
    assert idx.indexed_sha.startswith("abc123")


def test_open_index_invalid_kind(query_mod):
    with pytest.raises(ValueError):
        query_mod.open_index("x", kind="bogus", _log=False)  # type: ignore[arg-type]


def test_hit_dataclass_fields_stable(query_mod):
    """Pinned field set so changes are caught here, not silently downstream."""
    h = query_mod.Hit(
        path="src/foo.py", line_start=1, line_end=10,
        score=0.42, snippet="def x(): pass",
        symbol="x", source="vector", extras={"v_norm": 0.9},
    )
    assert h.path == "src/foo.py"
    assert h.symbol == "x"
    assert h.source == "vector"
    assert h.extras["v_norm"] == 0.9
    # Hit is frozen → mutation should fail.
    with pytest.raises(Exception):
        h.score = 0.5  # type: ignore[misc]


def test_similar_empty_query_returns_empty(tmp_path, monkeypatch, query_mod, base_index_mod):
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = query_mod.open_index("myrepo", _log=False)
    assert query_mod.similar(idx, "") == []
    assert query_mod.similar(idx, "   ") == []


def test_callers_returns_empty_when_no_worktree(tmp_path, monkeypatch, query_mod, base_index_mod):
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = query_mod.open_index("myrepo", _log=False)
    # No worktree on disk → callers must short-circuit.
    assert query_mod.callers(idx, "fn") == []


def test_public_surface(query_mod):
    """Pin the public surface so accidental rename triggers test failure."""
    for name in ("Hit", "Index",
                 "IndexNotBuilt", "IndexStale", "ModelMismatch", "CodeIndexError",
                 "open_index", "similar", "by_symbol", "defs",
                 "callers", "feature_flag"):
        assert hasattr(query_mod, name), f"missing public name: {name}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
