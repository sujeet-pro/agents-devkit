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
    """Point REPOS_ROOT at a clean tmp dir for the test.

    The path helpers `repo_dir_for` / `repo_branch_dir` / etc. now live in
    `scripts/lib/adk_common.py` and read `adk_common.REPOS_ROOT` at call time.
    Patch both bindings so direct module access (`repo.REPOS_ROOT`) and the
    shared helpers see the same tmp root.
    """
    import adk_common
    monkeypatch.setattr(repo, "REPOS_ROOT", tmp_path)
    monkeypatch.setattr(adk_common, "REPOS_ROOT", tmp_path)
    return tmp_path


def _mark_repo(repos_root: Path, name: str) -> Path:
    """Create the minimal disk shape so `_known_repo_names` recognizes it."""
    repo_dir = repos_root / name
    (repo_dir / "original-clone").mkdir(parents=True)
    return repo_dir


def test_known_repo_names_empty(fake_repos_root):
    assert repo._known_repo_names() == []


def test_known_repo_names_sorts_and_skips_hidden(fake_repos_root):
    _mark_repo(fake_repos_root, "beta")
    _mark_repo(fake_repos_root, "alpha")
    (fake_repos_root / "notarepo").mkdir()        # no original-clone — skipped
    (fake_repos_root / ".hidden").mkdir()         # hidden — skipped
    assert repo._known_repo_names() == ["alpha", "beta"]


def test_list_names_only(fake_repos_root, capsys):
    _mark_repo(fake_repos_root, "foo")
    _mark_repo(fake_repos_root, "bar")
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
    _mark_repo(fake_repos_root, "alpha")
    _mark_repo(fake_repos_root, "beta")
    _mark_repo(fake_repos_root, "gamma")

    calls: list[str] = []

    def fake_update_one(name, args, log):
        calls.append(name)
        if name == "beta":
            raise SystemExit("simulated failure")
        return {"name": name, "head_sha": "deadbeef", "indexed": "skipped",
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
    repo_dir = fake_repos_root / name
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


def test_ensure_worktree_avoids_fetching_into_checked_out_branch(tmp_path, monkeypatch):
    bare = tmp_path / "bare.git"
    worktree = tmp_path / "branch-develop" / "code"
    (worktree / ".git").mkdir(parents=True)
    calls: list[list[str]] = []

    monkeypatch.setattr(repo, "_step", lambda cmd, log: calls.append(cmd))

    repo._ensure_worktree(bare, worktree, "develop", repo.get_logger("t"))

    assert calls[0] == ["git", "-C", str(bare), "fetch", "origin", "develop"]
    assert calls[1] == ["git", "-C", str(worktree), "pull", "--ff-only", "origin", "develop"]
    assert not any("refs/heads/develop" in part for cmd in calls for part in cmd)


def test_ensure_worktree_adds_new_branch_from_fetch_head(tmp_path, monkeypatch):
    bare = tmp_path / "bare.git"
    worktree = tmp_path / "branch-develop" / "code"
    calls: list[list[str]] = []

    monkeypatch.setattr(repo, "_step", lambda cmd, log: calls.append(cmd))

    repo._ensure_worktree(bare, worktree, "develop", repo.get_logger("t"))

    assert calls[0] == ["git", "-C", str(bare), "fetch", "origin", "develop"]
    assert calls[1] == [
        "git", "-C", str(bare), "worktree", "add", "-B", "develop",
        str(worktree), "FETCH_HEAD",
    ]


def test_auto_branch_add_rebuilds_tracked_branch_missing_index(fake_repos_root, monkeypatch, capsys):
    monkeypatch.setattr(repo, "which", lambda *_: "/usr/bin/git")
    name = "storefront-bff"
    repo_dir = fake_repos_root / name
    (repo_dir / "original-clone").mkdir(parents=True)
    (repo_dir / "branch-develop").mkdir(parents=True)
    calls: list[tuple] = []

    monkeypatch.setattr(repo, "_index_one_branch", lambda *a, **kw: calls.append((a, kw)) or {
        "branch": "develop",
        "slug": "develop",
        "head_sha": "a" * 40,
        "indexed": "full",
    })
    monkeypatch.setattr(repo, "_rewrite_repo_catalog", lambda *a, **kw: None)

    args = SimpleNamespace(
        name=name,
        branch="develop",
        yes=False,
        auto=True,
        auto_reason="queued_prs=2",
        embed_model="nomic-embed-text",
    )
    rc = repo.cmd_branch_add(args)

    assert rc == 0
    assert calls
    assert calls[0][1]["created_by"] == "auto"


def test_branch_remove_refuses_default_branch(fake_repos_root, monkeypatch, capsys):
    """The default branch's index is load-bearing; removing it would break
    every PR review that falls back to default. Must require --yes."""
    name = "foo"
    repo_dir = fake_repos_root / name
    branch_dir = repo_dir / "branch-master"
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
    repo_dir = fake_repos_root / name
    for br in ("master", "develop"):
        bd = repo_dir / f"branch-{br}"
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
    assert not (repo_dir / "branch-develop").exists()
    # Default branch untouched.
    assert (repo_dir / "branch-master").exists()
    # Catalog refreshed.
    rm = json.loads((repo_dir / "repo-meta.json").read_text(encoding="utf-8"))
    assert {tb["branch"] for tb in rm["tracked_branches"]} == {"master"}


def test_branch_list_new_layout_shows_each_branch(fake_repos_root, capsys):
    name = "ecomm-ssr"
    repo_dir = fake_repos_root / name
    for br, sha in (("master", "m" * 40), ("develop", "d" * 40)):
        bd = repo_dir / f"branch-{br}"
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


# ----- is_configured_repo ---------------------------------------------------

def _write_minimal_bundle(cfg_dir: Path, repos: list | None = None) -> None:
    """Write a minimal v5 config bundle so ConfigBundle.load() succeeds."""
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "core.json5").write_text(json.dumps({
        "schema_version": 5,
        "user": {"email": "t@e.com", "first_name": "T"},
        "org": {"name": "acme", "primary_workspace": "w"},
        "bot": {"icon_emoji": ":robot:"},
        "defaults": {},
    }), encoding="utf-8")
    (cfg_dir / "workspaces.json5").write_text(json.dumps({
        "workspaces": [{
            "id": "workspace:w", "name": "W", "role": "work",
            "github_org": "acme", "workspace_root": "/tmp",
        }],
    }), encoding="utf-8")
    (cfg_dir / "teams.json5").write_text(json.dumps({
        "teams": [{"id": "team:t", "name": "T"}],
    }), encoding="utf-8")
    if repos is not None:
        (cfg_dir / "repos.json5").write_text(json.dumps({"repos": repos}),
                                              encoding="utf-8")


