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


# ---------------------------------------------------------------
# Phase A — multi-branch base indexes
# ---------------------------------------------------------------

def _write_branch(tmp_path: Path, repo: str, branch: str, *,
                  slug: str | None = None,
                  indexed_sha: str = "b" * 40,
                  indexed_at: str | None = None,
                  model: str = "nomic-embed-text",
                  rows: int = 100, dim: int = 768,
                  default_branch: str = "master") -> Path:
    """Create a per-branch index under tmp_path/.indices/<repo>/branches/<slug>/.
    Also writes the catalog repo-meta.json if absent."""
    base_index_mod = None  # not needed for path math
    from base_index import slugify_branch as _slug  # local import so import order matches the real reader
    branch_slug = slug or _slug(branch)
    repo_dir = tmp_path / ".indices" / repo
    branch_dir = repo_dir / "branches" / branch_slug
    code_index = branch_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    if indexed_at is None:
        indexed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Repo-level catalog. Don't overwrite if the test already created one.
    rm_path = repo_dir / "repo-meta.json"
    if not rm_path.exists():
        rm_path.write_text(json.dumps({
            "name": repo,
            "default_branch": default_branch,
            "tracked_branches": [],
        }), encoding="utf-8")
    # Per-branch metadata (replaces the old top-level last_indexed_oid field).
    (branch_dir / "branch-meta.json").write_text(json.dumps({
        "name": repo,
        "branch": branch,
        "slug": branch_slug,
        "last_indexed_oid": indexed_sha,
        "last_indexed_at": indexed_at,
        "embed_model": model,
    }), encoding="utf-8")
    (code_index / "meta.json").write_text(json.dumps({
        "table": "chunks",
        "model": model,
        "dim": dim,
        "rows": rows,
        "table_path": str(code_index / "chunks.lance"),
    }), encoding="utf-8")
    (code_index / "chunks.lance").mkdir(parents=True, exist_ok=True)
    return branch_dir


def test_slugify_branch_simple_names(base_index_mod):
    assert base_index_mod.slugify_branch("master") == "master"
    assert base_index_mod.slugify_branch("develop") == "develop"
    assert base_index_mod.slugify_branch("main") == "main"


def test_slugify_branch_slash_becomes_double_underscore(base_index_mod):
    assert base_index_mod.slugify_branch("release/2024-q3") == "release__2024-q3"
    assert base_index_mod.slugify_branch("feature/foo") == "feature__foo"


def test_slugify_branch_lowercases_and_strips_unsafe(base_index_mod):
    assert base_index_mod.slugify_branch("Develop") == "develop"
    assert base_index_mod.slugify_branch("feat/Foo Bar!") == "feat__foo-bar"
    assert base_index_mod.slugify_branch("") == ""


