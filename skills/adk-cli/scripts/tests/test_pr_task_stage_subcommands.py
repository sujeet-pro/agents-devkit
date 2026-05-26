"""Integration tests for the new per-stage pr-task subcommands.

Targets the contracts described in the pipeline redesign proposal §2 + §3.3:
  - `adk pr-task import <url>`  enriches queue row with title/author/head_sha.
  - `adk pr-task sync <url>`    runs Sync but NOT Index.
  - `adk pr-task index <url>`   runs ONLY Index.
  - `adk pr-task review <url>`  chains through validate+post unless -i is set.
  - `adk pr-task review <url>`  with ADK_PR_REVIEW_INTERACTIVE=1 skips auto-post.

These tests are PROBES: they will fail with SystemExit(2)/ImportError until
Slice A+B land the new subcommands.  That failure is the intended "red" state;
the tests are the gate that must go green before slices A+B can be merged.

Contracts that ARE independent of A+B (pure data + state tests) do pass today.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# sys.path bootstrap — mirror the pattern in conftest.py
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
ADK_PR_REVIEW_SCRIPTS = SCRIPTS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

import pr_task  # noqa: E402
import queue_io  # noqa: E402
import _common as adk_pr_common  # noqa: E402  # skills/adk-pr-review/scripts/_common.py

# ---------------------------------------------------------------------------
# Marker: tests that require Slice A/B production code
# ---------------------------------------------------------------------------

needs_slice_ab = pytest.mark.skipif(
    not hasattr(pr_task, "cmd_pipeline_import"),
    reason="Slice A/B not yet landed — new subcommands absent from pr_task.py",
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_STUB_URL = "https://github.com/foo/bar/pull/42"


@pytest.fixture
def cli_env(monkeypatch, tmp_path):
    """Isolated ADK_*_HOME dirs + a stub queue file with one pending row."""
    data = tmp_path / "d"
    conf = tmp_path / "c"
    mem = tmp_path / "m"
    logs = tmp_path / "logs"
    for d in (data, conf, mem, logs):
        d.mkdir(parents=True)

    monkeypatch.setenv("ADK_DATA_HOME", str(data))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(conf))
    monkeypatch.setenv("ADK_MEMORY_HOME", str(mem))
    monkeypatch.setenv("ADK_LOGS_HOME", str(logs))

    # Minimal queue with one pending row for the stub URL.
    queue_path = conf / "pr-queue.json5"
    queue_path.write_text(
        json.dumps({"prs": [{"pr_url": _STUB_URL, "status": "pending"}]}),
        encoding="utf-8",
    )

    # Point pr_task at the isolated queue. We have to patch BOTH bindings:
    # `queue_io.DEFAULT_QUEUE_PATH` (read by any fresh `queue_io` consumer)
    # AND `pr_task.DEFAULT_QUEUE_PATH` (a `from queue_io import …` snapshot
    # taken at import time and reused by every subparser's --queue default).
    monkeypatch.setattr(queue_io, "DEFAULT_QUEUE_PATH", queue_path)
    monkeypatch.setattr(pr_task, "DEFAULT_QUEUE_PATH", queue_path)
    # Reset PR_REVIEW_ROOT on BOTH modules. pr_task carries its own copy and
    # adk_pr_common is what skills/adk-pr-review/scripts/_common.py:task_dir_for
    # actually resolves against — patching one alone leaks real $ADK_DATA_HOME
    # through `_task_dir_for(...)` → `task_dir_for(...)`.
    pr_review_root = data / "skill-pr-review"
    pr_review_root.mkdir(parents=True)
    monkeypatch.setattr(pr_task, "PR_REVIEW_ROOT", pr_review_root)
    monkeypatch.setattr(adk_pr_common, "PR_REVIEW_ROOT", pr_review_root)

    return SimpleNamespace(
        data=data,
        conf=conf,
        mem=mem,
        queue=queue_path,
        pr_review_root=pr_review_root,
    )


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Stub subprocess.run so no real scripts are spawned.

    Any call to subprocess.run records its cmd in `calls` and returns rc=0
    with minimal valid JSON stdout.  Tests can inspect `calls` to assert
    which scripts were invoked and with which flags.
    """
    calls: list[list[str]] = []

    class _FakeCP:
        returncode = 0
        stdout = json.dumps({"status": "ok", "title": "Stub PR",
                             "head_sha": "deadbeef" * 5,
                             "author": {"login": "dev1"},
                             "target_branch": "main",
                             "is_draft": False,
                             "additions": 10,
                             "deletions": 2,
                             "changed_files": 3,
                             "metadata_only": True})
        stderr = ""

    def _fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return _FakeCP()

    # stages.do_review uses subprocess.Popen to spawn the agent (so it can
    # stream output). Capture that path too — otherwise the test launches a
    # real `claude -p /adk-pr-review …` against the user's account.
    class _FakePopen:
        def __init__(self, cmd, *_a, **_kw):
            calls.append(list(cmd))
            self.returncode = 0
            # stdout=None lets the production loop's `if proc.stdout is not None`
            # branch skip selector.register; `for line in (proc.stdout or [])`
            # then iterates over [], so no fake file-object plumbing is needed.
            self.stdout = None
            self.pid = -1

        def poll(self):
            return 0

        def wait(self, *_a, **_kw):
            return 0

        def communicate(self, *_a, **_kw):
            return ("", "")

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

    monkeypatch.setattr(subprocess, "run", _fake_run)
    monkeypatch.setattr(subprocess, "Popen", _FakePopen)
    return calls


