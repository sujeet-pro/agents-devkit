"""pr_pipeline/scheduler.py — pipelined stage-graph runner.

Each PR is a state machine (PRState). Stages run in a shared ThreadPoolExecutor;
per-stage semaphores enforce the slot limits:

  import   (default 4) — pure API calls, cheap
  sync     (default 2) — git fetch + MCP doc fetch
  index    (default 1) — the bottleneck: chunk + embed + SCIP
  review   (default 2) — LLM concurrency
  validate (default 4) — pure local
  post     (default 2) — API rate-limited

While PR-A is in Index, PR-B can be in Sync, PR-C in Review, PR-D in Post.

Usage:
  from pr_pipeline.scheduler import run, Semaphores
  from pr_pipeline.state import PRState

  states = [PRState(pr_url=..., repo=..., pr_number=..., task_dir=...)]
  final = run(states, sems=Semaphores(), queue_path=queue_path, runner_cfg={})
"""
from __future__ import annotations

import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

_LIB_DIR = Path(__file__).resolve().parent.parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from pr_pipeline.state import PRState, StageResult, StageName, _STAGE_ORDER  # noqa: E402
from pr_pipeline import stages as _stages  # noqa: E402


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Substrings that indicate a failure is worth retrying (transient/external).
_RETRYABLE_SUBSTRINGS = ("rc=", "timeout", "connection", "transient")

# Substrings that indicate a failure is deterministic — never retry.
_NON_RETRYABLE_SUBSTRINGS = (
    "lock held",
    "not in queue",
    "could not parse pr url",
    "queue row missing",
    "pr url not parsable",
)


def _is_retryable(reason: str) -> bool:
    """Return True if a stage failure reason is worth retrying.

    Deterministic errors (bad URL, missing queue row, lock contention) are
    excluded first; everything that looks like a transient subprocess or
    network failure is included.
    """
    lower = reason.lower()
    for phrase in _NON_RETRYABLE_SUBSTRINGS:
        if phrase in lower:
            return False
    for phrase in _RETRYABLE_SUBSTRINGS:
        if phrase in lower:
            return True
    return False


@dataclass
class RetryPolicy:
    """Controls how many times a failing stage is retried before giving up."""
    max_retries: int = 1   # 1 retry => up to 2 total attempts per stage
    backoff_s: float = 5.0
    per_stage_overrides: dict[str, int] = field(default_factory=dict)


@dataclass
class Semaphores:
    """Per-stage slot limits. index=1 keeps the bottleneck serialized by default."""
    import_: int = 4   # note: `import` is a Python keyword; we use import_
    sync: int = 2
    index: int = 1
    review: int = 2
    validate: int = 4
    post: int = 2


def _get_stage_fn(stage: StageName):
    """Look up the stage function at call time so tests can patch _stages.*."""
    fn_name = "do_import" if stage == "import" else f"do_{stage}"
    return getattr(_stages, fn_name)


def _make_sems(sems: Semaphores) -> dict[StageName, threading.Semaphore]:
    return {
        "import":   threading.Semaphore(max(1, sems.import_)),
        "sync":     threading.Semaphore(max(1, sems.sync)),
        "index":    threading.Semaphore(max(1, sems.index)),
        "review":   threading.Semaphore(max(1, sems.review)),
        "validate": threading.Semaphore(max(1, sems.validate)),
        "post":     threading.Semaphore(max(1, sems.post)),
    }


def _emit(on_event, kind: str, pr_url: str, stage: str,
          **extra: object) -> None:
    if on_event is None:
        return
    try:
        on_event({"kind": kind, "pr_url": pr_url, "stage": stage,
                  "ts": _now_iso(), **extra})
    except Exception:
        pass  # Event callbacks must never crash the scheduler.