def test_is_configured_repo_matches_configured_entry(tmp_path, monkeypatch):
    """Exact match on host + org (owner) + name returns True."""
    cfg_dir = tmp_path / "config"
    _write_minimal_bundle(cfg_dir, repos=[{
        "id": "repo:foo", "host": "github", "org": "acme", "name": "foo",
        "workspace": "workspace:w", "team": "team:t", "path": "/tmp/foo",
        "primary_language": "ts", "base_branch": "main",
    }])
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    assert repo.is_configured_repo("github", "acme", "foo") is True


def test_is_configured_repo_rejects_unknown_repo(tmp_path, monkeypatch):
    """A repo not listed in repos.json5 returns False."""
    cfg_dir = tmp_path / "config"
    _write_minimal_bundle(cfg_dir, repos=[{
        "id": "repo:foo", "host": "github", "org": "acme", "name": "foo",
        "workspace": "workspace:w", "team": "team:t", "path": "/tmp/foo",
        "primary_language": "ts", "base_branch": "main",
    }])
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    assert repo.is_configured_repo("github", "acme", "bar") is False


def test_is_configured_repo_empty_registry_returns_true(tmp_path, monkeypatch):
    """Empty repos list → backward compat passthrough."""
    cfg_dir = tmp_path / "config"
    _write_minimal_bundle(cfg_dir, repos=[])
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    assert repo.is_configured_repo("github", "acme", "anything") is True


def test_is_configured_repo_missing_registry_returns_true(tmp_path, monkeypatch):
    """When repos.json5 is absent, return True (don't filter)."""
    cfg_dir = tmp_path / "config"
    # repos is None → _write_minimal_bundle skips writing repos.json5;
    # ConfigBundle.load() treats absent file as empty list.
    _write_minimal_bundle(cfg_dir, repos=None)
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    assert repo.is_configured_repo("github", "acme", "anything") is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
