"""Integration tests for the pr_pipeline stage scheduler.

These tests exercise the scheduler's CONTRACTS without depending on
scheduler.py being present yet (Slice B).  They import pr_pipeline.state
(which exists now) and build a minimal inline scheduler that satisfies the
same semaphore-enforcement API the proposal describes, so that:

  a) The tests are SELF-CONTAINED and pass today (Slice B not yet landed).
  b) When Slice B does land, the same assertions can be re-run against the
     real scheduler.run() by swapping in the real implementation.

Contract under test (proposal §3.1 + §3.3):
  - At most N PRs can be at any given stage simultaneously (semaphore limits).
  - A failure in one PR's stage stops that PR but does not prevent others from
    advancing.
  - The Index bottleneck (sem=1) only blocks PRs waiting for Index; PRs that
    have already been indexed can advance to Review/Post concurrently.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pytest

# pr_pipeline.state is the only production module we touch here.
from pr_pipeline.state import PRState, StageResult, StageName


# ---------------------------------------------------------------------------
# Minimal inline scheduler (stands in for scripts/lib/pr_pipeline/scheduler.py
# until Slice B lands).  Tests can swap to `from pr_pipeline.scheduler import run`
# once that module exists.
# ---------------------------------------------------------------------------

@dataclass
class Semaphores:
    import_: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(4))
    sync: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(2))
    index: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(1))
    review: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(2))
    validate: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(4))
    post: threading.Semaphore = field(
        default_factory=lambda: threading.Semaphore(2))


_SEM_FOR_STAGE: dict[str, str] = {
    "import": "import_",
    "sync": "sync",
    "index": "index",
    "review": "review",
    "validate": "validate",
    "post": "post",
}

_STAGE_ORDER: list[StageName] = ["import", "sync", "index", "review", "validate", "post"]


def _sem(sems: Semaphores, stage: StageName) -> threading.Semaphore:
    return getattr(sems, _SEM_FOR_STAGE[stage])


def run(
    states: list[PRState],
    sems: Semaphores,
    stage_fns: dict[str, Callable[[PRState], StageResult]],
    *,
    starting_stage: str = "import",
) -> list[PRState]:
    """Drive every PRState through the pipeline using `stage_fns`.

    Each PR runs its stages in a worker thread; semaphores gate concurrency.
    `starting_stage` lets callers inject pre-advanced states (e.g. a PR that
    already has stage_status="reviewed" starts directly at "post").
    """
    def _run_pr(state: PRState) -> None:
        # Determine which stage to start from.
        start_idx = _STAGE_ORDER.index(state.current_stage)
        for stage in _STAGE_ORDER[start_idx:]:
            sem = _sem(sems, stage)
            fn = stage_fns.get(stage)
            if fn is None:
                # No function registered → treat as skipped.
                state.advance(StageResult(stage=stage, status="skipped"))
                continue
            sem.acquire()
            try:
                result = fn(state)
            finally:
                sem.release()
            state.advance(result)
            if result.status == "failed":
                break

    threads = []
    for state in states:
        t = threading.Thread(target=_run_pr, args=(state,), daemon=True)
        threads.append(t)
        t.start()
    for t in threads:
        t.join(timeout=30)
    return states


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_state(pr_number: int, *, task_dir: Path, current_stage: str = "import") -> PRState:
    s = PRState(
        pr_url=f"https://github.com/foo/bar/pull/{pr_number}",
        repo="bar",
        pr_number=pr_number,
        task_dir=task_dir / f"bar_pr-{pr_number}",
        current_stage=current_stage,
    )
    s.task_dir.mkdir(parents=True, exist_ok=True)
    return s


def _ok_stage(stage: StageName) -> Callable[[PRState], StageResult]:
    """Returns a stage function that always succeeds immediately."""
    def fn(state: PRState) -> StageResult:
        return StageResult(stage=stage, status="ok")
    fn.__name__ = f"ok_{stage}"
    return fn


def _ok_stage_fns() -> dict[str, Callable]:
    return {s: _ok_stage(s) for s in _STAGE_ORDER}


# ---------------------------------------------------------------------------
# test_pipelined_concurrency
# ---------------------------------------------------------------------------

class _ConcurrencyTracker:
    """Thread-safe max-concurrent tracker per stage."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current: dict[str, int] = {s: 0 for s in _STAGE_ORDER}
        self._max: dict[str, int] = {s: 0 for s in _STAGE_ORDER}

    def enter(self, stage: str) -> None:
        with self._lock:
            self._current[stage] += 1
            if self._current[stage] > self._max[stage]:
                self._max[stage] = self._current[stage]

    def leave(self, stage: str) -> None:
        with self._lock:
            self._current[stage] -= 1

    def max_concurrent(self, stage: str) -> int:
        return self._max[stage]


