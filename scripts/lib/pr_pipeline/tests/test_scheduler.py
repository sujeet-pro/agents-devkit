"""test_scheduler.py — concurrency invariants for the stage scheduler.

Verifies that with sems(index=1, sync=2):
  - At most 1 PR is running the index stage at any instant.
  - At most 2 PRs are running the sync stage at any instant.
  - All PRs reach terminal state.

Uses threading.Event to gate stub stages so we can count max concurrent.
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

_LIB_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(_LIB_ROOT))

from pr_pipeline.state import PRState, StageResult  # noqa: E402
from pr_pipeline.scheduler import run, Semaphores, RetryPolicy  # noqa: E402


class _ConcurrencyCounter:
    """Thread-safe counter that tracks the current count and the maximum seen."""

    def __init__(self):
        self._lock = threading.Lock()
        self.current = 0
        self.maximum = 0

    def enter(self):
        with self._lock:
            self.current += 1
            if self.current > self.maximum:
                self.maximum = self.current

    def exit(self):
        with self._lock:
            self.current -= 1


def _make_states(n: int) -> list[PRState]:
    return [
        PRState(
            pr_url=f"https://github.com/acme/repo/pull/{i}",
            repo="repo",
            pr_number=i,
            task_dir=Path(f"/tmp/adk-sched-test-{i}"),
        )
        for i in range(1, n + 1)
    ]


def _gating_fn(stage_name: str, counter: _ConcurrencyCounter,
               gate: threading.Barrier | None = None,
               hold_event: threading.Event | None = None,
               hold_s: float = 0.0):
    """Stage stub that tracks concurrent executions.

    If `hold_event` is set, the stub blocks until that event is set (used to
    force concurrent execution in a controlled way).  If `hold_s > 0`, the
    stub sleeps for that many seconds.  If `gate` is provided, the stub waits
    at the barrier so all instances synchronise (used for max-concurrent checks).
    """
    def fn(state: PRState, **_kw) -> StageResult:
        counter.enter()
        try:
            if gate is not None:
                try:
                    gate.wait(timeout=5.0)
                except threading.BrokenBarrierError:
                    pass
            if hold_s > 0:
                time.sleep(hold_s)
            if hold_event is not None:
                hold_event.wait(timeout=5.0)
        finally:
            counter.exit()
        return StageResult(stage=stage_name, status="ok", elapsed_s=0.01)  # type: ignore[arg-type]
    fn.__name__ = f"do_{stage_name}"
    return fn


def _instant_ok(stage_name: str):
    def fn(state: PRState, **_kw) -> StageResult:
        return StageResult(stage=stage_name, status="ok")  # type: ignore[arg-type]
    fn.__name__ = f"do_{stage_name}"
    return fn


def test_index_semaphore_limits_to_one():
    """With index=1, at most 1 PR should be in the index stage simultaneously."""
    n = 5
    index_counter = _ConcurrencyCounter()
    # Hold each index invocation briefly so overlap is visible.
    stubs = {
        "import":   _instant_ok("import"),
        "sync":     _instant_ok("sync"),
        "index":    _gating_fn("index", index_counter, hold_s=0.05),
        "review":   _instant_ok("review"),
        "validate": _instant_ok("validate"),
        "post":     _instant_ok("post"),
    }
    q = Path("/tmp/adk-test-queue.json5")
    states = _make_states(n)

    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            states,
            sems=Semaphores(import_=n, sync=n, index=1, review=n, validate=n, post=n),
            queue_path=q,
            runner_cfg={},
        )

    assert index_counter.maximum <= 1, (
        f"index semaphore violated: max concurrent was {index_counter.maximum}"
    )
    for s in results:
        assert s.terminal()
        assert not s.failed()


def test_sync_semaphore_limits_to_two():
    """With sync=2, at most 2 PRs should be in the sync stage simultaneously."""
    n = 5
    sync_counter = _ConcurrencyCounter()
    stubs = {
        "import":   _instant_ok("import"),
        "sync":     _gating_fn("sync", sync_counter, hold_s=0.05),
        "index":    _instant_ok("index"),
        "review":   _instant_ok("review"),
        "validate": _instant_ok("validate"),
        "post":     _instant_ok("post"),
    }
    q = Path("/tmp/adk-test-queue.json5")
    states = _make_states(n)

    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            states,
            sems=Semaphores(import_=n, sync=2, index=n, review=n, validate=n, post=n),
            queue_path=q,
            runner_cfg={},
        )

    assert sync_counter.maximum <= 2, (
        f"sync semaphore violated: max concurrent was {sync_counter.maximum}"
    )
    for s in results:
        assert s.terminal()
        assert not s.failed()


def test_all_prs_reach_terminal_with_mixed_sems():
    """5 PRs with varied semaphore values all reach terminal state."""
    n = 5
    stubs = {s: _instant_ok(s) for s in
             ("import", "sync", "index", "review", "validate", "post")}
    q = Path("/tmp/adk-test-queue.json5")
    states = _make_states(n)

    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            states,
            sems=Semaphores(import_=4, sync=2, index=1, review=2, validate=4, post=2),
            queue_path=q,
            runner_cfg={},
        )

    assert len(results) == n
    for s in results:
        assert s.terminal(), f"PR {s.pr_url} did not reach terminal state"
        assert not s.failed(), f"PR {s.pr_url} unexpectedly failed"


def test_empty_states_returns_empty():
    """run() with an empty list returns an empty list immediately."""
    q = Path("/tmp/adk-test-queue.json5")
    results = run([], sems=Semaphores(), queue_path=q, runner_cfg={})
    assert results == []


def test_on_event_callback_invoked():
    """The on_event callback is called for each stage start/done."""
    events: list[dict] = []
    stubs = {s: _instant_ok(s) for s in
             ("import", "sync", "index", "review", "validate", "post")}
    q = Path("/tmp/adk-test-queue.json5")
    states = _make_states(1)

    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        run(
            states,
            sems=Semaphores(import_=1, sync=1, index=1, review=1, validate=1, post=1),
            queue_path=q,
            runner_cfg={},
            on_event=events.append,
        )

    kinds = {e["kind"] for e in events}
    # At minimum we expect stage_start and stage_done events.
    assert "stage_start" in kinds or "stage_wait" in kinds, (
        f"no stage_start/stage_wait events in: {kinds}"
    )
    assert "stage_done" in kinds or "pr_done" in kinds, (
        f"no stage_done/pr_done events in: {kinds}"
    )


def test_failure_emits_fail_event():
    """A failing stage should emit a stage_fail event."""
    events: list[dict] = []

    def _fail(state: PRState, **_kw) -> StageResult:
        return StageResult(stage="import", status="failed", reason="test")

    stubs = {"import": _fail}
    for s in ("sync", "index", "review", "validate", "post"):
        stubs[s] = _instant_ok(s)

    q = Path("/tmp/adk-test-queue.json5")
    states = _make_states(1)

    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        run(
            states,
            sems=Semaphores(import_=1, sync=1, index=1, review=1, validate=1, post=1),
            queue_path=q,
            runner_cfg={},
            on_event=events.append,
        )

    fail_events = [e for e in events if e.get("kind") == "stage_fail"]
    assert fail_events, f"expected stage_fail event, got: {[e['kind'] for e in events]}"
    assert fail_events[0]["stage"] == "import"


# ---------------------------------------------------------------------------
# Retry-policy tests
# ---------------------------------------------------------------------------

def _sems_all_one() -> Semaphores:
    return Semaphores(import_=1, sync=1, index=1, review=1, validate=1, post=1)


def _run_single(stubs: dict, *, retry_policy: RetryPolicy,
                events: list | None = None) -> PRState:
    """Helper: run a single PR through the scheduler with given stubs."""
    q = Path("/tmp/adk-test-queue.json5")
    state = _make_states(1)[0]
    ev: list[dict] = [] if events is None else events
    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            [state],
            sems=_sems_all_one(),
            queue_path=q,
            runner_cfg={},
            on_event=ev.append,
            retry_policy=retry_policy,
        )
    return results[0]


def test_transient_failure_retried_once():
    """Stage fails first call with retryable reason, succeeds second call.

    With max_retries=1 the PR should reach ok and exactly one stage_retry
    event should be emitted.
    """
    call_count = {"n": 0}

    def _flaky_import(state: PRState, **_kw) -> StageResult:
        call_count["n"] += 1
        if call_count["n"] == 1:
            return StageResult(stage="import", status="failed",
                               reason="rc=137 transient")
        return StageResult(stage="import", status="ok")

    stubs = {"import": _flaky_import}
    for s in ("sync", "index", "review", "validate", "post"):
        stubs[s] = _instant_ok(s)

    events: list[dict] = []
    policy = RetryPolicy(max_retries=1, backoff_s=0.0)
    state = _run_single(stubs, retry_policy=policy, events=events)

    assert not state.failed(), "PR should succeed after retry"
    assert state.terminal()

    retry_events = [e for e in events if e["kind"] == "stage_retry"]
    assert len(retry_events) == 1, (
        f"expected exactly 1 stage_retry event, got {len(retry_events)}"
    )
    assert retry_events[0]["stage"] == "import"
    assert retry_events[0]["attempt"] == 1
    assert retry_events[0]["max_attempts"] == 2


def test_retry_budget_exhausted():
    """Stage fails every call.  max_retries=1 → 2 total attempts → terminal failed.

    Exactly one stage_retry event should be emitted (for the first retry
    attempt), and the PR should be terminal and failed after that.
    """
    def _always_fail(state: PRState, **_kw) -> StageResult:
        return StageResult(stage="import", status="failed",
                           reason="rc=1 transient connection reset")

    stubs = {"import": _always_fail}
    for s in ("sync", "index", "review", "validate", "post"):
        stubs[s] = _instant_ok(s)

    events: list[dict] = []
    policy = RetryPolicy(max_retries=1, backoff_s=0.0)
    state = _run_single(stubs, retry_policy=policy, events=events)

    assert state.failed()
    assert state.terminal()

    retry_events = [e for e in events if e["kind"] == "stage_retry"]
    assert len(retry_events) == 1, (
        f"expected exactly 1 stage_retry event, got {len(retry_events)}"
    )


def test_non_retryable_reason_no_retry():
    """A deterministic failure reason must not trigger any retry.

    Even with max_retries=2 the stage fails immediately and the PR is
    terminal failed with no stage_retry events.
    """
    def _bad_url(state: PRState, **_kw) -> StageResult:
        return StageResult(stage="import", status="failed",
                           reason="could not parse PR URL: invalid scheme")

    stubs = {"import": _bad_url}
    for s in ("sync", "index", "review", "validate", "post"):
        stubs[s] = _instant_ok(s)

    events: list[dict] = []
    policy = RetryPolicy(max_retries=2, backoff_s=0.0)
    state = _run_single(stubs, retry_policy=policy, events=events)

    assert state.failed()
    assert state.terminal()

    retry_events = [e for e in events if e["kind"] == "stage_retry"]
    assert len(retry_events) == 0, (
        f"expected no stage_retry events for non-retryable reason, got {len(retry_events)}"
    )


def test_per_stage_override():
    """max_retries=0 globally but per_stage_overrides={"import": 3}.

    Import stage retries up to 3 times; sync stage does not retry.
    """
    import_calls = {"n": 0}
    sync_calls = {"n": 0}

    def _flaky_import(state: PRState, **_kw) -> StageResult:
        import_calls["n"] += 1
        # Fail the first 3 calls, succeed on the 4th (attempt index 3).
        if import_calls["n"] <= 3:
            return StageResult(stage="import", status="failed",
                               reason="rc=1 timeout")
        return StageResult(stage="import", status="ok")

    def _fail_sync(state: PRState, **_kw) -> StageResult:
        sync_calls["n"] += 1
        return StageResult(stage="sync", status="failed", reason="rc=2 transient")

    stubs = {
        "import": _flaky_import,
        "sync": _fail_sync,
    }
    for s in ("index", "review", "validate", "post"):
        stubs[s] = _instant_ok(s)

    events: list[dict] = []
    # Global max_retries=0 means sync gets 1 attempt (no retries).
    # import override = 3 means import gets up to 4 attempts.
    policy = RetryPolicy(max_retries=0, backoff_s=0.0,
                         per_stage_overrides={"import": 3})
    state = _run_single(stubs, retry_policy=policy, events=events)

    # Import should have been called 4 times (3 failures + 1 success).
    assert import_calls["n"] == 4, (
        f"expected import called 4 times, got {import_calls['n']}"
    )
    # Sync should have been called exactly once (no retries at global max=0).
    assert sync_calls["n"] == 1, (
        f"expected sync called once, got {sync_calls['n']}"
    )

    retry_events = [e for e in events if e["kind"] == "stage_retry"]
    import_retries = [e for e in retry_events if e["stage"] == "import"]
    sync_retries = [e for e in retry_events if e["stage"] == "sync"]

    assert len(import_retries) == 3, (
        f"expected 3 import retry events, got {len(import_retries)}"
    )
    assert len(sync_retries) == 0, (
        f"expected 0 sync retry events (no retries), got {len(sync_retries)}"
    )
    # PR fails at sync (no retries allowed there).
    assert state.failed()
    assert state.terminal()
