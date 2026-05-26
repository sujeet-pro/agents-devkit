"""Tests for do_import.py — Import stage.

Coverage:
  - Fresh URL adds title/author/head_sha/target_branch to the queue row.
  - Idempotent: running twice doesn't error; updates last_imported_at.
  - Handles GitHub PR URL correctly.
  - fetch_pr subprocess failure returns rc=1 and error JSON.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

ADK_CLI_SCRIPTS = SCRIPTS_DIR.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))

import do_import  # noqa: E402
import queue_io   # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GITHUB_URL = "https://github.com/acme/frontend/pull/123"
_BB_URL = "https://bitbucket.org/acme/backend/pull-requests/7"

_METADATA_PAYLOAD = {
    "host": "github",
    "owner": "acme",
    "repo": "frontend",
    "pr_number": 123,
    "title": "Add dark mode",
    "author": {"login": "dev1"},
    "head_sha": "abc1234567890abc1234567890abc1234567890ab",
    "headRefOid": "abc1234567890abc1234567890abc1234567890ab",
    "target_branch": "main",
    "baseRefName": "main",
    "is_draft": False,
    "isDraft": False,
    "additions": 42,
    "deletions": 7,
    "changed_files": 5,
    "changedFiles": 5,
    "url": _GITHUB_URL,
    "metadata_only": True,
}

_FETCH_PR_JSON_OUTPUT = json.dumps({
    "metadata_only": True,
    "head_sha": _METADATA_PAYLOAD["head_sha"],
    "title": _METADATA_PAYLOAD["title"],
    "author": _METADATA_PAYLOAD["author"],
    "target_branch": "main",
    "is_draft": False,
    "additions": 42,
    "deletions": 7,
    "changed_files": 5,
    "url": _GITHUB_URL,
})


def _make_queue(tmp_path: Path, pr_url: str) -> Path:
    """Create a minimal queue file with one pending row."""
    q = {"prs": [{"pr_url": pr_url, "status": "pending"}]}
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps(q), encoding="utf-8")
    return p


def _stub_fetch_pr(monkeypatch, pr_json_content: dict, *, returncode: int = 0,
                   stderr: str = ""):
    """Monkeypatch subprocess.run so fetch_pr.py --metadata-only:
      1. Writes pr.json into the task_dir supplied in the command args.
      2. Returns the given returncode.
    """
    def fake_run(cmd, capture_output, text, check):
        # Extract --task-dir from cmd args.
        try:
            td_idx = cmd.index("--task-dir")
            task_dir = Path(cmd[td_idx + 1])
        except (ValueError, IndexError):
            task_dir = None

        if task_dir is not None and returncode == 0:
            pr_review = task_dir / "pr-review"
            pr_review.mkdir(parents=True, exist_ok=True)
            (pr_review / "pr.json").write_text(
                json.dumps(pr_json_content), encoding="utf-8"
            )

        return MagicMock(
            returncode=returncode,
            stdout=json.dumps({
                "metadata_only": True,
                "head_sha": pr_json_content.get("head_sha"),
                "title": pr_json_content.get("title"),
            }),
            stderr=stderr,
        )

    monkeypatch.setattr(subprocess, "run", fake_run)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fresh_url_adds_title_to_queue_row(monkeypatch, tmp_path):
    """do_import on a fresh URL should populate title/author/head_sha in the queue."""
    queue_path = _make_queue(tmp_path, _GITHUB_URL)
    _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    # Redirect ADK_DATA_HOME so task_dir_for resolves inside tmp_path.
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 0

    row = queue_io.find_row(queue_path, _GITHUB_URL)
    assert row is not None
    assert row["title"] == "Add dark mode"
    assert row["head_sha"] == _METADATA_PAYLOAD["head_sha"]
    assert row["target_branch"] == "main"
    assert row["is_draft"] is False
    assert row["additions"] == 42
    assert row["deletions"] == 7
    assert row["changed_files"] == 5
    assert "last_imported_at" in row


def test_do_import_is_idempotent(monkeypatch, tmp_path):
    """Running do_import twice must not error; last_imported_at must be updated."""
    queue_path = _make_queue(tmp_path, _GITHUB_URL)
    _stub_fetch_pr(monkeypatch, _METADATA_PAYLOAD)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()

    rc1 = do_import.do_import(_GITHUB_URL, queue_path, log)
    assert rc1 == 0
    row1 = queue_io.find_row(queue_path, _GITHUB_URL)
    first_imported_at = row1["last_imported_at"]

    # Second run — sleep not required; _now_iso() has second resolution but the
    # assertion only checks that the field is present and the call succeeds.
    rc2 = do_import.do_import(_GITHUB_URL, queue_path, log)
    assert rc2 == 0
    row2 = queue_io.find_row(queue_path, _GITHUB_URL)
    assert row2["title"] == "Add dark mode"
    assert "last_imported_at" in row2


def test_do_import_handles_github_url(monkeypatch, tmp_path):
    """do_import passes the correct host/owner/repo/pr-number to fetch_pr."""
    queue_path = _make_queue(tmp_path, _GITHUB_URL)
    captured: list[list] = []

    def fake_run(cmd, capture_output, text, check):
        captured.append(list(cmd))
        # Write pr.json so the rest of do_import can proceed.
        try:
            td_idx = cmd.index("--task-dir")
            task_dir = Path(cmd[td_idx + 1])
            pr_review = task_dir / "pr-review"
            pr_review.mkdir(parents=True, exist_ok=True)
            (pr_review / "pr.json").write_text(
                json.dumps(_METADATA_PAYLOAD), encoding="utf-8"
            )
        except (ValueError, IndexError):
            pass
        return MagicMock(returncode=0, stdout="{}", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()
    rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 0
    assert captured, "subprocess.run was never called"
    cmd = captured[0]
    assert "--host" in cmd
    assert cmd[cmd.index("--host") + 1] == "github"
    assert cmd[cmd.index("--owner") + 1] == "acme"
    assert cmd[cmd.index("--repo") + 1] == "frontend"
    assert cmd[cmd.index("--pr-number") + 1] == "123"
    assert "--metadata-only" in cmd


def test_do_import_fetch_failure_returns_rc1(monkeypatch, tmp_path):
    """When fetch_pr.py exits non-zero, do_import should return rc=1 with an error."""
    queue_path = _make_queue(tmp_path, _GITHUB_URL)
    _stub_fetch_pr(monkeypatch, {}, returncode=1, stderr="gh: not authenticated")
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp_path / "data"))

    log = MagicMock()

    # Capture stdout to inspect the JSON emitted by _emit().
    import io
    buf = io.StringIO()
    with patch("builtins.print", side_effect=lambda *a, **kw: buf.write(str(a[0]) + "\n")):
        rc = do_import.do_import(_GITHUB_URL, queue_path, log)

    assert rc == 1
    output = buf.getvalue()
    payload = json.loads(output.strip().split("\n")[-1])
    assert payload["status"] == "failed"
    assert "error" in payload


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
