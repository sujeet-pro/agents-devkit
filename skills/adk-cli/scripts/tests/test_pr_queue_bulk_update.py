"""Tests for `adk pr-queue update` bulk + --full semantics:
- list --urls-only emits one URL per line (used by shell completion).
- update (no arg, no --all) errors out cleanly.
- update <url> --all is rejected (mutually exclusive).
- update --all iterates non-merged rows, skips merged ones, and continues
  past per-row failures with rc=1.
- update --full invokes prepare_task.py --prepare-only and folds its output.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

import pr_queue
from queue_io import STATUS_MERGED, STATUS_PENDING


def _write_queue(tmp_path: Path, prs: list[dict]) -> Path:
    """Write a json5 queue (the loader handles plain JSON too)."""
    p = tmp_path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


def test_list_urls_only(tmp_path, capsys):
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1"},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": STATUS_MERGED},
    ])
    args = SimpleNamespace(queue=str(queue_path), status=None, urls_only=True)
    rc = pr_queue.cmd_list(args)
    assert rc == 0
    assert capsys.readouterr().out.splitlines() == [
        "https://github.com/acme/foo/pull/1",
        "https://github.com/acme/foo/pull/2",
    ]


def test_list_urls_only_with_status_filter(tmp_path, capsys):
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "u1", "status": "pending"},
        {"pr_url": "u2", "status": STATUS_MERGED},
    ])
    args = SimpleNamespace(queue=str(queue_path), status=STATUS_MERGED, urls_only=True)
    pr_queue.cmd_list(args)
    assert capsys.readouterr().out.splitlines() == ["u2"]


def test_update_requires_url_or_all(tmp_path):
    queue_path = _write_queue(tmp_path, [])
    with pytest.raises(SystemExit):
        pr_queue.main(["--queue", str(queue_path), "update"])


def test_update_rejects_url_with_all(tmp_path):
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1"},
    ])
    with pytest.raises(SystemExit):
        pr_queue.main(["--queue", str(queue_path), "update",
                       "https://github.com/acme/foo/pull/1", "--all"])


def test_update_all_with_empty_queue(tmp_path, capsys):
    queue_path = _write_queue(tmp_path, [])
    rc = pr_queue.main(["--queue", str(queue_path), "update", "--all"])
    assert rc == 0
    out = capsys.readouterr().out
    # Message wording was widened to cover closed rows too.
    assert "no rows to refresh" in out


def test_update_all_skips_merged_and_continues_on_failure(tmp_path, capsys, monkeypatch):
    """One simulated per-row failure → rc=1, but the others still ran. Merged
    rows are not touched at all."""
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": STATUS_PENDING},
        {"pr_url": "https://github.com/acme/foo/pull/2", "status": STATUS_MERGED},
        {"pr_url": "https://github.com/acme/foo/pull/3", "status": STATUS_PENDING},
        {"pr_url": "https://github.com/acme/foo/pull/4", "status": STATUS_PENDING},
    ])
    calls: list[str] = []

    def fake_refresh(pr_url, entry, *, queue_path, log):
        calls.append(pr_url)
        if pr_url.endswith("/3"):
            return {"pr_url": pr_url, "status": "failed", "stage": "meta",
                    "reason": "simulated"}
        return {"pr_url": pr_url, "refreshed": "meta", "head_sha": "abc"}

    monkeypatch.setattr(pr_queue, "_refresh_one", fake_refresh)
    rc = pr_queue.main(["--queue", str(queue_path), "update", "--all"])
    assert rc == 1
    # Merged row /pull/2 must be skipped; others processed in order.
    assert calls == [
        "https://github.com/acme/foo/pull/1",
        "https://github.com/acme/foo/pull/3",
        "https://github.com/acme/foo/pull/4",
    ]
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["count"] == 3
    assert any(r.get("status") == "failed" for r in parsed["updated"])


def test_update_full_flag_removed(tmp_path):
    """`pr-queue update --full` no longer exists — `update` is metadata-only
    by design. Heavy prep goes through `adk pr-task prepare` instead.

    Argparse should reject the flag now."""
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": STATUS_PENDING},
    ])
    with pytest.raises(SystemExit):
        pr_queue.main(["--queue", str(queue_path), "update", "--all", "--full"])


def test_refresh_one_metadata_only(tmp_path, monkeypatch):
    """`_refresh_one` no longer accepts a `full=` kwarg. It refreshes the
    queue row's metadata and returns — no subprocess spawning."""
    import pr_scan
    monkeypatch.setattr(pr_scan, "cheap_pr_meta",
                        lambda url, log: {"head_sha": "newhead", "merged_at": None,
                                          "state": "OPEN"})
    queue_path = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1", "status": STATUS_PENDING,
         "head_sha": "oldhead"},
    ])
    spawned: list = []
    monkeypatch.setattr("subprocess.run",
                        lambda *a, **kw: spawned.append(a) or SimpleNamespace(
                            returncode=0, stdout="", stderr=""))

    from _common import get_logger
    log = get_logger("test")
    entry = {"pr_url": "https://github.com/acme/foo/pull/1", "head_sha": "oldhead"}
    out = pr_queue._refresh_one(
        "https://github.com/acme/foo/pull/1", entry,
        queue_path=queue_path, log=log,
    )
    # No subprocess: update is metadata-only by contract.
    assert spawned == []
    assert out["refreshed"] == "meta"
    assert out["head_sha"] == "newhead"
    assert out["head_unchanged"] is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
