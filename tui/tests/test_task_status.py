"""Tests for tui/model/pr_status.py — derive_task_status and ProgressEvent.

All tests use injected ``now`` / fabricated fixtures so they are
independent of wall-clock time and filesystem state.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tui.model.pr_status import (
    ProgressEvent,
    TaskStateInfo,
    PhaseRecord,
    _REVIEW_KIND_TO_PROGRESS_KIND,
    build_progress_from_state,
    build_progress_from_worker,
    derive_task_status,
    read_task_state,
    review_event_to_progress,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class _FakeRow:
    """Minimal duck-type stand-in for QueueRow for derive_task_status tests."""

    pr_url: str = "https://github.com/acme/foo/pull/42"
    status: str = "pending"
    prep_status: str | None = None
    prep_error: str | None = None
    taken_at: str | None = None
    head_sha: str | None = None
    last_reviewed_head_sha: str | None = None
    ready_for_review: bool = False
    # Extra fields (forward-compat).
    slack_post_status: str | None = None


@dataclass
class _FakeWorker:
    """Minimal duck-type stand-in for WorkerRow."""

    pr_url: str = "https://github.com/acme/foo/pull/42"
    task_type: str = "review"
    current_phase: str = ""
    status: str = "running"
    is_stale: bool = False
    age_s: float = 30.0
    log_path: str | None = None
    artifacts: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# derive_task_status — terminal states
# ---------------------------------------------------------------------------

def test_merged_returns_merged() -> None:
    row = _FakeRow(status="merged")
    assert derive_task_status(row, now=_NOW) == "merged"


def test_merged_with_slack_post_status_ok() -> None:
    row = _FakeRow(status="merged", slack_post_status="ok")
    assert derive_task_status(row, now=_NOW) == "merged_with_slack"


def test_merged_with_slack_post_status_failed() -> None:
    row = _FakeRow(status="merged", slack_post_status="failed")
    assert derive_task_status(row, now=_NOW) == "merged_slack_warn"


def test_merged_with_slack_post_status_pending() -> None:
    row = _FakeRow(status="merged", slack_post_status="pending")
    assert derive_task_status(row, now=_NOW) == "slack_pending"


def test_closed_returns_unknown() -> None:
    row = _FakeRow(status="closed")
    assert derive_task_status(row, now=_NOW) == "unknown"


# ---------------------------------------------------------------------------
# derive_task_status — active workers
# ---------------------------------------------------------------------------

def test_active_sync_worker_returns_syncing() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="sync")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "syncing"


def test_active_prepare_worker_returns_indexing() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="prepare")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "indexing"


def test_active_index_worker_returns_indexing() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="index")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "indexing"


def test_active_review_worker_returns_reviewing() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="review")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "reviewing"


def test_active_post_worker_returns_posting() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="post")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "posting"


def test_active_merge_worker_returns_merging() -> None:
    row = _FakeRow()
    worker = _FakeWorker(task_type="merge")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "merging"


def test_stale_worker_is_ignored() -> None:
    row = _FakeRow(prep_status="ready", ready_for_review=True)
    stale = _FakeWorker(task_type="review", is_stale=True)
    assert derive_task_status(row, workers=[stale], now=_NOW) == "ready"


def test_worker_for_different_pr_ignored() -> None:
    row = _FakeRow(pr_url="https://github.com/acme/foo/pull/42",
                   prep_status="ready", ready_for_review=True)
    other = _FakeWorker(pr_url="https://github.com/acme/foo/pull/99",
                        task_type="review")
    assert derive_task_status(row, workers=[other], now=_NOW) == "ready"


# ---------------------------------------------------------------------------
# derive_task_status — stale lock
# ---------------------------------------------------------------------------

def test_expired_taken_at_returns_stale_lock() -> None:
    # taken_at is 3 hours ago; default lock max is 2 h.
    old = _iso(_NOW - timedelta(hours=3))
    row = _FakeRow(taken_at=old)
    assert derive_task_status(row, now=_NOW) == "stale_lock"


def test_fresh_taken_at_does_not_return_stale_lock() -> None:
    # taken_at is 5 minutes ago; lock is still valid.
    fresh = _iso(_NOW - timedelta(minutes=5))
    row = _FakeRow(taken_at=fresh, prep_status="ready", ready_for_review=True)
    # Worker is absent, but taken_at is fresh → not stale_lock.
    result = derive_task_status(row, now=_NOW)
    assert result != "stale_lock"


# ---------------------------------------------------------------------------
# derive_task_status — prep_status-driven states
# ---------------------------------------------------------------------------

def test_prep_status_failed_returns_failed() -> None:
    row = _FakeRow(prep_status="failed", prep_error="git fetch returned 128")
    assert derive_task_status(row, now=_NOW) == "failed"


def test_prep_status_preparing_returns_indexing() -> None:
    row = _FakeRow(prep_status="preparing")
    assert derive_task_status(row, now=_NOW) == "indexing"


def test_prep_status_waiting_for_base_returns_indexing() -> None:
    row = _FakeRow(prep_status="waiting_for_base")
    assert derive_task_status(row, now=_NOW) == "indexing"


def test_prep_status_ready_and_ready_for_review_returns_ready() -> None:
    row = _FakeRow(prep_status="ready", ready_for_review=True)
    assert derive_task_status(row, now=_NOW) == "ready"


def test_no_prep_status_returns_unknown() -> None:
    row = _FakeRow(prep_status=None)
    assert derive_task_status(row, now=_NOW) == "unknown"


# ---------------------------------------------------------------------------
# derive_task_status — needs_re_review
# ---------------------------------------------------------------------------

def test_head_sha_moved_returns_needs_re_review() -> None:
    row = _FakeRow(
        prep_status="ready",
        ready_for_review=True,
        head_sha="abc123",
        last_reviewed_head_sha="deadbeef",
    )
    assert derive_task_status(row, now=_NOW) == "needs_re_review"


def test_head_sha_same_returns_ready() -> None:
    sha = "abc123"
    row = _FakeRow(
        prep_status="ready",
        ready_for_review=True,
        head_sha=sha,
        last_reviewed_head_sha=sha,
    )
    assert derive_task_status(row, now=_NOW) == "ready"


def test_no_last_reviewed_head_sha_not_needs_re_review() -> None:
    """If we have never reviewed, last_reviewed_head_sha is None.
    That should NOT produce needs_re_review (it's just not reviewed yet).
    """
    row = _FakeRow(
        prep_status="ready",
        ready_for_review=True,
        head_sha="abc123",
        last_reviewed_head_sha=None,
    )
    assert derive_task_status(row, now=_NOW) == "ready"


# ---------------------------------------------------------------------------
# derive_task_status — task_state-derived states
# ---------------------------------------------------------------------------

def _make_task_state(
    *,
    has_failed: bool = False,
    last_indexed_sha: str | None = None,
    has_findings: bool = False,
    has_finalized_triage: bool = False,
) -> TaskStateInfo:
    return TaskStateInfo(
        phases={},
        has_failed_phase=has_failed,
        last_indexed_head_sha=last_indexed_sha,
        index_chunk_count=None,
        has_findings=has_findings,
        has_finalized_triage=has_finalized_triage,
    )


def test_task_state_failed_phase_returns_failed() -> None:
    row = _FakeRow(prep_status="ready", ready_for_review=True)
    ts = _make_task_state(has_failed=True)
    assert derive_task_status(row, task_state=ts, now=_NOW) == "failed"


def test_task_state_head_moved_returns_queued_for_index() -> None:
    row = _FakeRow(
        prep_status="ready",
        ready_for_review=True,
        head_sha="new_sha",
        last_reviewed_head_sha="new_sha",  # review is current
    )
    ts = _make_task_state(last_indexed_sha="old_sha")  # index is stale
    assert derive_task_status(row, task_state=ts, now=_NOW) == "queued_for_index"


def test_task_state_head_current_no_queued_for_index() -> None:
    sha = "abc123"
    row = _FakeRow(
        prep_status="ready",
        ready_for_review=True,
        head_sha=sha,
        last_reviewed_head_sha=sha,
    )
    ts = _make_task_state(last_indexed_sha=sha)
    assert derive_task_status(row, task_state=ts, now=_NOW) == "ready"


def test_task_state_findings_no_triage_returns_ready_to_act() -> None:
    row = _FakeRow(prep_status="ready", ready_for_review=True)
    ts = _make_task_state(has_findings=True, has_finalized_triage=False)
    assert derive_task_status(row, task_state=ts, now=_NOW) == "ready_to_act"


def test_task_state_finalized_triage_returns_reviewed() -> None:
    row = _FakeRow(prep_status="ready", ready_for_review=True)
    ts = _make_task_state(has_finalized_triage=True, has_findings=True)
    assert derive_task_status(row, task_state=ts, now=_NOW) == "reviewed"


def test_queue_status_reviewed_returns_reviewed() -> None:
    row = _FakeRow(status="reviewed", prep_status="ready", ready_for_review=True)
    assert derive_task_status(row, now=_NOW) == "reviewed"


def test_queue_status_approved_returns_reviewed() -> None:
    row = _FakeRow(status="approved", prep_status="ready", ready_for_review=True)
    assert derive_task_status(row, now=_NOW) == "reviewed"


# ---------------------------------------------------------------------------
# derive_task_status — ready_to_merge
# ---------------------------------------------------------------------------

def _make_task_state_with_bucket(
    *,
    has_finalized_triage: bool = True,
    merge_status_bucket: str | None = None,
) -> TaskStateInfo:
    return TaskStateInfo(
        phases={},
        has_failed_phase=False,
        last_indexed_head_sha=None,
        index_chunk_count=None,
        has_findings=True,
        has_finalized_triage=has_finalized_triage,
        merge_status_bucket=merge_status_bucket,
    )


def test_ready_to_merge_happy_path() -> None:
    """Approved row + finalized triage + mergeable_now → ready_to_merge."""
    row = _FakeRow(status="approved", prep_status="ready", ready_for_review=True)
    ts = _make_task_state_with_bucket(merge_status_bucket="mergeable_now")
    assert derive_task_status(row, task_state=ts, now=_NOW) == "ready_to_merge"


def test_ready_to_merge_boundary_caveats_stays_reviewed() -> None:
    """Approved row + finalized triage + mergeable_with_caveats → reviewed, not ready_to_merge."""
    row = _FakeRow(status="approved", prep_status="ready", ready_for_review=True)
    ts = _make_task_state_with_bucket(merge_status_bucket="mergeable_with_caveats")
    assert derive_task_status(row, task_state=ts, now=_NOW) == "reviewed"


def test_ready_to_merge_not_approved_stays_reviewed() -> None:
    """Finalized triage + mergeable_now but status != approved → reviewed."""
    row = _FakeRow(status="reviewed", prep_status="ready", ready_for_review=True)
    ts = _make_task_state_with_bucket(merge_status_bucket="mergeable_now")
    assert derive_task_status(row, task_state=ts, now=_NOW) == "reviewed"


def test_ready_to_merge_no_bucket_stays_reviewed() -> None:
    """Approved + finalized triage but no merge-status file → reviewed."""
    row = _FakeRow(status="approved", prep_status="ready", ready_for_review=True)
    ts = _make_task_state_with_bucket(merge_status_bucket=None)
    assert derive_task_status(row, task_state=ts, now=_NOW) == "reviewed"


# ---------------------------------------------------------------------------
# Priority ordering
# ---------------------------------------------------------------------------

def test_active_worker_takes_priority_over_prep_failed() -> None:
    """An active non-stale worker beats prep_status==failed."""
    row = _FakeRow(prep_status="failed")
    worker = _FakeWorker(task_type="review")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "reviewing"


def test_merged_takes_priority_over_active_worker() -> None:
    """Merged terminal state is checked before workers."""
    row = _FakeRow(status="merged")
    worker = _FakeWorker(task_type="review")
    assert derive_task_status(row, workers=[worker], now=_NOW) == "merged"


# ---------------------------------------------------------------------------
# read_task_state — filesystem integration
# ---------------------------------------------------------------------------

def test_read_task_state_missing_dir(tmp_path: Path) -> None:
    result = read_task_state(tmp_path / "skill-pr-review", "foo", 42)
    assert result is None


def test_read_task_state_missing_state_json(tmp_path: Path) -> None:
    task_dir = tmp_path / "skill-pr-review" / "foo_pr-42"
    task_dir.mkdir(parents=True)
    result = read_task_state(tmp_path / "skill-pr-review", "foo", 42)
    assert result is None


def test_read_task_state_parses_phases(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-7"
    task_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({
        "phases": {
            "1_clone": {"status": "ok", "elapsed_ms": 1200},
            "3_index": {
                "status": "ok",
                "head_sha_at_index": "abc123",
                "chunk_count": 128,
                "chunks_embedded": 128,
                "elapsed_ms": 45000,
            },
        }
    }))

    ts = read_task_state(root, "myrepo", 7)

    assert ts is not None
    assert not ts.has_failed_phase
    assert ts.last_indexed_head_sha == "abc123"
    assert ts.index_chunk_count == 128
    assert "1_clone" in ts.phases
    assert "3_index" in ts.phases
    assert ts.phases["3_index"].chunks_embedded == 128


def test_read_task_state_detects_failed_phase(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-8"
    task_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({
        "phases": {
            "3_index": {"status": "failed", "error": "ollama: model not found"},
        }
    }))

    ts = read_task_state(root, "myrepo", 8)

    assert ts is not None
    assert ts.has_failed_phase
    assert ts.phases["3_index"].error == "ollama: model not found"


def test_read_task_state_detects_findings_and_triage(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-9"
    pr_review_dir = task_dir / "pr-review"
    pr_review_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({"phases": {}}))
    (pr_review_dir / "findings.json").write_text("[]")
    (pr_review_dir / "posting-plan.json").write_text("{}")

    ts = read_task_state(root, "myrepo", 9)

    assert ts is not None
    assert ts.has_findings
    assert ts.has_finalized_triage


def test_read_task_state_reads_merge_status_bucket(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-11"
    pr_review_dir = task_dir / "pr-review"
    pr_review_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({"phases": {}}))
    (pr_review_dir / "merge-status.json").write_text(
        json.dumps({"bucket": "mergeable_now", "reason": "no conflicts"})
    )

    ts = read_task_state(root, "myrepo", 11)

    assert ts is not None
    assert ts.merge_status_bucket == "mergeable_now"


def test_read_task_state_merge_status_missing_returns_none_bucket(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-12"
    task_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({"phases": {}}))

    ts = read_task_state(root, "myrepo", 12)

    assert ts is not None
    assert ts.merge_status_bucket is None


def test_read_task_state_triage_json_finalized(tmp_path: Path) -> None:
    root = tmp_path / "skill-pr-review"
    task_dir = root / "myrepo_pr-10"
    pr_review_dir = task_dir / "pr-review"
    pr_review_dir.mkdir(parents=True)
    (task_dir / "state.json").write_text(json.dumps({"phases": {}}))
    (pr_review_dir / "findings.json").write_text("[]")
    (pr_review_dir / "triage.json").write_text(json.dumps({"finalized": True}))

    ts = read_task_state(root, "myrepo", 10)

    assert ts is not None
    assert ts.has_finalized_triage


# ---------------------------------------------------------------------------
# ProgressEvent — dataclass construction
# ---------------------------------------------------------------------------

def test_progress_event_defaults() -> None:
    ev = ProgressEvent(
        op_id="index-foo-42",
        pr_url="https://github.com/acme/foo/pull/42",
        kind="step_start",
        label="indexing",
    )
    assert ev.pct is None
    assert ev.detail is None
    assert ev.error is None
    assert ev.links == {}
    assert ev.timestamp  # non-empty ISO string


def test_progress_event_determinate() -> None:
    ev = ProgressEvent(
        op_id="index-foo-42",
        pr_url="https://github.com/acme/foo/pull/42",
        kind="step_progress",
        label="embed (63/128)",
        pct=49,
        current=63,
        total=128,
        elapsed_ms=12000,
    )
    assert ev.pct == 49
    assert ev.current == 63
    assert ev.total == 128


# ---------------------------------------------------------------------------
# build_progress_from_worker
# ---------------------------------------------------------------------------

def test_build_progress_from_stale_worker_returns_empty() -> None:
    w = _FakeWorker(is_stale=True)
    assert build_progress_from_worker(w) == []


def test_build_progress_from_active_review_worker() -> None:
    w = _FakeWorker(task_type="review", current_phase="phase 4", age_s=90.0)
    events = build_progress_from_worker(w)
    assert len(events) == 1
    ev = events[0]
    assert ev.kind == "step_start"  # no chunk progress → indeterminate
    assert "reviewing" in ev.label
    assert ev.elapsed_ms == 90_000
    assert ev.pct is None


def test_build_progress_from_index_worker_with_chunks() -> None:
    w = _FakeWorker(
        task_type="prepare",
        current_phase="embed",
        age_s=45.0,
        artifacts={"chunks_embedded": 64, "chunk_count": 128},
    )
    events = build_progress_from_worker(w)
    assert len(events) == 1
    ev = events[0]
    assert ev.kind == "step_progress"
    assert ev.pct == 50
    assert ev.current == 64
    assert ev.total == 128


def test_build_progress_includes_log_link() -> None:
    w = _FakeWorker(log_path="/tmp/review.log", task_type="review")
    events = build_progress_from_worker(w)
    assert events[0].links.get("log") == "/tmp/review.log"


# ---------------------------------------------------------------------------
# build_progress_from_state
# ---------------------------------------------------------------------------

def test_build_progress_from_state_emits_step_done() -> None:
    ts = TaskStateInfo(
        phases={
            "1_clone": PhaseRecord(
                name="1_clone", status="ok", head_sha_at_index=None,
                chunk_count=None, chunks_embedded=None, elapsed_ms=1200, error=None,
            ),
            "3_index": PhaseRecord(
                name="3_index", status="failed", head_sha_at_index="abc",
                chunk_count=128, chunks_embedded=64, elapsed_ms=5000,
                error="ollama: model not found",
            ),
        },
        has_failed_phase=True,
        last_indexed_head_sha="abc",
        index_chunk_count=128,
        has_findings=False,
        has_finalized_triage=False,
    )
    events = build_progress_from_state("https://github.com/acme/foo/pull/42", ts)
    assert len(events) == 2
    failed_ev = next(e for e in events if e.label == "3_index")
    assert failed_ev.error == "ollama: model not found"
    ok_ev = next(e for e in events if e.label == "1_clone")
    assert ok_ev.error is None


# ---------------------------------------------------------------------------
# review_event_to_progress — ReviewRunner bridge
# ---------------------------------------------------------------------------

@dataclass
class _FakeReviewEvent:
    """Minimal duck-type stand-in for ReviewEvent (avoids CLI-side import)."""
    kind: str
    label: str
    detail: str | None = None
    pct: int | None = None
    elapsed_ms: int | None = None
    links: dict = field(default_factory=dict)


def test_review_kind_map_covers_all_review_event_kinds() -> None:
    """Every ReviewEventKind must have an entry in _REVIEW_KIND_TO_PROGRESS_KIND."""
    # Taken from review_runner.ReviewEventKind literal.
    expected_kinds = {
        "started", "phase", "progress", "waiting_for_confirmation",
        "completed", "failed", "warning",
    }
    assert expected_kinds == set(_REVIEW_KIND_TO_PROGRESS_KIND.keys())


def test_review_event_phase_maps_to_step_start() -> None:
    ev = _FakeReviewEvent(kind="phase", label="phase 3: embed", elapsed_ms=5000)
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/42")
    assert prog.kind == "step_start"
    assert prog.label == "phase 3: embed"
    assert prog.elapsed_ms == 5000
    assert prog.error is None


def test_review_event_progress_maps_to_step_progress() -> None:
    ev = _FakeReviewEvent(kind="progress", label="chunk 64/128", pct=50)
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/42")
    assert prog.kind == "step_progress"
    assert prog.pct == 50


def test_review_event_completed_maps_to_op_done() -> None:
    ev = _FakeReviewEvent(kind="completed", label="review completed")
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/42")
    assert prog.kind == "op_done"
    assert prog.error is None


def test_review_event_failed_sets_error() -> None:
    ev = _FakeReviewEvent(kind="failed", label="review failed", detail="ollama timeout")
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/42")
    assert prog.kind == "op_error"
    assert prog.error == "ollama timeout"


def test_review_event_warning_does_not_set_error() -> None:
    ev = _FakeReviewEvent(kind="warning", label="minor issue", detail="rate limited")
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/42")
    assert prog.kind == "step_done"
    assert prog.error is None


def test_review_event_pr_url_from_links() -> None:
    """pr_url in links takes priority over the pr_url kwarg."""
    ev = _FakeReviewEvent(
        kind="started",
        label="spawning",
        links={"pr": "https://github.com/acme/foo/pull/99", "log": "/tmp/x.log"},
    )
    prog = review_event_to_progress(ev, pr_url="https://github.com/acme/foo/pull/00")
    assert prog.pr_url == "https://github.com/acme/foo/pull/99"
    assert prog.links.get("log") == "/tmp/x.log"
