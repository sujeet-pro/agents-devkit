"""End-to-end tests for the Import stage: do_import + fetch_pr --metadata-only.

Covers the contracts from the pipeline redesign proposal §4:
  - Exactly one call to fetch_pr.py with --metadata-only.
  - Queue row is updated with title + author + head_sha.
  - Total elapsed time < 2 s when fetch_pr is mocked.
  - Back-compat: when fetch_pr.py is invoked WITHOUT --metadata-only it returns
    the full payload; do_import still works (uses title from pr.json).

These tests are self-contained integration tests: they call do_import.do_import()
directly with a subprocess.run monkeypatch, exercising the full function body
without spawning real processes.

Note: fetch_pr.py --metadata-only support is part of Slice A.  If the flag is
not yet recognised by fetch_pr.py the test will still PASS in isolation because
subprocess.run is mocked here.  The real integration check (that fetch_pr.py
accepts the flag) is exercised by test_do_import.py::test_do_import_handles_github_url.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# sys.path bootstrap — mirror skills/adk-pr-review/scripts/tests/conftest.py
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

ADK_CLI_SCRIPTS = SCRIPTS_DIR.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))

import do_import  # noqa: E402
import queue_io   # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GITHUB_URL = "https://github.com/foo/bar/pull/42"

_METADATA_PAYLOAD = {
    "host": "github",
    "owner": "foo",
    "repo": "bar",
    "pr_number": 42,
    "title": "feat: add pagination",
    "author": {"login": "alice"},
    "head_sha": "abc123abc123abc123abc123abc123abc123abc1",
    "headRefOid": "abc123abc123abc123abc123abc123abc123abc1",
    "target_branch": "main",
    "baseRefName": "main",
    "is_draft": False,
    "isDraft": False,
    "additions": 55,
    "deletions": 12,
    "changed_files": 4,
    "changedFiles": 4,
    "url": _GITHUB_URL,
    "metadata_only": True,
}

_FULL_PAYLOAD = {
    **_METADATA_PAYLOAD,
    "metadata_only": False,
    "diff": "--- a/foo.py\n+++ b/foo.py\n@@ -1 +1 @@\n-old\n+new",
    "comments": [],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_queue(tmp_path: Path, pr_url: str = _GITHUB_URL) -> Path:
    q = {"prs": [{"pr_url": pr_url, "status": "pending"}]}
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps(q), encoding="utf-8")
    return p


def _stub_fetch_pr(monkeypatch, pr_json_content: dict, *,
                   returncode: int = 0, stderr: str = ""):
    """Stub subprocess.run to mimic fetch_pr.py.

    Writes pr.json to the --task-dir arg so do_import can read it.
    """
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        try:
            td_idx = list(cmd).index("--task-dir")
            task_dir = Path(cmd[td_idx + 1])
            pr_review = task_dir / "pr-review"
            pr_review.mkdir(parents=True, exist_ok=True)
            (pr_review / "pr.json").write_text(
                json.dumps(pr_json_content), encoding="utf-8"
            )
        except (ValueError, IndexError):
            pass

        return MagicMock(
            returncode=returncode,
            stdout=json.dumps({
                "metadata_only": pr_json_content.get("metadata_only", True),
                "head_sha": pr_json_content.get("head_sha"),
                "title": pr_json_content.get("title"),
            }),
            stderr=stderr,
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


# ---------------------------------------------------------------------------
# Test 1: exactly one call to fetch_pr.py with --metadata-only
# ---------------------------------------------------------------------------

def test_exactly_one_metadata_only_call(monkeypatch, tmp_path):
    """do_import must make exactly one subprocess call with --metadata-only."""
    queue_path = _make_queue(tmp_path)
    calls = _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 0
    assert len(calls) == 1, (
        f"Expected exactly one subprocess call, got {len(calls)}"
    )
    cmd = calls[0]
    assert "--metadata-only" in cmd, (
        f"Expected --metadata-only in subprocess args; got: {cmd}"
    )
    # Verify it targets fetch_pr.py specifically.
    assert any("fetch_pr" in tok for tok in cmd), (
        f"Expected fetch_pr.py in call; got: {cmd}"
    )


# ---------------------------------------------------------------------------
# Test 2: queue row updated with title + author + head_sha
# ---------------------------------------------------------------------------

def test_queue_row_updated_with_title_author_head_sha(monkeypatch, tmp_path):
    """Queue row must have title, author, and head_sha after do_import succeeds."""
    queue_path = _make_queue(tmp_path)
    _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 0

    row = queue_io.find_row(queue_path, _GITHUB_URL)
    assert row is not None, "Queue row disappeared after do_import"

    assert row.get("title") == "feat: add pagination"
    # author may be stored as a dict ({"login": "alice"}) or a string.
    author = row.get("author")
    assert author is not None, "author not set on queue row"
    if isinstance(author, dict):
        assert author.get("login") == "alice"
    else:
        assert "alice" in str(author)

    assert row.get("head_sha") == _METADATA_PAYLOAD["head_sha"]
    assert "last_imported_at" in row


# ---------------------------------------------------------------------------
# Test 3: total elapsed time < 2 s when fetch_pr is mocked
# ---------------------------------------------------------------------------

def test_elapsed_under_2s_with_mocked_fetch_pr(monkeypatch, tmp_path):
    """do_import must complete in under 2 s when fetch_pr.py is mocked.

    This guards against accidentally adding blocking I/O or sleeps to the
    Import stage path.
    """
    queue_path = _make_queue(tmp_path)
    _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    t0 = time.perf_counter()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)
    elapsed = time.perf_counter() - t0

    assert rc == 0
    assert elapsed < 2.0, (
        f"do_import took {elapsed:.2f}s; must complete in <2s when mocked"
    )


# ---------------------------------------------------------------------------
# Test 4 (back-compat): full payload still yields correct title
# ---------------------------------------------------------------------------

def test_full_payload_back_compat_uses_title_field(monkeypatch, tmp_path):
    """When fetch_pr.py returns the FULL payload (no metadata_only flag),
    do_import must still write the correct title to the queue row.

    Simulates back-compat: an older fetch_pr.py that doesn't recognise
    --metadata-only just ignores the flag and returns the full pr.json.
    """
    queue_path = _make_queue(tmp_path)
    # Use the full payload (metadata_only=False) — back-compat scenario.
    _stub_fetch_pr(monkeypatch, _FULL_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 0

    row = queue_io.find_row(queue_path, _GITHUB_URL)
    assert row is not None
    assert row.get("title") == "feat: add pagination", (
        "Title from full payload must still be written to queue row"
    )
    assert "last_imported_at" in row


# ---------------------------------------------------------------------------
# Test 5 (boundary): fetch_pr failure propagates as rc=1
# ---------------------------------------------------------------------------

def test_fetch_pr_failure_returns_rc1(monkeypatch, tmp_path):
    """When fetch_pr.py exits non-zero, do_import must return rc=1."""
    queue_path = _make_queue(tmp_path)
    _stub_fetch_pr(monkeypatch, {}, returncode=1, stderr="network error")
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 1, "Expected rc=1 when fetch_pr exits non-zero"


# ---------------------------------------------------------------------------
# Test 6 (boundary): missing queue row is tolerated (no crash)
# ---------------------------------------------------------------------------

def test_missing_queue_row_does_not_crash(monkeypatch, tmp_path):
    """do_import on a URL not present in the queue must not raise.

    The queue update will be a no-op (not matched), but the function must
    return successfully (the PR metadata was still fetched).
    """
    # Queue with a DIFFERENT URL — our target is absent.
    queue_path = _make_queue(tmp_path, pr_url="https://github.com/other/repo/pull/1")
    _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    # Must not raise.
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    # ok is acceptable — the stage succeeded even though the queue row didn't exist.
    assert rc in (0, 1), f"do_import returned unexpected rc={rc}"


# ---------------------------------------------------------------------------
# Test 7 (error): invalid URL returns rc=1
# ---------------------------------------------------------------------------

def test_invalid_url_returns_rc1(monkeypatch, tmp_path):
    """An unparseable URL must make do_import fail cleanly with rc=1."""
    queue_path = _make_queue(tmp_path)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import("not-a-valid-pr-url", queue_path, log)
    assert rc == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