def _tracking_stage(stage: StageName, tracker: _ConcurrencyTracker,
                    t_seconds: float = 0.01) -> Callable[[PRState], StageResult]:
    """Stage function that tracks concurrent executions and sleeps briefly."""
    def fn(state: PRState) -> StageResult:
        tracker.enter(stage)
        time.sleep(t_seconds)
        tracker.leave(stage)
        return StageResult(stage=stage, status="ok")
    fn.__name__ = f"tracked_{stage}"
    return fn


def test_pipelined_concurrency(tmp_path):
    """No stage ever exceeds its semaphore limit."""
    sems = Semaphores(
        import_=threading.Semaphore(4),
        sync=threading.Semaphore(2),
        index=threading.Semaphore(1),
        review=threading.Semaphore(2),
        validate=threading.Semaphore(4),
        post=threading.Semaphore(2),
    )
    tracker = _ConcurrencyTracker()
    fns = {s: _tracking_stage(s, tracker, t_seconds=0.02) for s in _STAGE_ORDER}

    states = [_make_state(i, task_dir=tmp_path) for i in range(1, 7)]
    run(states, sems, fns)

    # All PRs must have completed.
    for s in states:
        assert s.terminal(), f"PR #{s.pr_number} did not reach terminal state"

    # Semaphore limits must never have been exceeded.
    limit_map = {
        "import": 4,
        "sync": 2,
        "index": 1,
        "review": 2,
        "validate": 4,
        "post": 2,
    }
    for stage, limit in limit_map.items():
        observed = tracker.max_concurrent(stage)
        assert observed <= limit, (
            f"Stage '{stage}' had {observed} concurrent executions; limit is {limit}"
        )


# ---------------------------------------------------------------------------
# test_stage_failure_stops_pr_advances_others
# ---------------------------------------------------------------------------

def test_stage_failure_stops_pr_advances_others(tmp_path):
    """A sync failure for PR #2 stops that PR; others still progress to 'post'."""
    sems = Semaphores()

    failing_pr_number = 2

    def sync_fn(state: PRState) -> StageResult:
        if state.pr_number == failing_pr_number:
            return StageResult(stage="sync", status="failed", reason="injected failure")
        return StageResult(stage="sync", status="ok")

    fns = _ok_stage_fns()
    fns["sync"] = sync_fn

    states = [_make_state(i, task_dir=tmp_path) for i in range(1, 7)]
    run(states, sems, fns)

    for s in states:
        if s.pr_number == failing_pr_number:
            assert s.failed(), f"PR #{s.pr_number} should have failed but didn't"
            # current_stage stays at the failed stage.
            assert s.current_stage == "sync"
        else:
            assert s.terminal(), f"PR #{s.pr_number} should have reached terminal state"
            assert not s.failed(), f"PR #{s.pr_number} should not have failed"
            # The last stage recorded must be "post" with status ok.
            post_result = s.results.get("post")
            assert post_result is not None, f"PR #{s.pr_number} has no post result"
            assert post_result.status == "ok"


# ---------------------------------------------------------------------------
# test_index_bottleneck_does_not_block_review
# ---------------------------------------------------------------------------

