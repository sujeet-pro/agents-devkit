"""Tests for `pr_queue.get_next_eligible` — the API-validated picker that
auto-drops merged/declined rows discovered at claim time.

Wired in as `adk pr-queue get-next` and used by `run_review.py` in queue
mode. The previous design (calling `acquire_next_row` directly) could hand
back a row that had merged between scans; this fixes that.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import pr_queue
from queue_io import (
    STATUS_PENDING, STATUS_MERGED, STATUS_DECLINED,
    read_queue,
)


def _write_queue(tmp_path: Path, prs: list[dict]) -> Path:
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


def test_get_next_returns_eligible_row(tmp_path, monkeypatch):
    """API says OPEN → row is returned (with taken_at claim)."""
    q = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
         "status": STATUS_PENDING, "head_oid": "abc"},
    ])
    # cheap_pr_meta is imported from pr_scan inside get_next_eligible. Patch
    # the source module so the late import picks up the stub.
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda url, log: {"merged_at": None, "state": "OPEN",
                                          "head_oid": "abc"})

    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is not None
    assert row["pr_link"] == "https://github.com/acme/foo/pull/1"
    # And it's marked claimed in the persisted file.
    persisted = read_queue(q)["prs"][0]
    assert persisted["taken_at"]


def test_get_next_drops_merged_row_and_picks_next(tmp_path, monkeypatch):
    """Two rows; API says #1 is now merged (since last sync); picker drops
    it and returns #2. The task folder for #1 (if any) goes away too."""
    q = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
         "status": STATUS_PENDING, "head_oid": "abc"},
        {"pr_link": "https://github.com/acme/foo/pull/2",
         "status": STATUS_PENDING, "head_oid": "def"},
    ])

    def fake_meta(url, log):
        if url.endswith("/1"):
            return {"merged_at": "2026-05-21T10:00Z", "state": "MERGED",
                    "head_oid": "abc"}
        return {"merged_at": None, "state": "OPEN", "head_oid": "def"}

    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta", fake_meta)

    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is not None
    assert row["pr_link"].endswith("/2")
    # #1 was dropped from the queue.
    persisted = read_queue(q)["prs"]
    assert len(persisted) == 1
    assert persisted[0]["pr_link"].endswith("/2")


def test_get_next_drops_declined_row(tmp_path, monkeypatch):
    """Same as merged, but for Bitbucket-style DECLINED."""
    q = _write_queue(tmp_path, [
        {"pr_link": "https://bitbucket.org/acme/foo/pull-requests/7",
         "status": STATUS_PENDING, "head_oid": "abc"},
        {"pr_link": "https://github.com/acme/foo/pull/9",
         "status": STATUS_PENDING, "head_oid": "def"},
    ])

    def fake_meta(url, log):
        if "bitbucket" in url:
            return {"merged_at": None, "state": "DECLINED", "head_oid": "abc"}
        return {"merged_at": None, "state": "OPEN", "head_oid": "def"}

    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta", fake_meta)

    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is not None
    assert row["pr_link"].endswith("/pull/9")
    persisted = read_queue(q)["prs"]
    assert all("bitbucket.org" not in e["pr_link"] for e in persisted)


def test_get_next_returns_none_when_all_terminal(tmp_path, monkeypatch):
    q = _write_queue(tmp_path, [
        {"pr_link": "u1", "status": STATUS_PENDING, "head_oid": "x"},
    ])
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda url, log: {"merged_at": "2026-05-21T10:00Z",
                                          "state": "MERGED", "head_oid": "x"})
    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is None
    # Row was dropped from the queue.
    assert read_queue(q)["prs"] == []


def test_get_next_refreshes_head_oid_on_eligible(tmp_path, monkeypatch):
    """When API reports a newer head_oid than the cached one, the row is
    updated before being returned — so the downstream skill can index the
    actual head, not a stale snapshot."""
    q = _write_queue(tmp_path, [
        {"pr_link": "u1", "status": STATUS_PENDING, "head_oid": "old"},
    ])
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda url, log: {"merged_at": None, "state": "OPEN",
                                          "head_oid": "new-head-abc"})
    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is not None
    assert row["head_oid"] == "new-head-abc"
    persisted = read_queue(q)["prs"][0]
    assert persisted["head_oid"] == "new-head-abc"


def test_get_next_no_validate_skips_api(tmp_path, monkeypatch):
    """`--no-validate` is the legacy in-memory path; cheap_pr_meta MUST NOT
    be called. Used by tests + by callers who validated separately."""
    q = _write_queue(tmp_path, [
        {"pr_link": "u1", "status": STATUS_PENDING, "head_oid": "x"},
    ])
    calls: list = []
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda *a, **kw: calls.append(a) or {})
    row = pr_queue.get_next_eligible(q, validate=False)
    assert row is not None
    assert calls == []


def test_get_next_skips_locked_rows(tmp_path, monkeypatch):
    """Locked rows (active reviewer holds them) should never come back from
    get_next_eligible — even with API validation."""
    # Locked < 30min ago.
    q = _write_queue(tmp_path, [
        {"pr_link": "locked", "status": STATUS_PENDING, "head_oid": "x",
         "taken_at": "2099-12-31T23:59:59Z"},   # far-future → still locked
        {"pr_link": "open", "status": STATUS_PENDING, "head_oid": "y"},
    ])
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda url, log: {"merged_at": None, "state": "OPEN",
                                          "head_oid": "y"})
    row = pr_queue.get_next_eligible(q, validate=True)
    assert row is not None
    assert row["pr_link"] == "open"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
