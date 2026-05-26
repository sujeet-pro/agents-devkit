"""test_stage_transitions.py — verify stage transitions through the scheduler.

Tests that with stubbed stage functions:
  1. Happy path: import → sync → index → review → validate → post
  2. Fail-fast: a failing stage stops further progression
  3. Skipped stages propagate (status="skipped")
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import patch

# Ensure the lib root is on sys.path.
_LIB_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(_LIB_ROOT))

from pr_pipeline.state import PRState, StageResult  # noqa: E402
from pr_pipeline.scheduler import run, Semaphores  # noqa: E402


def _make_state(pr_url: str = "https://github.com/acme/foo/pull/1",
                tmp_path: Path | None = None) -> PRState:
    td = tmp_path or Path("/tmp/adk-test-task-dir")
    return PRState(
        pr_url=pr_url,
        repo="foo",
        pr_number=1,
        task_dir=td,
    )


def _ok_fn(stage_name: str):
    """Return a stage function that always succeeds."""
    def fn(state: PRState, **_kw) -> StageResult:
        return StageResult(stage=stage_name, status="ok", elapsed_s=0.01)  # type: ignore[arg-type]
    fn.__name__ = f"do_{stage_name}"
    return fn


def _fail_fn(stage_name: str, reason: str = "injected failure"):
    """Return a stage function that always fails."""
    def fn(state: PRState, **_kw) -> StageResult:
        return StageResult(stage=stage_name, status="failed", reason=reason)  # type: ignore[arg-type]
    fn.__name__ = f"do_{stage_name}"
    return fn


def _skip_fn(stage_name: str):
    """Return a stage function that returns skipped."""
    def fn(state: PRState, **_kw) -> StageResult:
        return StageResult(stage=stage_name, status="skipped")  # type: ignore[arg-type]
    fn.__name__ = f"do_{stage_name}"
    return fn


def _run_with_stubs(stubs: dict, *, tmp_path: Path | None = None,
                    pr_url: str = "https://github.com/acme/foo/pull/1") -> PRState:
    """Run a single PR through the scheduler with the given stage stubs."""
    state = _make_state(pr_url, tmp_path)
    q = Path("/tmp/adk-test-queue.json5")

    patch_targets = {
        f"pr_pipeline.stages.do_{s}": fn
        for s, fn in stubs.items()
    }
    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            [state],
            sems=Semaphores(import_=1, sync=1, index=1, review=1, validate=1, post=1),
            queue_path=q,
            runner_cfg={},
        )
    return results[0]


def test_happy_path_all_stages():
    """All six stages succeed → terminal, no failures, all stages in results."""
    stubs = {s: _ok_fn(s) for s in ("import", "sync", "index", "review", "validate", "post")}
    state = _run_with_stubs(stubs)

    assert state.terminal()
    assert not state.failed()
    for stage in ("import", "sync", "index", "review", "validate", "post"):
        assert stage in state.results, f"missing result for stage: {stage}"
        assert state.results[stage].status == "ok", (
            f"expected ok for {stage}, got {state.results[stage].status}"
        )


def test_fail_at_import_stops_pipeline():
    """Import failure → only import in results, all others absent."""
    stubs = {"import": _fail_fn("import")}
    for s in ("sync", "index", "review", "validate", "post"):
        stubs[s] = _ok_fn(s)

    state = _run_with_stubs(stubs)

    assert state.terminal()
    assert state.failed()
    assert "import" in state.results
    assert state.results["import"].status == "failed"
    # No downstream stages should have run.
    for stage in ("sync", "index", "review", "validate", "post"):
        assert stage not in state.results, f"stage {stage} should not have run after import fail"


def test_fail_at_index_stops_pipeline():
    """Failure at index → import + sync ok, index failed, review/validate/post not run."""
    stubs = {
        "import": _ok_fn("import"),
        "sync": _ok_fn("sync"),
        "index": _fail_fn("index", "chunker died"),
        "review": _ok_fn("review"),
        "validate": _ok_fn("validate"),
        "post": _ok_fn("post"),
    }
    state = _run_with_stubs(stubs)

    assert state.terminal()
    assert state.failed()
    assert state.results["import"].status == "ok"
    assert state.results["sync"].status == "ok"
    assert state.results["index"].status == "failed"
    assert state.results["index"].reason == "chunker died"
    for stage in ("review", "validate", "post"):
        assert stage not in state.results


def test_skipped_stage_propagates():
    """A skipped stage should propagate through the pipeline as if ok."""
    stubs = {
        "import": _ok_fn("import"),
        "sync": _skip_fn("sync"),
        "index": _ok_fn("index"),
        "review": _ok_fn("review"),
        "validate": _ok_fn("validate"),
        "post": _ok_fn("post"),
    }
    state = _run_with_stubs(stubs)

    assert state.terminal()
    assert not state.failed()
    assert state.results["sync"].status == "skipped"
    # Pipeline must continue past skipped.
    assert state.results["index"].status == "ok"
    assert state.results["post"].status == "ok"


def test_multiple_prs_independent():
    """Two PRs should both reach terminal independently."""
    stubs = {s: _ok_fn(s) for s in ("import", "sync", "index", "review", "validate", "post")}
    states = [
        PRState(pr_url="https://github.com/acme/foo/pull/1", repo="foo",
                pr_number=1, task_dir=Path("/tmp/td1")),
        PRState(pr_url="https://github.com/acme/foo/pull/2", repo="foo",
                pr_number=2, task_dir=Path("/tmp/td2")),
    ]
    q = Path("/tmp/adk-test-queue.json5")
    with patch.multiple("pr_pipeline.scheduler._stages", **{
        f"do_{s}": fn for s, fn in stubs.items()
    }):
        results = run(
            states,
            sems=Semaphores(import_=2, sync=2, index=1, review=2, validate=2, post=2),
            queue_path=q,
            runner_cfg={},
        )
    assert len(results) == 2
    for s in results:
        assert s.terminal()
        assert not s.failed()


def test_stage_result_elapsed():
    """StageResult.elapsed_s is non-negative."""
    r = StageResult(stage="import", status="ok", elapsed_s=0.05)
    assert r.elapsed_s >= 0
    assert r.stage == "import"
    assert r.status == "ok"


def test_prstate_terminal_all_ok():
    """PRState.terminal() is True when all stages have ok results."""
    from pr_pipeline.state import _STAGE_ORDER
    state = _make_state()
    for s in _STAGE_ORDER:
        state.results[s] = StageResult(stage=s, status="ok")  # type: ignore[arg-type]
    assert state.terminal()
    assert not state.failed()


def test_prstate_terminal_on_fail():
    """PRState.terminal() is True when any stage has failed."""
    state = _make_state()
    state.results["import"] = StageResult(stage="import", status="failed")
    assert state.terminal()
    assert state.failed()


def test_prstate_not_terminal_pending():
    """PRState.terminal() is False when no stages have results yet."""
    state = _make_state()
    assert not state.terminal()
