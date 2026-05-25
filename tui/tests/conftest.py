from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def pytest_configure(config):
    """Set ADK_*_HOME env vars before any module imports so module-level
    constants (ADK_HOME, REPOS_ROOT, …) resolve without hard-failing."""
    _base = Path(tempfile.mkdtemp(prefix="adk-tui-test-"))
    os.environ.setdefault("ADK_DATA_HOME", str(_base / "data"))
    os.environ.setdefault("ADK_CONFIG_HOME", str(_base / "config"))
    os.environ.setdefault("ADK_MEMORY_HOME", str(_base / "memory"))


@pytest.fixture(autouse=True)
def _adk_home_env(tmp_path_factory, monkeypatch):
    """Redirect ADK_*_HOME to tmp dirs so every test gets an isolated data dir.

    Uses tmp_path_factory.mktemp() with short neutral names rather than tmp_path
    so the resolved paths don't contain test-function names (which could cause
    false pattern-matches in scripts that grep their own argv).
    """
    base = tmp_path_factory.mktemp("adk")
    monkeypatch.setenv("ADK_DATA_HOME", str(base / "d"))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(base / "c"))
    monkeypatch.setenv("ADK_MEMORY_HOME", str(base / "m"))

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def frozen_now() -> datetime:
    return datetime(2026, 5, 21, 18, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def fake_queue_path(tmp_path: Path) -> Path:
    src = _FIXTURES_DIR / "sample_queue.json5"
    dst = tmp_path / "pr-queue.json5"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture
def missing_queue_path(tmp_path: Path) -> Path:
    return tmp_path / "does-not-exist.json5"


@pytest.fixture
def tui_app(fake_queue_path: Path):
    from tui.app import AdkApp

    return AdkApp(queue_path=fake_queue_path, poll_interval=0.05)


@pytest.fixture
def fake_plan_path(tmp_path: Path) -> Path:
    """Path to a non-existent plan file the test can read/write."""
    return tmp_path / "sync-plan.json"


@pytest.fixture
def sync_plan_in_progress(tmp_path: Path) -> Path:
    """A plan file with 2 ok steps + 1 running step + 5 pending."""
    p = tmp_path / "sync-plan.json"
    p.write_text(json.dumps({
        "version": 1,
        "queue": "/tmp/q.json5",
        "argv": [],
        "started_at": "2026-05-22T14:00:00Z",
        "updated_at": "2026-05-22T14:01:30Z",
        "completed_at": None,
        "rc": None,
        "steps": [
            {"name": "pr-scan", "status": "ok", "rc": 0,
             "started_at": "2026-05-22T14:00:00Z",
             "completed_at": "2026-05-22T14:00:42Z"},
            {"name": "pr-queue update --all", "status": "ok", "rc": 0,
             "started_at": "2026-05-22T14:00:42Z",
             "completed_at": "2026-05-22T14:01:20Z"},
            {"name": "pr-queue clean (merged)", "status": "running",
             "rc": None,
             "started_at": "2026-05-22T14:01:20Z",
             "completed_at": None},
            *[{"name": n, "status": "pending", "rc": None,
               "started_at": None, "completed_at": None}
              for n in (
                  "pr-task clean-orphans",
                  "pr-queue remind",
                  "base-index audit",
                  "auto-base cleanup",
                  "pr-task prepare --all",
              )],
        ],
    }))
    return p


@pytest.fixture
def fake_adk_script(tmp_path: Path) -> Path:
    """A tiny /bin/sh script that mimics `adk pr-sync` for action tests.

    Echoes 3 lines and exits 0. Tests that need a long-lived process build
    their own script in-line and pass adk_bin= directly.
    """
    p = tmp_path / "fake-adk"
    p.write_text(
        "#!/bin/sh\n"
        "echo 'pr-scan: running'\n"
        "echo 'pr-scan: 0 new'\n"
        "echo 'done'\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


@pytest.fixture
def fake_claude_script(tmp_path: Path) -> Path:
    """A tiny /bin/sh script that mimics `claude -p ...` for review-action tests.

    Echoes 3 phase lines and exits 0. Tests that need a long-lived or failing
    agent build their own script and pass --agent-bin directly.
    """
    p = tmp_path / "fake-claude"
    p.write_text(
        "#!/bin/sh\n"
        "echo '[claude] phase 2: querying'\n"
        "echo '[claude] phase 5: posting comments'\n"
        "echo '[claude] phase 6: report'\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


@pytest.fixture
def worker_heartbeat_dir(tmp_path: Path) -> Path:
    """tmp subdir the worker writes its heartbeat file into."""
    d = tmp_path / "tui-workers"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def workers_dir_with_two(tmp_path: Path) -> Path:
    """A workers/ dir containing two fresh heartbeat files."""
    d = tmp_path / "workers"
    d.mkdir(parents=True)
    now_iso = "2026-05-22T14:00:00Z"
    for pid, pr in [
        (11111, "https://github.com/acme/foo/pull/42"),
        (22222, "https://github.com/acme/bar/pull/7"),
    ]:
        (d / f"{pid}.json").write_text(
            json.dumps(
                {
                    "pid": pid,
                    "pr_url": pr,
                    "task_type": "review",
                    "agent": "claude",
                    "queue": "/tmp/q",
                    "started_at": now_iso,
                    "last_heartbeat": now_iso,
                    "current_phase": "review",
                    "rc": None,
                }
            )
        )
    return d


@pytest.fixture
def stale_worker_file(tmp_path: Path) -> Path:
    """A workers/ dir with a single STALE heartbeat (5 min ago)."""
    d = tmp_path / "workers"
    d.mkdir(parents=True)
    old_iso = "2026-05-22T13:55:00Z"
    (d / "99999.json").write_text(
        json.dumps(
            {
                "pid": 99999,
                "pr_url": "https://github.com/acme/old/pull/1",
                "task_type": "review",
                "agent": "claude",
                "queue": "/tmp/q",
                "started_at": old_iso,
                "last_heartbeat": old_iso,
                "current_phase": "review",
                "rc": None,
            }
        )
    )
    return d


@pytest.fixture
def fake_slow_adk_script(tmp_path: Path) -> Path:
    """A /bin/sh adk that takes >1s to complete each verb — used by the SIGTERM
    streaming tests. Reads $ADK_SLOW_S (default 2) for sleep duration."""
    p = tmp_path / "slow-adk"
    p.write_text(
        "#!/bin/sh\n"
        'echo "slow-adk $@"\n'
        'sleep "${ADK_SLOW_S:-2}"\n'
        "echo ok\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


@pytest.fixture
def eligible_queue_path(tmp_path: Path) -> Path:
    """A queue file with exactly one row that's ready_for_review=True."""
    src = _FIXTURES_DIR / "eligible_queue.json5"
    dst = tmp_path / "eligible-queue.json5"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture
def eligible_multi_queue(tmp_path: Path) -> Path:
    """A queue with 3 rows, all ready_for_review=True (mirrors eligible_queue.json5
    but with 3 distinct URLs)."""
    src = _FIXTURES_DIR / "eligible_multi_queue.json5"
    dst = tmp_path / "eligible-multi.json5"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture
def fake_repos_dir(tmp_path: Path) -> Path:
    """A `$ADK_DATA_HOME/repos/`-shaped tmp dir for RepoModel/RepoScreen tests.

    Layout:
      repos/
        fake-repo/
          repo-meta.json
          branch-main/          (created_by=user)
            branch-meta.json
          branch-feat-x/        (created_by=auto, with auto_reason)
            branch-meta.json
    """
    root = tmp_path / "repos"
    repo = root / "fake-repo"
    repo.mkdir(parents=True)
    (repo / "repo-meta.json").write_text(json.dumps({
        "name": "fake-repo",
        "url": "git@github.com:acme/fake.git",
        "default_branch": "main",
    }))
    branch = repo / "branch-main"
    branch.mkdir()
    (branch / "branch-meta.json").write_text(json.dumps({
        "branch": "main",
        "slug": "main",
        "created_by": "user",
        "last_indexed_at": "2026-05-22T10:00:00Z",
        "last_used_at": "2026-05-22T13:00:00Z",
    }))
    auto_branch = repo / "branch-feat-x"
    auto_branch.mkdir()
    (auto_branch / "branch-meta.json").write_text(json.dumps({
        "branch": "feat/x",
        "slug": "feat-x",
        "created_by": "auto",
        "last_indexed_at": "2026-05-22T13:30:00Z",
        "last_used_at": "2026-05-22T13:30:00Z",
        "auto_reason": "3 PRs target feat/x",
    }))
    return root
