"""Tests for scripts.lib.code_index.base_index — Phase 3 of refactor-a.

Covers: discovery (get_base_index returns None when absent or malformed,
populated dataclass when present), freshness check, seed_copy (table_path
rewrite, replaces existing dst, source untouched).
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def base_index_mod():
    lib = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "lib" / "code_index"
    sys.path.insert(0, str(lib))
    import importlib
    import base_index as mod
    importlib.reload(mod)
    return mod


def _write_base(tmp_path: Path, repo: str, *,
                indexed_sha: str = "a" * 40,
                indexed_at: str | None = None,
                model: str = "nomic-embed-text",
                rows: int = 1000,
                dim: int = 768,
                default_branch: str = "main") -> Path:
    """Create a minimal repo-level base index under tmp_path/.indices/<repo>/."""
    base = tmp_path / ".indices" / repo
    code_index = base / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    if indexed_at is None:
        indexed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (base / "repo-meta.json").write_text(json.dumps({
        "name": repo,
        "default_branch": default_branch,
        "last_indexed_oid": indexed_sha,
        "last_indexed_at": indexed_at,
    }), encoding="utf-8")
    (code_index / "meta.json").write_text(json.dumps({
        "table": "chunks",
        "model": model,
        "dim": dim,
        "rows": rows,
        "table_path": str(code_index / "chunks.lance"),
    }), encoding="utf-8")
    # Fake the LanceDB table dir (just an empty directory — seed_copy only
    # needs to know it exists and can be copied).
    (code_index / "chunks.lance").mkdir(parents=True, exist_ok=True)
    (code_index / "chunks.lance" / "_versions.txt").write_text("0", encoding="utf-8")
    (code_index / "chunks.jsonl").write_text('{"id":"x","file":"f","line_start":1,"line_end":1,"content":"x"}\n',
                                              encoding="utf-8")
    (code_index / "scip").mkdir(parents=True, exist_ok=True)
    (code_index / "scip" / "index.ts.scip").write_text("scip-binary-placeholder", encoding="utf-8")
    return base


def test_get_base_index_returns_none_when_absent(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    assert base_index_mod.get_base_index("nonexistent") is None


def test_get_base_index_returns_none_when_repo_meta_missing(tmp_path, monkeypatch, base_index_mod):
    base = tmp_path / ".indices" / "myrepo"
    (base / "code-index").mkdir(parents=True, exist_ok=True)
    (base / "code-index" / "meta.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    assert base_index_mod.get_base_index("myrepo") is None


def test_get_base_index_populated(tmp_path, monkeypatch, base_index_mod):
    _write_base(tmp_path, "myrepo", indexed_sha="deadbeef" + "f" * 32, rows=42, dim=768)
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")
    assert idx is not None
    assert idx.repo == "myrepo"
    assert idx.indexed_sha.startswith("deadbeef")
    assert idx.rows == 42
    assert idx.embed_model == "nomic-embed-text"
    assert idx.default_branch == "main"
    assert idx.age_days >= 0


def test_is_fresh_within_default(tmp_path, monkeypatch, base_index_mod):
    """A just-written index is fresh by default."""
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")
    assert base_index_mod.is_fresh(idx) is True


def test_is_fresh_rejects_old(tmp_path, monkeypatch, base_index_mod):
    """An index older than the cap is not fresh."""
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_base(tmp_path, "myrepo", indexed_at=old_ts)
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")
    assert base_index_mod.is_fresh(idx, max_staleness_days=7) is False
    assert base_index_mod.is_fresh(idx, max_staleness_days=60) is True


def test_seed_copy_table_path_rewritten(tmp_path, monkeypatch, base_index_mod):
    """The seed_copy must rewrite meta.json.table_path to the new location.

    If it doesn't, query_index.py opens the SOURCE table, defeating the
    point of seeding (and corrupting the base when the PR's incremental
    embedder writes back).
    """
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")

    dst = tmp_path / "pr-task"
    summary = base_index_mod.seed_copy(idx, dst)

    assert (dst / "code-index" / "meta.json").exists()
    assert (dst / "code-index" / "chunks.lance").is_dir()
    assert (dst / "code-index" / "chunks.lance" / "_versions.txt").read_text(encoding="utf-8") == "0"
    assert (dst / "code-index" / "scip" / "index.ts.scip").exists()
    new_meta = json.loads((dst / "code-index" / "meta.json").read_text(encoding="utf-8"))
    assert new_meta["table_path"] == str(dst / "code-index" / "chunks.lance")
    assert new_meta["seeded_from_base"] is True
    assert new_meta["seeded_from_sha"] == idx.indexed_sha
    assert "seeded_at" in new_meta
    assert summary["rows"] == idx.rows
    assert summary["seeded_from_sha"] == idx.indexed_sha


def test_seed_copy_replaces_existing_dst(tmp_path, monkeypatch, base_index_mod):
    """If dst/code-index/ already exists, it gets replaced — never half-merged."""
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")

    dst = tmp_path / "pr-task"
    (dst / "code-index").mkdir(parents=True, exist_ok=True)
    (dst / "code-index" / "STALE.txt").write_text("should be gone after seed", encoding="utf-8")

    base_index_mod.seed_copy(idx, dst)

    assert not (dst / "code-index" / "STALE.txt").exists()
    assert (dst / "code-index" / "chunks.lance" / "_versions.txt").exists()


def test_seed_copy_does_not_mutate_source(tmp_path, monkeypatch, base_index_mod):
    """The source base must be untouched after a seed."""
    _write_base(tmp_path, "myrepo")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    idx = base_index_mod.get_base_index("myrepo")
    src_meta_path = idx.code_index_dir / "meta.json"
    src_meta_before = src_meta_path.read_text(encoding="utf-8")

    dst = tmp_path / "pr-task"
    base_index_mod.seed_copy(idx, dst)

    assert src_meta_path.read_text(encoding="utf-8") == src_meta_before


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
