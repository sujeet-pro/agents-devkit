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
from pr_pipeline.scheduler import run, Semaphores  # noqa: E402


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
