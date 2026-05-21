"""Unit tests for tui/model/repo_model.py — η.

Mirrors the pattern in test_workers_model.py: tmp_path-backed layout,
injected `now_fn` so age_s is deterministic.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from tui.model.repo_model import RepoBranchRow, RepoModel, RepoRow


# Anchor "now" matches the fake_repos_dir fixture timestamps:
# branch-main: last_used_at = 2026-05-22T13:00:00Z  → age 1h 30m
# branch-feat-x: last_used_at = 2026-05-22T13:30:00Z → age 1h 0m
_NOW = datetime(2026, 5, 22, 14, 30, 0, tzinfo=timezone.utc)


def _now_fn() -> datetime:
    return _NOW


def test_snapshot_empty_dir_returns_empty(tmp_path: Path) -> None:
    d = tmp_path / "repos"
    d.mkdir()
    model = RepoModel(repos_dir=d, now_fn=_now_fn)
    assert model.snapshot() == []


def test_snapshot_one_repo_one_user_branch(tmp_path: Path) -> None:
    root = tmp_path / "repos"
    repo = root / "solo-repo"
    repo.mkdir(parents=True)
    (repo / "repo-meta.json").write_text(json.dumps({
        "name": "solo-repo",
        "url": "git@github.com:acme/solo.git",
        "default_branch": "main",
    }))
    br = repo / "branch-main"
    br.mkdir()
    (br / "branch-meta.json").write_text(json.dumps({
        "branch": "main",
        "slug": "main",
        "created_by": "user",
        "last_indexed_at": "2026-05-22T13:00:00Z",
        "last_used_at": "2026-05-22T14:00:00Z",
    }))
    rows = RepoModel(repos_dir=root, now_fn=_now_fn).snapshot()
    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, RepoRow)
    assert row.name == "solo-repo"
    assert row.url == "git@github.com:acme/solo.git"
    assert row.default_branch == "main"
    assert len(row.branches) == 1
    b = row.branches[0]
    assert isinstance(b, RepoBranchRow)
    assert b.repo_name == "solo-repo"
    assert b.branch == "main"
    assert b.created_by == "user"
    assert b.auto_reason is None
    # 14:00 → 14:30 = 30 min = 1800s
    assert b.age_s == 1800.0


def test_snapshot_user_and_auto_branches_both_present(fake_repos_dir: Path) -> None:
    rows = RepoModel(repos_dir=fake_repos_dir, now_fn=_now_fn).snapshot()
    assert len(rows) == 1
    repo = rows[0]
    assert repo.name == "fake-repo"
    assert len(repo.branches) == 2
    by_branch = {b.branch: b for b in repo.branches}
    assert "main" in by_branch
    assert "feat/x" in by_branch
    assert by_branch["main"].created_by == "user"
    assert by_branch["feat/x"].created_by == "auto"
    assert by_branch["feat/x"].auto_reason == "3 PRs target feat/x"
    assert by_branch["main"].auto_reason is None


def test_snapshot_skips_subdir_missing_repo_meta(tmp_path: Path) -> None:
    root = tmp_path / "repos"
    good = root / "good"
    good.mkdir(parents=True)
    (good / "repo-meta.json").write_text(json.dumps({
        "name": "good", "url": "", "default_branch": "main",
    }))
    # Sub-dir without repo-meta.json — silently skipped.
    (root / "no-meta").mkdir()
    rows = RepoModel(repos_dir=root, now_fn=_now_fn).snapshot()
    assert len(rows) == 1
    assert rows[0].name == "good"


def test_snapshot_skips_corrupt_repo_meta(tmp_path: Path) -> None:
    root = tmp_path / "repos"
    good = root / "good"
    good.mkdir(parents=True)
    (good / "repo-meta.json").write_text(json.dumps({
        "name": "good", "url": "", "default_branch": "main",
    }))
    bad = root / "bad"
    bad.mkdir()
    (bad / "repo-meta.json").write_text("{ this is not json")
    rows = RepoModel(repos_dir=root, now_fn=_now_fn).snapshot()
    assert len(rows) == 1
    assert rows[0].name == "good"


def test_snapshot_skips_non_dict_repo_meta(tmp_path: Path) -> None:
    root = tmp_path / "repos"
    good = root / "good"
    good.mkdir(parents=True)
    (good / "repo-meta.json").write_text(json.dumps({
        "name": "good", "url": "", "default_branch": "main",
    }))
    weird = root / "weird"
    weird.mkdir()
    # JSON array, not an object.
    (weird / "repo-meta.json").write_text(json.dumps(["not", "a", "dict"]))
    rows = RepoModel(repos_dir=root, now_fn=_now_fn).snapshot()
    assert len(rows) == 1
    assert rows[0].name == "good"


def test_has_changed_returns_true_initially_then_false(fake_repos_dir: Path) -> None:
    model = RepoModel(repos_dir=fake_repos_dir, now_fn=_now_fn)
    # Initial call — signature mismatches the cached None.
    assert model.has_changed() is True
    # Take a snapshot to update the cached signature.
    model.snapshot()
    assert model.has_changed() is False
    # Mutate a branch-meta.json mtime → signature changes.
    bm = fake_repos_dir / "fake-repo" / "branch-main" / "branch-meta.json"
    # Force a different mtime (1 hour in the future) so signature differs even on
    # filesystems with low mtime resolution.
    future = time.time() + 3600
    import os as _os
    _os.utime(bm, (future, future))
    assert model.has_changed() is True


def test_age_s_uses_injected_now_fn(tmp_path: Path) -> None:
    """Confirm age_s is driven by the injected `now_fn`, not wall clock."""
    root = tmp_path / "repos"
    repo = root / "r"
    repo.mkdir(parents=True)
    (repo / "repo-meta.json").write_text(json.dumps({
        "name": "r", "url": "", "default_branch": "main",
    }))
    br = repo / "branch-main"
    br.mkdir()
    (br / "branch-meta.json").write_text(json.dumps({
        "branch": "main",
        "slug": "main",
        "created_by": "user",
        "last_indexed_at": "2026-05-22T12:00:00Z",
        "last_used_at": "2026-05-22T12:00:00Z",
    }))

    # 2.5 hour gap from injected now.
    now = datetime(2026, 5, 22, 14, 30, 0, tzinfo=timezone.utc)
    rows = RepoModel(repos_dir=root, now_fn=lambda: now).snapshot()
    assert rows[0].branches[0].age_s == 9000.0  # 2.5h * 3600

    # Different injected now → different age_s.
    now2 = datetime(2026, 5, 22, 13, 0, 0, tzinfo=timezone.utc)
    rows2 = RepoModel(repos_dir=root, now_fn=lambda: now2).snapshot()
    assert rows2[0].branches[0].age_s == 3600.0  # 1h * 3600