def test_list_branch_indexes_empty_repo(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    assert base_index_mod.list_branch_indexes("nope") == []


def test_list_branch_indexes_finds_new_layout(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "master",
                  indexed_sha="m" * 40, default_branch="master")
    _write_branch(tmp_path, "ecomm-ssr", "develop",
                  indexed_sha="d" * 40, default_branch="master")
    found = base_index_mod.list_branch_indexes("ecomm-ssr")
    branches = {idx.branch: idx for idx in found}
    assert set(branches) == {"master", "develop"}
    assert branches["develop"].indexed_sha == "d" * 40
    assert branches["develop"].slug == "develop"
    assert branches["develop"].legacy_layout is False


def test_list_branch_indexes_falls_back_to_legacy(tmp_path, monkeypatch, base_index_mod):
    """When no `branches/` dir exists but the old `code-index/` does, that one
    legacy index surfaces as the default-branch index. New layout wins when
    BOTH are present (verified by skipping legacy once we have any new entry)."""
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_base(tmp_path, "ecomm-ssr", default_branch="master")
    found = base_index_mod.list_branch_indexes("ecomm-ssr")
    assert len(found) == 1
    assert found[0].branch == "master"
    assert found[0].legacy_layout is True
    assert found[0].code_index_dir.parent.name == "ecomm-ssr"  # not branches/


def test_get_branch_index_exact_match(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "develop", indexed_sha="d" * 40)
    idx = base_index_mod.get_branch_index("ecomm-ssr", "develop")
    assert idx is not None
    assert idx.branch == "develop"
    assert idx.indexed_sha.startswith("d")


def test_get_branch_index_returns_none_when_missing(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "master")
    assert base_index_mod.get_branch_index("ecomm-ssr", "develop") is None
    assert base_index_mod.get_branch_index("ecomm-ssr", "") is None


def test_get_default_branch_index_uses_repo_meta(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "master", default_branch="master")
    _write_branch(tmp_path, "ecomm-ssr", "develop", default_branch="master")
    idx = base_index_mod.get_default_branch_index("ecomm-ssr")
    assert idx is not None and idx.branch == "master"


def test_pick_base_index_prefers_target_branch(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "master", indexed_sha="m" * 40,
                  default_branch="master")
    _write_branch(tmp_path, "ecomm-ssr", "develop", indexed_sha="d" * 40,
                  default_branch="master")
    picked = base_index_mod.pick_base_index("ecomm-ssr", target_branch="develop")
    assert picked is not None and picked.branch == "develop"
    assert picked.indexed_sha.startswith("d")


def test_pick_base_index_falls_back_to_default(tmp_path, monkeypatch, base_index_mod):
    """PR targets `develop` but only `master` is indexed → caller still gets
    `master` so the cold reindex path isn't triggered unnecessarily."""
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "master", indexed_sha="m" * 40,
                  default_branch="master")
    picked = base_index_mod.pick_base_index("ecomm-ssr", target_branch="develop")
    assert picked is not None and picked.branch == "master"


def test_pick_base_index_returns_none_when_nothing_indexed(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    assert base_index_mod.pick_base_index("ecomm-ssr", target_branch="develop") is None


def test_pick_base_index_skips_model_mismatch(tmp_path, monkeypatch, base_index_mod):
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "develop", model="nomic-embed-text",
                  default_branch="develop")
    # require_model differs → no candidate satisfies → None
    assert base_index_mod.pick_base_index(
        "ecomm-ssr", target_branch="develop", require_model="bge-m3"
    ) is None
    # require_model matches → returned
    picked = base_index_mod.pick_base_index(
        "ecomm-ssr", target_branch="develop", require_model="nomic-embed-text"
    )
    assert picked is not None


def test_pick_base_index_skips_stale_when_require_fresh(tmp_path, monkeypatch, base_index_mod):
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "develop",
                  indexed_at=old_ts, default_branch="develop")
    assert base_index_mod.pick_base_index(
        "ecomm-ssr", target_branch="develop",
        require_fresh=True, max_staleness_days=7
    ) is None
    # Without require_fresh, the stale index is acceptable.
    picked = base_index_mod.pick_base_index("ecomm-ssr", target_branch="develop")
    assert picked is not None and picked.branch == "develop"


def test_get_base_index_shim_returns_default_branch(tmp_path, monkeypatch, base_index_mod):
    """The legacy `get_base_index(repo)` helper now resolves to the default
    branch's BranchIndex — same public field set, plus `branch`/`slug`."""
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "develop", default_branch="develop")
    idx = base_index_mod.get_base_index("ecomm-ssr")
    assert idx is not None and idx.branch == "develop"


def test_seed_copy_records_source_branch(tmp_path, monkeypatch, base_index_mod):
    """meta.json on the seeded copy must record the source branch + slug so
    debugging shows where the PR's seeded chunks originated."""
    monkeypatch.setattr(base_index_mod, "REPO_INDICES_ROOT", tmp_path / ".indices")
    _write_branch(tmp_path, "ecomm-ssr", "develop", indexed_sha="d" * 40,
                  default_branch="master")
    idx = base_index_mod.pick_base_index("ecomm-ssr", target_branch="develop")
    dst = tmp_path / "pr-task"
    summary = base_index_mod.seed_copy(idx, dst)
    seeded_meta = json.loads((dst / "code-index" / "meta.json").read_text(encoding="utf-8"))
    assert seeded_meta["seeded_from_branch"] == "develop"
    assert seeded_meta["seeded_from_branch_slug"] == "develop"
    assert summary["seeded_from_branch"] == "develop"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