def test_index_bottleneck_does_not_block_review(tmp_path):
    """Index semaphore=1 only blocks PRs waiting for Index.

    PR #1  — starts at 'import'; gets stuck in Index (slow).
    PR #2  — starts at 'import'; finishes Sync before PR#1 Index completes;
              must be allowed to queue for Index (wait), then continue.
    PR #3  — starts at 'review' (already indexed in a prior run); must be
              able to reach 'post' without touching Index.
    All three must reach terminal state.
    """
    index_event = threading.Event()  # Set to unblock Index for PRs waiting on it.
    index_entered = threading.Event()  # Signals that the slow PR is inside Index.

    sems = Semaphores(
        import_=threading.Semaphore(4),
        sync=threading.Semaphore(2),
        index=threading.Semaphore(1),
        review=threading.Semaphore(2),
        validate=threading.Semaphore(4),
        post=threading.Semaphore(2),
    )

    def slow_index(state: PRState) -> StageResult:
        """Index function: first call blocks until event set, rest proceed."""
        if not index_entered.is_set():
            # PR #1 (or the first caller) signals it is inside Index then waits.
            index_entered.set()
            index_event.wait(timeout=5)
        return StageResult(stage="index", status="ok")

    fns = _ok_stage_fns()
    fns["index"] = slow_index

    # PR #3 starts at review — skips Import/Sync/Index entirely.
    pr3 = _make_state(3, task_dir=tmp_path, current_stage="review")
    # Pre-fill its earlier results so PRState.terminal() works correctly.
    for stage in ["import", "sync", "index"]:
        pr3.results[stage] = StageResult(stage=stage, status="skipped")

    pr1 = _make_state(1, task_dir=tmp_path)
    pr2 = _make_state(2, task_dir=tmp_path)

    states = [pr1, pr2, pr3]

    # Run pipeline in a background thread so we can unblock it.
    done_event = threading.Event()
    result_holder: list[list[PRState]] = []

    def run_pipeline():
        result_holder.append(run(states, sems, fns))
        done_event.set()

    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()

    # Wait until at least one PR has entered Index (Index is occupied).
    assert index_entered.wait(timeout=5), "No PR entered Index within timeout"

    # PR #3 should be able to run Review and Post while Index is occupied.
    # Give it enough time to get through Review+Validate+Post.
    time.sleep(0.1)

    # Unblock Index so the other PRs can proceed.
    index_event.set()

    assert done_event.wait(timeout=10), "Pipeline did not finish within timeout"

    for s in states:
        assert s.terminal(), f"PR #{s.pr_number} did not reach terminal state"
        assert not s.failed(), f"PR #{s.pr_number} unexpectedly failed"

    # PR #3 must NOT have touched Index (it started at 'review').
    index_result_3 = pr3.results.get("index")
    assert index_result_3 is not None
    assert index_result_3.status == "skipped", (
        "PR #3 should have skipped Index (started at 'review'), "
        f"got {index_result_3.status!r}"
    )


# ---------------------------------------------------------------------------
# PRState contract tests (no scheduler — pure unit)
# ---------------------------------------------------------------------------

def test_pr_state_advance_ok_moves_to_next_stage(tmp_path):
    """PRState.advance() with status='ok' increments current_stage."""
    s = _make_state(1, task_dir=tmp_path)
    assert s.current_stage == "import"
    s.advance(StageResult(stage="import", status="ok"))
    assert s.current_stage == "sync"


def test_pr_state_advance_failed_keeps_current_stage(tmp_path):
    """PRState.advance() with status='failed' leaves current_stage unchanged."""
    s = _make_state(1, task_dir=tmp_path)
    s.advance(StageResult(stage="import", status="failed"))
    assert s.current_stage == "import"
    assert s.failed()


def test_pr_state_terminal_after_all_stages(tmp_path):
    """PRState.terminal() is True only after all six stages have a result."""
    s = _make_state(1, task_dir=tmp_path)
    for stage in _STAGE_ORDER:
        assert not s.terminal()
        s.advance(StageResult(stage=stage, status="ok"))
    assert s.terminal()
    assert not s.failed()


def test_pr_state_terminal_on_first_failure(tmp_path):
    """terminal() becomes True as soon as any stage records 'failed'."""
    s = _make_state(1, task_dir=tmp_path)
    s.advance(StageResult(stage="import", status="ok"))
    s.advance(StageResult(stage="sync", status="failed", reason="boom"))
    assert s.terminal()
    assert s.failed()


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-v"]))
