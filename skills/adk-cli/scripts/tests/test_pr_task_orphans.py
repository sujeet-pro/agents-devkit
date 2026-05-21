"""Tests for `adk pr-task clean-orphans` + `prepare --all`:
- clean-orphans removes folders whose PR is not in the queue, leaves queued ones.
- clean-orphans requires --yes (or --dry-run) before deleting; safer-by-default.
- merged rows also count as orphans (their folders should not survive cleanup).
- prepare --all iterates non-merged queue rows; merged rows are skipped.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import pr_task
from queue_io import STATUS_MERGED, STATUS_PENDING


def _write_queue(path: Path, prs: list[dict]) -> Path:
    p = path / "pr-queue.json5"
    p.write_text(json.dumps({"prs": prs}, indent=2), encoding="utf-8")
    return p


@pytest.fixture
def fake_pr_reviews(tmp_path, monkeypatch):
    monkeypatch.setattr(pr_task, "PR_REVIEWS_ROOT", tmp_path / "pr-reviews")
    (tmp_path / "pr-reviews").mkdir()
    return tmp_path


def test_clean_orphans_keeps_queued_folders(fake_pr_reviews, capsys):
    """Two folders on disk; one PR in the queue → only the unqueued folder
    is reported as an orphan."""
    reviews = pr_task.PR_REVIEWS_ROOT
    (reviews / "foo_pr-1").mkdir()
    (reviews / "bar_pr-2").mkdir()  # this one stays in the queue

    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "https://github.com/acme/bar/pull/2",
         "status": STATUS_PENDING, "head_sha": "x"},
    ])
    args = SimpleNamespace(queue=str(queue), dry_run=True, yes=False)
    rc = pr_task.cmd_clean_orphans(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 1
    assert any("foo_pr-1" in p for p in out["would_remove"])
    assert not any("bar_pr-2" in p for p in out["would_remove"])
    # Nothing actually deleted in dry-run.
    assert (reviews / "foo_pr-1").exists()


def test_clean_orphans_removes_when_yes(fake_pr_reviews, capsys):
    reviews = pr_task.PR_REVIEWS_ROOT
    (reviews / "foo_pr-1").mkdir()
    (reviews / "bar_pr-2").mkdir()

    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "https://github.com/acme/bar/pull/2",
         "status": STATUS_PENDING, "head_sha": "x"},
    ])
    args = SimpleNamespace(queue=str(queue), dry_run=False, yes=True)
    rc = pr_task.cmd_clean_orphans(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 1
    assert not (reviews / "foo_pr-1").exists()
    assert (reviews / "bar_pr-2").exists()


def test_clean_orphans_requires_yes_or_dry_run(fake_pr_reviews, capsys):
    """Default invocation (no --yes, no --dry-run) refuses to delete and
    asks for confirmation. Prevents accidental rm of an unrecognized folder."""
    reviews = pr_task.PR_REVIEWS_ROOT
    (reviews / "foo_pr-1").mkdir()
    queue = _write_queue(fake_pr_reviews, [])
    args = SimpleNamespace(queue=str(queue), dry_run=False, yes=False)
    rc = pr_task.cmd_clean_orphans(args)
    assert rc == 2
    out = capsys.readouterr().out
    assert "Re-run with --yes" in out
    assert (reviews / "foo_pr-1").exists()


def test_merged_row_folder_treated_as_orphan(fake_pr_reviews, capsys):
    """Merged PRs are excluded from `_queued_task_dirs`, so their on-disk
    folders count as orphans during clean-orphans. This is how `pr-sync`
    catches anything `pr-queue clean` may have missed."""
    reviews = pr_task.PR_REVIEWS_ROOT
    (reviews / "foo_pr-1").mkdir()

    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": STATUS_MERGED, "head_sha": "x"},
    ])
    args = SimpleNamespace(queue=str(queue), dry_run=True, yes=False)
    pr_task.cmd_clean_orphans(args)
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 1


def test_clean_orphans_no_op_when_all_queued(fake_pr_reviews, capsys):
    reviews = pr_task.PR_REVIEWS_ROOT
    (reviews / "foo_pr-1").mkdir()
    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": STATUS_PENDING, "head_sha": "x"},
    ])
    args = SimpleNamespace(queue=str(queue), dry_run=False, yes=True)
    rc = pr_task.cmd_clean_orphans(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 0
    assert "no orphans" in out["reason"]


def test_prepare_all_skips_merged_rows(fake_pr_reviews, monkeypatch, capsys):
    """`pr-task prepare --all` should iterate the queue but skip merged
    rows (we're about to drop them in the sync flow)."""
    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": STATUS_PENDING, "head_sha": "x"},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "status": STATUS_MERGED, "head_sha": "y"},
        {"pr_url": "https://github.com/acme/foo/pull/3",
         "status": STATUS_PENDING, "head_sha": "z"},
    ])

    calls: list[str] = []

    def fake_prepare_one(pr_url, *, queue, rebuild, detailed, embed_model, log):
        calls.append(pr_url)
        return {"pr_url": pr_url, "action": "prepared", "head_sha": "abc"}

    monkeypatch.setattr(pr_task, "_prepare_one", fake_prepare_one)
    rc = pr_task.main(["prepare", "--all", "--queue", str(queue)])
    assert rc == 0
    assert calls == [
        "https://github.com/acme/foo/pull/1",
        "https://github.com/acme/foo/pull/3",
    ]


def test_prepare_all_continues_past_failures(fake_pr_reviews, monkeypatch, capsys):
    queue = _write_queue(fake_pr_reviews, [
        {"pr_url": "u1", "status": STATUS_PENDING, "head_sha": "x"},
        {"pr_url": "u2", "status": STATUS_PENDING, "head_sha": "y"},
        {"pr_url": "u3", "status": STATUS_PENDING, "head_sha": "z"},
    ])

    def fake_prepare_one(pr_url, *, queue, rebuild, detailed, embed_model, log):
        if pr_url == "u2":
            return {"pr_url": pr_url, "status": "failed", "reason": "boom"}
        return {"pr_url": pr_url, "action": "prepared"}

    monkeypatch.setattr(pr_task, "_prepare_one", fake_prepare_one)
    # Bypass parse_pr_url validation for the fake URLs by patching it to a no-op.
    monkeypatch.setattr(pr_task, "parse_pr_url",
                        lambda url: {"repo": "fake", "pr_number": hash(url) % 1000})
    rc = pr_task.main(["prepare", "--all", "--queue", str(queue)])
    assert rc == 1  # one failure → rc=1
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 3
    assert any(r.get("status") == "failed" for r in out["prepared"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
