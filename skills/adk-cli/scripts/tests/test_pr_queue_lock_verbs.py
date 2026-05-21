"""v4 §6.v lock-handling verbs: claim / heartbeat / release / set-status.

The agent (or TUI) calls these around a long-running review:
  1. claim   — set taken_at + status=in_review
  2. (review runs; heartbeat every ~5 min)
  3. heartbeat — bump taken_at
  4. set-status — mid-review transitions (e.g. → 'reviewed')
  5. release — clear taken_at; optionally set terminal status
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import pytest
import pr_queue
from queue_io import STATUS_IN_REVIEW, STATUS_APPROVED


def _write_queue(path: Path, prs: list[dict]) -> None:
    path.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")


def test_claim_sets_taken_at_and_status(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "head_sha": "abc"},
    ])
    ns = argparse.Namespace(
        queue=str(qp), pr_url="https://github.com/acme/foo/pull/1", force=False,
    )
    rc = pr_queue.cmd_claim(ns)
    assert rc == 0
    row = json.loads(qp.read_text())["prs"][0]
    assert row["taken_at"] is not None
    assert row["status"] == STATUS_IN_REVIEW


def test_claim_fails_on_active_lock(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    from datetime import datetime, timezone
    fresh = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_queue(qp, [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc", "taken_at": fresh},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1", force=False)
    with pytest.raises(SystemExit):
        pr_queue.cmd_claim(ns)


def test_claim_force_overrides_active_lock(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    from datetime import datetime, timezone
    fresh = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_queue(qp, [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc", "taken_at": fresh},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1", force=True)
    rc = pr_queue.cmd_claim(ns)
    assert rc == 0


def test_heartbeat_bumps_taken_at(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "u1", "status": "in_review", "head_sha": "abc",
         "taken_at": "2026-05-21T00:00:00Z"},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1")
    rc = pr_queue.cmd_heartbeat(ns)
    assert rc == 0
    row = json.loads(qp.read_text())["prs"][0]
    assert row["taken_at"] != "2026-05-21T00:00:00Z"


def test_heartbeat_fails_without_active_claim(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "u1", "status": "pending", "head_sha": "abc", "taken_at": None},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1")
    with pytest.raises(SystemExit):
        pr_queue.cmd_heartbeat(ns)


def test_set_status_mid_review(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "u1", "status": "in_review", "head_sha": "abc",
         "taken_at": "2026-05-21T00:00:00Z"},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1", status="reviewed")
    rc = pr_queue.cmd_set_status(ns)
    assert rc == 0
    row = json.loads(qp.read_text())["prs"][0]
    assert row["status"] == "reviewed"
    # Lock is preserved.
    assert row["taken_at"] == "2026-05-21T00:00:00Z"


def test_release_clears_taken_at(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "u1", "status": "in_review", "head_sha": "abc",
         "taken_at": "2026-05-21T00:00:00Z"},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1", status=None)
    rc = pr_queue.cmd_release(ns)
    assert rc == 0
    row = json.loads(qp.read_text())["prs"][0]
    assert row["taken_at"] is None
    assert row["status"] == "in_review"  # unchanged when --status absent


def test_release_with_status_sets_terminal(tmp_path):
    qp = tmp_path / "pr-queue.json5"
    _write_queue(qp, [
        {"pr_url": "u1", "status": "in_review", "head_sha": "abc",
         "taken_at": "2026-05-21T00:00:00Z"},
    ])
    ns = argparse.Namespace(queue=str(qp), pr_url="u1", status=STATUS_APPROVED)
    rc = pr_queue.cmd_release(ns)
    assert rc == 0
    row = json.loads(qp.read_text())["prs"][0]
    assert row["taken_at"] is None
    assert row["status"] == STATUS_APPROVED
