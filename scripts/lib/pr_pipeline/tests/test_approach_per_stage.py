"""Test that each pipeline stage function emits exactly one fork_id entry to
decisions.jsonl via pick_approach, with the expected fork_id and recommended
choice.

Coverage:
  - Every stage (do_import, do_sync, do_index, do_review, do_validate, do_post)
    appends exactly one JSONL line to decisions.jsonl.
  - do_index recommended choice is "rebuild" when rebuild=True and
    "seed-and-overlay" when rebuild=False.
  - do_review recommended choice is "deep" when deep=True, "detailed" when
    detailed=True, and "default" otherwise.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# sys.path: scripts/lib must be on path (handled by conftest) so that
# `from pr_pipeline.stages import ...` resolves.  We also need decision_logger
# which lives one level above scripts/lib.
# ---------------------------------------------------------------------------

_SCRIPTS_LIB = Path(__file__).resolve().parents[2]
_SCRIPTS_ROOT = _SCRIPTS_LIB.parent
for _p in [str(_SCRIPTS_LIB), str(_SCRIPTS_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Add adk-cli scripts to path so queue_io is importable from do_index etc.
_ADK_CLI_SCRIPTS = _SCRIPTS_ROOT.parent / "skills" / "adk-cli" / "scripts"
_ADK_PR_REVIEW_SCRIPTS = _SCRIPTS_ROOT.parent / "skills" / "adk-pr-review" / "scripts"
for _p in [str(_ADK_CLI_SCRIPTS), str(_ADK_PR_REVIEW_SCRIPTS)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pr_pipeline.state import PRState, StageResult  # noqa: E402
from pr_pipeline import stages as _stages_mod  # noqa: E402
import decision_logger as _dl  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STUB_URL = "https://github.com/foo/bar/pull/42"


def _make_state(tmp_path: Path) -> PRState:
    td = tmp_path / "bar_pr-42"
    td.mkdir(parents=True, exist_ok=True)
    return PRState(
        pr_url=_STUB_URL,
        repo="bar",
        pr_number=42,
        task_dir=td,
    )


def _make_queue(tmp_path: Path) -> Path:
    qp = tmp_path / "pr-queue.json5"
    qp.write_text(
        json.dumps({"prs": [{"pr_url": _STUB_URL, "status": "pending"}]}),
        encoding="utf-8",
    )
    return qp


def _isolate_decision_log(monkeypatch, tmp_path: Path) -> Path:
    """Redirect decision_logger to a fresh temp file. Returns the decisions.jsonl path."""
    log_dir = tmp_path / "learning"
    log_file = log_dir / "decisions.jsonl"
    monkeypatch.setattr(_dl, "LOG_DIR", log_dir)
    monkeypatch.setattr(_dl, "LOG_FILE", log_file)
    return log_file


def _read_decisions(log_file: Path) -> list[dict]:
    if not log_file.exists():
        return []
    return [json.loads(ln) for ln in log_file.read_text(encoding="utf-8").splitlines() if ln.strip()]


# Fake subprocess.run and Popen that succeed without launching anything.
class _FakeCP:
    returncode = 0
    stdout = json.dumps({
        "status": "ok",
        "head_sha": "deadbeef" * 5,
        "title": "Stub PR",
        "author": {"login": "dev1"},
        "target_branch": "main",
        "is_draft": False,
        "additions": 10,
        "deletions": 2,
        "changed_files": 3,
        "metadata_only": True,
    })
    stderr = ""


def _fake_run(cmd, **kwargs):
    return _FakeCP()


class _FakePopen:
    def __init__(self, cmd, *_a, **_kw):
        self.returncode = 0
        self.stdout = None
        self.pid = -1

    def poll(self):
        return 0

    def wait(self, *_a, **_kw):
        return 0


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def env(monkeypatch, tmp_path):
    """Isolated environment: patched subprocess + fresh decision log."""
    monkeypatch.setattr(subprocess, "run", _fake_run)
    monkeypatch.setattr(subprocess, "Popen", _FakePopen)
    log_file = _isolate_decision_log(monkeypatch, tmp_path)
    state = _make_state(tmp_path)
    queue_path = _make_queue(tmp_path)
    log = MagicMock()
    return SimpleNamespace(
        state=state,
        queue_path=queue_path,
        log=log,
        log_file=log_file,
        tmp_path=tmp_path,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_do_import_emits_import_source_fork(env):
    """do_import writes exactly one decision with fork_id='import-source'."""
    _stages_mod.do_import(env.state, queue_path=env.queue_path, log=env.log)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "import-source"
    assert entries[0]["skill"] == "adk-pr-review"


def test_do_sync_emits_sync_scope_fork(env):
    """do_sync writes exactly one decision with fork_id='sync-scope'."""
    _stages_mod.do_sync(env.state, queue_path=env.queue_path, log=env.log)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "sync-scope"


def test_do_index_emits_index_mode_fork_seed_and_overlay(env):
    """do_index with rebuild=False recommends 'seed-and-overlay'."""
    _stages_mod.do_index(env.state, queue_path=env.queue_path, log=env.log, rebuild=False)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "index-mode"
    assert entries[0].get("user_chose") == "seed-and-overlay", (
        f"Expected user_chose='seed-and-overlay', got {entries[0].get('user_chose')!r}"
    )


def test_do_index_emits_index_mode_fork_rebuild(env):
    """do_index with rebuild=True recommends 'rebuild'."""
    _stages_mod.do_index(env.state, queue_path=env.queue_path, log=env.log, rebuild=True)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "index-mode"
    assert entries[0].get("user_chose") == "rebuild", (
        f"Expected user_chose='rebuild', got {entries[0].get('user_chose')!r}"
    )


def test_do_review_emits_review_depth_fork_default(env):
    """do_review with deep=False, detailed=False recommends 'default'."""
    _stages_mod.do_review(
        env.state,
        queue_path=env.queue_path,
        log=env.log,
        deep=False,
        detailed=False,
    )
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "review-depth"
    assert entries[0].get("user_chose") == "default", (
        f"Expected user_chose='default', got {entries[0].get('user_chose')!r}"
    )


def test_do_review_emits_review_depth_fork_deep(env):
    """do_review with deep=True recommends 'deep'."""
    _stages_mod.do_review(
        env.state,
        queue_path=env.queue_path,
        log=env.log,
        deep=True,
        detailed=False,
    )
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "review-depth"
    assert entries[0].get("user_chose") == "deep", (
        f"Expected user_chose='deep', got {entries[0].get('user_chose')!r}"
    )


def test_do_review_emits_review_depth_fork_detailed(env):
    """do_review with deep=False, detailed=True recommends 'detailed'."""
    _stages_mod.do_review(
        env.state,
        queue_path=env.queue_path,
        log=env.log,
        deep=False,
        detailed=True,
    )
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "review-depth"
    assert entries[0].get("user_chose") == "detailed", (
        f"Expected user_chose='detailed', got {entries[0].get('user_chose')!r}"
    )


def test_do_validate_emits_validate_strict_fork(env):
    """do_validate writes exactly one decision with fork_id='validate-strict'."""
    _stages_mod.do_validate(env.state, queue_path=env.queue_path, log=env.log)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "validate-strict"


def test_do_post_emits_post_policy_fork(env):
    """do_post writes exactly one decision with fork_id='post-policy'."""
    _stages_mod.do_post(env.state, queue_path=env.queue_path, log=env.log)
    entries = _read_decisions(env.log_file)
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}: {entries}"
    assert entries[0]["fork_id"] == "post-policy"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
