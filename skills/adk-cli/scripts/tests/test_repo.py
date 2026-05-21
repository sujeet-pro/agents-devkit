"""Tests for `adk repo`:
- _repo_name_from_url — URL → repo-name derivation (used by every downstream path).
- _known_repo_names — discovery of indexed repos under REPOS_ROOT (used by --all
  and by the shell completion's dynamic name list).
- cmd_list --names-only — completion-friendly listing.
- cmd_update argparse wiring — `--all` is accepted; bare `update` (no name, no --all)
  errors out cleanly.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from contextlib import redirect_stdout

import pytest

import repo
from repo import _repo_name_from_url


@pytest.mark.parametrize("url,expected", [
    ("https://github.com/acme/foo.git", "foo"),
    ("https://github.com/acme/foo", "foo"),
    ("https://github.com/acme/foo/", "foo"),
    ("git@github.com:acme/foo.git", "foo"),
    ("git@github.com:acme/foo", "foo"),
    ("https://bitbucket.org/team/my-repo.git", "my-repo"),
    ("/home/user/repos/myproject", "myproject"),
    ("ssh://git@gitea.example.com/acme/zoo.git", "zoo"),
])
def test_repo_name_derivation(url, expected):
    assert _repo_name_from_url(url) == expected


@pytest.fixture
def fake_repos_root(tmp_path, monkeypatch):
    """Point REPOS_ROOT at a clean tmp dir for the test."""
    monkeypatch.setattr(repo, "REPOS_ROOT", tmp_path)
    # _index_task_dir builds REPO_INDICES_ROOT off REPOS_ROOT at import time, so
    # patch the derived constant too.
    monkeypatch.setattr(repo, "REPO_INDICES_ROOT", tmp_path / ".indices")
    return tmp_path


def test_known_repo_names_empty(fake_repos_root):
    assert repo._known_repo_names() == []


def test_known_repo_names_sorts_and_skips_hidden(fake_repos_root):
    (fake_repos_root / "beta").mkdir()
    (fake_repos_root / "alpha").mkdir()
    (fake_repos_root / ".indices").mkdir()   # hidden — should be excluded
    (fake_repos_root / ".worktree-lock").touch()  # hidden file — should be excluded
    assert repo._known_repo_names() == ["alpha", "beta"]


def test_list_names_only(fake_repos_root, capsys):
    (fake_repos_root / "foo").mkdir()
    (fake_repos_root / "bar").mkdir()
    args = type("A", (), {"names_only": True, "yes": False})()
    rc = repo.cmd_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert out.splitlines() == ["bar", "foo"]


def test_update_requires_name_or_all(fake_repos_root, monkeypatch):
    """`adk repo update` (no name, no --all) should die with a helpful error."""
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    with pytest.raises(SystemExit):
        repo.main(["update"])


def test_update_rejects_name_with_all(fake_repos_root, monkeypatch):
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    (fake_repos_root / "foo").mkdir()
    with pytest.raises(SystemExit):
        repo.main(["update", "foo", "--all"])


def test_update_all_with_no_repos(fake_repos_root, monkeypatch, capsys):
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    rc = repo.main(["update", "--all"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "no repos" in out


def test_update_all_iterates_each_repo(fake_repos_root, monkeypatch, capsys):
    """--all should call _update_one once per indexed repo and aggregate
    results, even when some fail."""
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    (fake_repos_root / "alpha").mkdir()
    (fake_repos_root / "beta").mkdir()
    (fake_repos_root / "gamma").mkdir()

    calls: list[str] = []

    def fake_update_one(name, args, log):
        calls.append(name)
        if name == "beta":
            raise SystemExit("simulated failure")
        return {"name": name, "head_oid": "deadbeef", "indexed": "skipped",
                "reason": "HEAD unchanged"}

    monkeypatch.setattr(repo, "_update_one", fake_update_one)
    rc = repo.main(["update", "--all"])
    # One failure → exit 1; the other two still ran.
    assert rc == 1
    assert calls == ["alpha", "beta", "gamma"]
    out = capsys.readouterr().out
    assert "alpha" in out and "beta" in out and "gamma" in out
    assert "simulated failure" in out


# ---------------------------------------------------------------
# Phase C — multi-branch index management
# ---------------------------------------------------------------

import json
from types import SimpleNamespace


def _make_legacy(fake_repos_root: Path, name: str, *, default_branch: str = "master",
                 indexed_sha: str = "deadbeefcafebabe") -> Path:
    """Create the OLD <repo>/code-index/ layout to test the migration path."""
    repo_dir = fake_repos_root / ".indices" / name
    code_index = repo_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name,
        "default_branch": default_branch,
        "last_indexed_oid": indexed_sha,
        "last_indexed_at": "2026-05-19T00:00:00Z",
    }), encoding="utf-8")
    (code_index / "meta.json").write_text(json.dumps({
        "model": "nomic-embed-text", "rows": 1, "dim": 768,
        "table_path": str(code_index / "chunks.lance"),
    }), encoding="utf-8")
    (code_index / "chunks.lance").mkdir()
    (code_index / "chunks.lance" / "_versions.txt").write_text("0", encoding="utf-8")
    return repo_dir


def test_migrate_if_legacy_moves_code_index(fake_repos_root, monkeypatch):
    """The migration helper relocates the legacy index to
    branches/<slug(default_branch)>/code-index/ and rewrites repo-meta to
    the catalog shape."""
    repo_dir = _make_legacy(fake_repos_root, "ecomm-ssr", default_branch="master",
                            indexed_sha="m" * 40)
    log = repo.get_logger("test-migrate")
    moved = repo._migrate_if_legacy("ecomm-ssr", log)
    assert moved is True
    # Old code-index/ is gone.
    assert not (repo_dir / "code-index").exists()
    # New branches/master/code-index/ exists with the same content.
    new_code = repo_dir / "branches" / "master" / "code-index"
    assert new_code.is_dir()
    assert (new_code / "chunks.lance" / "_versions.txt").read_text(encoding="utf-8") == "0"
    # branch-meta.json carries the per-branch SHA.
    bm = json.loads((repo_dir / "branches" / "master" / "branch-meta.json").read_text(encoding="utf-8"))
    assert bm["branch"] == "master"
    assert bm["slug"] == "master"
    assert bm["last_indexed_oid"] == "m" * 40
    # repo-meta catalog now has tracked_branches and no top-level last_*.
    rm = json.loads((repo_dir / "repo-meta.json").read_text(encoding="utf-8"))
    assert "tracked_branches" in rm and len(rm["tracked_branches"]) == 1
    assert "last_indexed_oid" not in rm
    assert "last_indexed_at" not in rm


def test_migrate_if_legacy_is_idempotent(fake_repos_root, monkeypatch):
    _make_legacy(fake_repos_root, "ecomm-ssr")
    log = repo.get_logger("test-migrate-2")
    assert repo._migrate_if_legacy("ecomm-ssr", log) is True   # first run migrates
    assert repo._migrate_if_legacy("ecomm-ssr", log) is False  # second is a no-op


def test_migrate_if_legacy_skips_when_default_branch_unknown(fake_repos_root):
    """If repo-meta.json lacks default_branch, migration bails rather than
    guessing — the user has to set it (or `adk repo add` would set it for them)."""
    repo_dir = fake_repos_root / ".indices" / "ecomm-ssr"
    (repo_dir / "code-index").mkdir(parents=True)
    (repo_dir / "repo-meta.json").write_text(json.dumps({"name": "ecomm-ssr"}),
                                              encoding="utf-8")
    log = repo.get_logger("test-migrate-3")
    assert repo._migrate_if_legacy("ecomm-ssr", log) is False
    # Old layout untouched.
    assert (repo_dir / "code-index").exists()
    assert not (repo_dir / "branches").exists()


def test_resolve_branches_for_update_default_only(fake_repos_root):
    """No --branch and no --all-branches → just the default branch."""
    args = SimpleNamespace(branch=None, all_branches=False)
    log = repo.get_logger("t")
    chosen = repo._resolve_branches_for_update("foo", args, "master", log)
    assert chosen == ["master"]


def test_resolve_branches_for_update_explicit_branches_win(fake_repos_root):
    args = SimpleNamespace(branch=["develop", "release/24"], all_branches=False)
    chosen = repo._resolve_branches_for_update("foo", args, "master",
                                               repo.get_logger("t"))
    assert chosen == ["develop", "release/24"]


def test_resolve_branches_for_update_all_branches_uses_catalog(fake_repos_root):
    """--all-branches reads tracked_branches from repo-meta.json."""
    name = "foo"
    repo_dir = fake_repos_root / ".indices" / name
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name,
        "default_branch": "master",
        "tracked_branches": [
            {"branch": "master"}, {"branch": "develop"},
        ],
    }), encoding="utf-8")
    args = SimpleNamespace(branch=None, all_branches=True)
    chosen = repo._resolve_branches_for_update(name, args, "master",
                                               repo.get_logger("t"))
    assert chosen == ["master", "develop"]


def test_resolve_branches_for_update_all_branches_falls_back_when_catalog_empty(fake_repos_root):
    args = SimpleNamespace(branch=None, all_branches=True)
    chosen = repo._resolve_branches_for_update("foo", args, "master",
                                               repo.get_logger("t"))
    assert chosen == ["master"]


def test_branch_remove_refuses_default_branch(fake_repos_root, monkeypatch, capsys):
    """The default branch's index is load-bearing; removing it would break
    every PR review that falls back to default. Must require --yes."""
    name = "foo"
    repo_dir = fake_repos_root / ".indices" / name
    branch_dir = repo_dir / "branches" / "master"
    (branch_dir / "code-index").mkdir(parents=True)
    (branch_dir / "branch-meta.json").write_text(json.dumps({
        "branch": "master", "slug": "master",
        "last_indexed_oid": "abc", "last_indexed_at": "2026-05-21T00:00:00Z",
    }), encoding="utf-8")
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name, "default_branch": "master",
        "tracked_branches": [{"branch": "master", "slug": "master"}],
    }), encoding="utf-8")
    args = SimpleNamespace(name=name, branch="master", yes=False)
    with pytest.raises(SystemExit):
        repo.cmd_branch_remove(args)
    # Branch dir still on disk.
    assert (branch_dir / "code-index").exists()


def test_branch_remove_non_default_succeeds(fake_repos_root, monkeypatch, capsys):
    name = "foo"
    repo_dir = fake_repos_root / ".indices" / name
    for br in ("master", "develop"):
        bd = repo_dir / "branches" / br
        (bd / "code-index").mkdir(parents=True)
        (bd / "branch-meta.json").write_text(json.dumps({
            "branch": br, "slug": br,
            "last_indexed_oid": "abc", "last_indexed_at": "2026-05-21T00:00:00Z",
        }), encoding="utf-8")
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name, "default_branch": "master",
    }), encoding="utf-8")
    args = SimpleNamespace(name=name, branch="develop", yes=False)
    rc = repo.cmd_branch_remove(args)
    assert rc == 0
    assert not (repo_dir / "branches" / "develop").exists()
    # Default branch untouched.
    assert (repo_dir / "branches" / "master").exists()
    # Catalog refreshed.
    rm = json.loads((repo_dir / "repo-meta.json").read_text(encoding="utf-8"))
    assert {tb["branch"] for tb in rm["tracked_branches"]} == {"master"}


def test_branch_list_legacy_repo_reports_legacy(fake_repos_root, capsys):
    _make_legacy(fake_repos_root, "foo", default_branch="master")
    args = SimpleNamespace(name="foo", yes=False)
    rc = repo.cmd_branch_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "legacy" in out


def test_branch_list_new_layout_shows_each_branch(fake_repos_root, capsys):
    name = "ecomm-ssr"
    repo_dir = fake_repos_root / ".indices" / name
    for br, sha in (("master", "m" * 40), ("develop", "d" * 40)):
        bd = repo_dir / "branches" / br
        (bd / "code-index").mkdir(parents=True)
        (bd / "branch-meta.json").write_text(json.dumps({
            "branch": br, "slug": br,
            "last_indexed_oid": sha, "last_indexed_at": "2026-05-21T00:00:00Z",
        }), encoding="utf-8")
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name, "default_branch": "master",
    }), encoding="utf-8")
    args = SimpleNamespace(name=name, yes=False)
    rc = repo.cmd_branch_list(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "master" in out and "develop" in out


def test_cmd_migrate_handles_all_repos(fake_repos_root, monkeypatch, capsys):
    """`adk repo migrate` (no name) migrates every legacy repo."""
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    # Two repos: one legacy, one already migrated. clone dirs first.
    (fake_repos_root / "foo").mkdir()
    (fake_repos_root / "bar").mkdir()
    _make_legacy(fake_repos_root, "foo", default_branch="master")
    # bar starts already-migrated → its row should report migrated=False.
    bar_dir = fake_repos_root / ".indices" / "bar"
    (bar_dir / "branches" / "main" / "code-index").mkdir(parents=True)
    (bar_dir / "repo-meta.json").write_text(json.dumps({
        "name": "bar", "default_branch": "main",
    }), encoding="utf-8")

    args = SimpleNamespace(name=None, yes=False)
    rc = repo.cmd_migrate(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    statuses = {r["name"]: r["migrated"] for r in out["results"]}
    assert statuses == {"foo": True, "bar": False}


def test_rewrite_repo_catalog_drops_legacy_sha_when_branches_populated(fake_repos_root):
    name = "foo"
    repo_dir = fake_repos_root / ".indices" / name
    # repo-meta with the OLD top-level last_indexed_oid + last_indexed_at.
    (repo_dir).mkdir(parents=True)
    (repo_dir / "repo-meta.json").write_text(json.dumps({
        "name": name, "default_branch": "master",
        "last_indexed_oid": "leftover-from-pre-migration",
        "last_indexed_at": "2026-01-01T00:00:00Z",
    }), encoding="utf-8")
    # And one branch-meta in place.
    (repo_dir / "branches" / "master").mkdir(parents=True)
    (repo_dir / "branches" / "master" / "branch-meta.json").write_text(json.dumps({
        "branch": "master", "slug": "master",
        "last_indexed_oid": "current-sha", "last_indexed_at": "2026-05-21T00:00:00Z",
    }), encoding="utf-8")

    repo._rewrite_repo_catalog(name, repo.get_logger("t"))

    rm = json.loads((repo_dir / "repo-meta.json").read_text(encoding="utf-8"))
    assert "last_indexed_oid" not in rm
    assert "last_indexed_at" not in rm
    assert rm["tracked_branches"][0]["last_indexed_oid"] == "current-sha"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
