from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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
def eligible_queue_path(tmp_path: Path) -> Path:
    """A queue file with exactly one row that's ready_for_review=True."""
    src = _FIXTURES_DIR / "eligible_queue.json5"
    dst = tmp_path / "eligible-queue.json5"
    shutil.copyfile(src, dst)
    return dst