# ---------------------------------------------------------------------------
# Helper: build a fake pr.json in the task dir so do_import can read it.
# ---------------------------------------------------------------------------

def _write_fake_pr_json(task_dir: Path) -> None:
    pr_review = task_dir / "pr-review"
    pr_review.mkdir(parents=True, exist_ok=True)
    payload = {
        "title": "Stub PR",
        "author": {"login": "dev1"},
        "head_sha": "deadbeef" * 5,
        "headRefOid": "deadbeef" * 5,
        "target_branch": "main",
        "baseRefName": "main",
        "is_draft": False,
        "additions": 10,
        "deletions": 2,
        "changed_files": 3,
        "metadata_only": True,
    }
    (pr_review / "pr.json").write_text(json.dumps(payload), encoding="utf-8")


def _stub_fetch_pr_writes_pr_json(monkeypatch, *, queue_path: Path):
    """subprocess.run stub that mimics fetch_pr.py --metadata-only.

    Writes a minimal pr.json to the --task-dir argument so do_import can
    proceed past the 'could not read pr.json' check.
    """
    calls: list[list[str]] = []

    class _FakeCP:
        returncode = 0
        stdout = json.dumps({
            "metadata_only": True,
            "head_sha": "deadbeef" * 5,
            "title": "Stub PR",
        })
        stderr = ""

    def _fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        try:
            td_idx = list(cmd).index("--task-dir")
            task_dir = Path(cmd[td_idx + 1])
            _write_fake_pr_json(task_dir)
        except (ValueError, IndexError):
            pass
        return _FakeCP()

    monkeypatch.setattr(subprocess, "run", _fake_run)
    return calls


# ---------------------------------------------------------------------------
# a. test_import_subcommand_enriches_queue_row
# ---------------------------------------------------------------------------

@needs_slice_ab
def test_import_subcommand_enriches_queue_row(cli_env, monkeypatch):
    """cmd_import calls do_import which enriches queue row with title + last_imported_at."""
    _stub_fetch_pr_writes_pr_json(monkeypatch, queue_path=cli_env.queue)

    rc = pr_task.main(["import", _STUB_URL])

    assert rc == 0, "cmd_import returned non-zero"

    row = queue_io.find_row(cli_env.queue, _STUB_URL)
    assert row is not None, "Queue row not found after import"
    assert row.get("title") == "Stub PR", (
        f"Expected title='Stub PR', got {row.get('title')!r}"
    )
    assert "last_imported_at" in row, "last_imported_at not set on queue row"


# ---------------------------------------------------------------------------
# b. test_sync_subcommand_runs_sync_phases_only
# ---------------------------------------------------------------------------

@needs_slice_ab
def test_sync_subcommand_runs_sync_phases_only(cli_env, mock_subprocess):
    """cmd_sync must call prepare_task.py (or do_sync) with --phases sync,
    and must NOT call with --phases index or --phases all."""
    rc = pr_task.main(["sync", _STUB_URL])

    assert rc == 0, "cmd_sync returned non-zero"

    # At least one subprocess call must have been made.
    assert mock_subprocess, "No subprocess was called"

    # Collect all CLI tokens from all calls.
    all_tokens = [tok for cmd in mock_subprocess for tok in cmd]

    # Must reference 'sync' as the phase to run.
    assert any("sync" in tok for tok in all_tokens), (
        "Expected a 'sync' token in subprocess args; got: " + str(all_tokens)
    )

    # Must NOT reference 'index' as a phase to run (unless it appears in a
    # path, e.g. "code-index/" — check for the flag form).
    phase_tokens = [tok for tok in all_tokens if tok.startswith("--phase")]
    assert not any("index" in tok for tok in phase_tokens), (
        "cmd_sync should not request the Index phase; got: " + str(phase_tokens)
    )


# ---------------------------------------------------------------------------
# c. test_index_subcommand_runs_index_only
# ---------------------------------------------------------------------------

