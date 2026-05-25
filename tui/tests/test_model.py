from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

import pytest

from tui.model import queue_model
from tui.model.queue_model import QueueModel


def _model(path: Path, now: datetime) -> QueueModel:
    return QueueModel(queue_path=path, now_fn=lambda: now)


def test_snapshot_parses_all_rows(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot()
    assert snap.total == 6
    assert len(snap.rows) == 6
    assert snap.missing is False


def test_snapshot_filter_open_excludes_merged(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot(filter_mode="open")
    assert len(snap.rows) == 5
    assert all(r.status != "merged" for r in snap.rows)
    # `total` is across all statuses regardless of filter.
    assert snap.total == 6


def test_snapshot_filter_ready_is_subset(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot(filter_mode="ready")
    assert len(snap.rows) >= 1
    assert all(r.ready_for_review for r in snap.rows)


def test_snapshot_sort_queue_preserves_queue_file_order(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot(
        filter_mode="all", sort_mode="queue"
    )
    assert [r.number for r in snap.rows] == [100, 101, 99, 5550, 42, 5551]
    assert [r.queue_index for r in snap.rows] == list(range(6))


def test_snapshot_sort_repo_groups(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot(
        filter_mode="all", sort_mode="repo"
    )
    keys = [f"{r.host}:{r.repo}" for r in snap.rows]
    # Every host:repo cluster should be contiguous (no key reappears after a gap).
    seen: set[str] = set()
    last: str | None = None
    for k in keys:
        if k != last:
            assert k not in seen, f"non-contiguous group for {k}: {keys}"
            seen.add(k)
            last = k


def test_has_changed_after_mtime_bump(fake_queue_path, frozen_now):
    model = _model(fake_queue_path, frozen_now)
    model.snapshot()
    assert model.has_changed() is False
    # Bump mtime by a wide margin so the filesystem resolution can't hide it.
    new_mtime = fake_queue_path.stat().st_mtime + 5
    os.utime(fake_queue_path, (new_mtime, new_mtime))
    assert model.has_changed() is True


def test_snapshot_empty_when_file_missing(missing_queue_path, frozen_now):
    model = _model(missing_queue_path, frozen_now)
    snap = model.snapshot()
    assert snap.missing is True
    assert snap.total == 0
    assert snap.rows == []


def test_ready_count_matches_helper(fake_queue_path, frozen_now):
    # Compute expected count by calling queue_io.ready_for_review directly on the
    # raw fixture entries with the same frozen clock.
    import queue_io  # type: ignore[import-not-found]

    raw = json.loads(fake_queue_path.read_text(encoding="utf-8"))
    expected = sum(
        1 for e in raw.get("prs", []) if queue_io.ready_for_review(e, now=frozen_now)
    )
    snap = _model(fake_queue_path, frozen_now).snapshot()
    assert snap.ready_count == expected
    assert expected >= 1


def test_platform_summary_mixed(fake_queue_path, frozen_now):
    snap = _model(fake_queue_path, frozen_now).snapshot()
    assert snap.platform_summary == "github+bitbucket"


def test_title_falls_back_to_prepared_task_pr_json(tmp_path, frozen_now, monkeypatch):
    queue = tmp_path / "q.json5"
    queue.write_text(json.dumps({
        "prs": [{
            "pr_url": "https://github.com/acme/foo/pull/42",
            "status": "pending",
            "head_sha": "abc",
        }]
    }))
    task_root = tmp_path / "skill-pr-review"
    task_dir = task_root / "foo_pr-42"
    task_dir.mkdir(parents=True)
    (task_dir / "pr.json").write_text(json.dumps({"title": "Fallback title from task"}))
    monkeypatch.setattr(queue_model, "_PR_REVIEW_ROOT", task_root)

    snap = _model(queue, frozen_now).snapshot()

    assert snap.rows[0].title == "Fallback title from task"