def run(
    states: list[PRState],
    *,
    sems: Semaphores,
    queue_path: Path,
    runner_cfg: dict,
    on_event: Optional[Callable[[dict], None]] = None,
    retry_policy: Optional[RetryPolicy] = None,
) -> list[PRState]:
    """Run all PRState objects through the pipeline concurrently.

    Returns the list of PRState objects in their final state.  Each PRState's
    `.results` dict records every StageResult.

    Thread safety: each PRState is processed by at most one worker at a time
    (the scheduler's per-PR FSM serializes stage transitions for a single PR).
    Different PRs proceed independently within their semaphore slots.
    """
    if not states:
        return states

    _policy = retry_policy if retry_policy is not None else RetryPolicy()
    _sems = _make_sems(sems)
    # Total workers = sum of all semaphore values so no stage is deadlocked
    # waiting for pool space that a blocking stage is using.
    total_workers = (
        sems.import_ + sems.sync + sems.index +
        sems.review + sems.validate + sems.post
    )

    # Per-PR lock: prevents two futures for the same PR from running in parallel.
    pr_locks: dict[str, threading.Lock] = {s.pr_url: threading.Lock() for s in states}

    # We need a logger. Use adk_common if available, else stdlib logging.
    try:
        from adk_common import get_logger  # noqa: WPS433
        log = get_logger("pr-pipeline-scheduler")
    except Exception:
        import logging
        log = logging.getLogger("pr-pipeline-scheduler")

    pool = ThreadPoolExecutor(max_workers=max(1, total_workers))
    pending: dict[Future, PRState] = {}
    done_count = 0

    def _submit_stage(state: PRState, stage: StageName) -> None:
        """Enqueue a stage execution task into the thread pool."""
        fut = pool.submit(_run_one_stage, state, stage)
        pending[fut] = state

    def _run_one_stage(state: PRState, stage: StageName) -> PRState:
        """Acquire the stage semaphore, call the stage function, release.

        On failure, retries up to _policy.max_retries times (or the
        per_stage_overrides value for this stage) when the failure reason
        is retryable.  Sleeps _policy.backoff_s * attempt before each retry.
        """
        sem = _sems[stage]
        _emit(on_event, "stage_wait", state.pr_url, stage)
        sem.acquire()
        try:
            _emit(on_event, "stage_start", state.pr_url, stage)
            fn = _get_stage_fn(stage)
            # Build keyword args for this stage.
            kw: dict = {
                "queue_path": queue_path,
                "log": log,
            }
            # Review-stage extras from runner_cfg.
            if stage == "review":
                kw.update({
                    "runner": runner_cfg.get("runner", "claude"),
                    "agent": runner_cfg.get("agent"),
                    "model": runner_cfg.get("model"),
                    "detailed": bool(runner_cfg.get("detailed")),
                    "deep": bool(runner_cfg.get("deep")),
                    "rebuild": bool(runner_cfg.get("rebuild")),
                })
            elif stage == "index":
                kw["rebuild"] = bool(runner_cfg.get("rebuild"))
                if runner_cfg.get("embed_model"):
                    kw["embed_model"] = runner_cfg["embed_model"]
            elif stage in ("sync",):
                for flag in ("rebuild", "detailed", "deep"):
                    if runner_cfg.get(flag):
                        kw[flag] = runner_cfg[flag]
                if runner_cfg.get("embed_model"):
                    kw["embed_model"] = runner_cfg["embed_model"]

            max_for_stage = _policy.per_stage_overrides.get(stage, _policy.max_retries)
            max_attempts = max_for_stage + 1  # attempts = retries + 1

            result: StageResult = StageResult(stage=stage, status="failed", reason="")
            for attempt in range(max_attempts):
                with pr_locks[state.pr_url]:
                    result = fn(state, **kw)
                if result.status != "failed":
                    break
                # Failed — decide whether to retry.
                if attempt < max_attempts - 1 and _is_retryable(result.reason):
                    _emit(on_event, "stage_retry", state.pr_url, stage,
                          attempt=attempt + 1,
                          max_attempts=max_attempts,
                          reason=result.reason)
                    time.sleep(_policy.backoff_s * (attempt + 1))
                else:
                    # Either not retryable or budget exhausted.
                    break

            state.advance(result)
            if result.status == "failed":
                _emit(on_event, "stage_fail", state.pr_url, stage,
                      reason=result.reason)
            else:
                _emit(on_event, "stage_done", state.pr_url, stage,
                      elapsed_s=result.elapsed_s)
        finally:
            sem.release()
        return state

    # Kick off the first stage for each PR.
    for state in states:
        _submit_stage(state, "import")

    # Process completions; for each finished stage, enqueue the next.
    while pending:
        done_futures = set()
        for fut in as_completed(list(pending.keys())):
            state = pending.pop(fut, None)
            if state is None:
                continue
            done_futures.add(fut)

            try:
                fut.result()  # Raises if _run_one_stage raised unexpectedly.
            except Exception as exc:
                # Unexpected error in the worker itself — fail this PR.
                stage = state.current_stage
                result = StageResult(
                    stage=stage, status="failed",
                    reason=f"scheduler worker exception: {exc}",
                )
                state.advance(result)
                _emit(on_event, "stage_fail", state.pr_url, stage,
                      reason=result.reason)

            if state.terminal():
                done_count += 1
                status = "failed" if state.failed() else "ok"
                _emit(on_event, "pr_done", state.pr_url, state.current_stage,
                      status=status)
            else:
                # Enqueue next stage.
                _submit_stage(state, state.current_stage)

        if not done_futures:
            # as_completed already blocks; this branch should not be reached,
            # but guard against an infinite loop just in case.
            break

    pool.shutdown(wait=True)
    return states