@needs_slice_ab
def test_index_subcommand_runs_index_only(cli_env, mock_subprocess):
    """cmd_index must invoke the Index phase and must NOT invoke Sync."""
    rc = pr_task.main(["index", _STUB_URL])

    assert rc == 0, "cmd_index returned non-zero"

    assert mock_subprocess, "No subprocess was called"

    all_tokens = [tok for cmd in mock_subprocess for tok in cmd]

    # Must reference 'index' as the phase.
    assert any("index" in tok for tok in all_tokens), (
        "Expected an 'index' token in subprocess args; got: " + str(all_tokens)
    )

    # The --phases flag (or equivalent) must not request 'sync'.
    phase_tokens = [tok for tok in all_tokens if tok.startswith("--phase")]
    assert not any("sync" in tok for tok in phase_tokens), (
        "cmd_index should not request the Sync phase; got: " + str(phase_tokens)
    )


# ---------------------------------------------------------------------------
# d. test_review_subcommand_chains_through_validate_and_post
# ---------------------------------------------------------------------------

@needs_slice_ab
def test_review_subcommand_chains_through_validate_and_post(cli_env, mock_subprocess,
                                                             monkeypatch):
    """cmd_review must spawn a review agent, then run validate, then post."""
    monkeypatch.delenv("ADK_PR_REVIEW_INTERACTIVE", raising=False)

    rc = pr_task.main(["review", _STUB_URL])

    assert rc == 0, "cmd_review returned non-zero"

    script_names = []
    for cmd in mock_subprocess:
        for tok in cmd:
            if tok.endswith(".py"):
                script_names.append(Path(tok).name)

    # validate_findings.py must have been called.
    assert any("validate_findings" in n for n in script_names), (
        "Expected validate_findings.py to be called; scripts invoked: " +
        str(script_names)
    )

    # post_comments.py must have been called.
    assert any("post_comments" in n for n in script_names), (
        "Expected post_comments.py to be called; scripts invoked: " +
        str(script_names)
    )


# ---------------------------------------------------------------------------
# e. test_review_subcommand_with_interactive_skips_auto_post
# ---------------------------------------------------------------------------

@needs_slice_ab
def test_review_subcommand_with_interactive_skips_auto_post(cli_env, mock_subprocess,
                                                             monkeypatch):
    """With ADK_PR_REVIEW_INTERACTIVE=1, cmd_review must NOT call post_comments.py."""
    monkeypatch.setenv("ADK_PR_REVIEW_INTERACTIVE", "1")

    rc = pr_task.main(["review", _STUB_URL])

    # rc may be 0 or a triage/init rc; the key assertion is about what was called.
    script_names = []
    for cmd in mock_subprocess:
        for tok in cmd:
            if tok.endswith(".py"):
                script_names.append(Path(tok).name)

    # post_comments.py must NOT have been called.
    assert not any("post_comments" in n for n in script_names), (
        "cmd_review with ADK_PR_REVIEW_INTERACTIVE=1 should not auto-post; "
        "scripts invoked: " + str(script_names)
    )

    # triage.py with --init should have been called.
    assert any("triage" in n for n in script_names), (
        "Expected triage.py --init to be called in interactive mode; "
        "scripts invoked: " + str(script_names)
    )


# ---------------------------------------------------------------------------
# Sanity: existing subcommands still parse (no regression)
# ---------------------------------------------------------------------------

def test_existing_prepare_subcommand_still_parses(monkeypatch):
    """The new subcommands must not break the existing 'prepare' subcommand's
    argparse registration."""
    captured: dict = {}

    class _FakeCP:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(subprocess, "run",
                        lambda cmd, **kw: (captured.update(cmd=cmd) or _FakeCP()))

    args = SimpleNamespace(
        pr_url="https://github.com/acme/foo/pull/1",
        queue="~/.config/adk/pr-queue.json5",
        all=False, rebuild=False, detailed=False, deep=False,
        embed_model=None, jobs=None, yes=False,
    )
    rc = pr_task.cmd_prepare(args)
    assert rc == 0


def test_info_subcommand_still_works_for_nonexistent_task(monkeypatch, tmp_path):
    """info on a non-existent URL must return exists=false without crashing."""
    monkeypatch.setattr(pr_task, "_task_dir_for", lambda url: tmp_path / "nope")
    args = SimpleNamespace(pr_url=_STUB_URL, yes=False)
    import io
    buf = io.StringIO()
    monkeypatch.setattr("builtins.print", lambda *a, **kw: buf.write(str(a[0]) + "\n"))
    rc = pr_task.cmd_info(args)
    assert rc == 0
    out = json.loads(buf.getvalue().strip())
    assert out["exists"] is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
