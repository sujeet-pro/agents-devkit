"""per-PR task_status derivation and progress event model.

The TUI derives a single developer-facing ``task_status`` for each queue row
at render time.  The derivation is a pure function of:

  1. The ``QueueRow`` fields already stored in the queue file.
  2. An optional list of live ``WorkerRow`` objects (from WorkersModel).
  3. An optional ``TaskStateInfo`` pre-loaded from ``state.json`` in the PR
     task dir (callers that want state.json precision pass this in; the fast
     path that only has queue data omits it).

``ProgressEvent`` is the common TUI-internal shape for inline progress
rendering.  It is emitted by helpers that translate worker heartbeats,
state.json phase records, and run_state step events into a single stream.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# Avoid a hard import of queue_io at module level; it does a sys.path dance.
# We only need the TAKEN_LOCK_MAX_AGE_SECONDS constant here.
try:
    from skills.adk_cli.scripts import queue_io as _queue_io_mod  # type: ignore
    _TAKEN_LOCK_MAX_AGE_SECONDS: int = _queue_io_mod.TAKEN_LOCK_MAX_AGE_SECONDS
except Exception:
    # Fallback: queue_io may be importable via the sys.path wiring in queue_model.
    try:
        import queue_io as _queue_io_mod  # type: ignore  # noqa: E402
        _TAKEN_LOCK_MAX_AGE_SECONDS = _queue_io_mod.TAKEN_LOCK_MAX_AGE_SECONDS
    except Exception:
        _TAKEN_LOCK_MAX_AGE_SECONDS = 2 * 60 * 60  # 2 h (queue_io default)

# Re-use the same parse helper used elsewhere in the TUI.
# We inline a copy to avoid a circular import from queue_model.
def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# TaskStatus
# ---------------------------------------------------------------------------

TaskStatus = Literal[
    # No prep has run; state is entirely unknown.
    "unknown",
    # A per-PR sync operation is scheduled (worker not yet started).
    "queued_for_sync",
    # Active worker with task_type == "sync".
    "syncing",
    # head_sha moved since the last index (state.json 3_index.head_sha_at_index).
    # Requires TaskStateInfo to distinguish from needs_re_review precisely;
    # falls back to needs_re_review when state.json is not provided.
    "queued_for_index",
    # Active prepare/index worker OR prep_status == "preparing".
    "indexing",
    # Prep done and ready_for_review; head is current; no active review.
    "ready",
    # head_sha moved since last review OR new unresolved comment activity.
    "needs_re_review",
    # Active review worker (heartbeat not stale).
    "reviewing",
    # Review complete; findings exist; triage not yet finalized/posted.
    "ready_to_act",
    # Active post worker.
    "posting",
    # Findings posted; triage finalized.
    "reviewed",
    # Reviewed + approved on host + merge-status.json bucket == "mergeable_now".
    "ready_to_merge",
    # Any phase has status == "failed" (prep_status or state.json).
    "failed",
    # taken_at set and older than TAKEN_LOCK_MAX_AGE_SECONDS (stale lock).
    "stale_lock",
    # Active merge worker.
    "merging",
    # PR merged; no Slack context or Slack skipped.
    "merged",
    # Slack update queued after merge.
    "slack_pending",
    # PR merged and Slack thread updated successfully.
    "merged_with_slack",
    # PR merged; Slack update failed — retry available.
    "merged_slack_warn",
]

# Ordered set of terminal queue statuses mapped to task_status values.
_TERMINAL_MAP: dict[str, TaskStatus] = {
    "merged": "merged",
    "closed": "unknown",  # no explicit "closed" task_status; fall through
}


# ---------------------------------------------------------------------------
# TaskStateInfo — lightweight read of state.json from the PR task dir
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PhaseRecord:
    """One phase's record from state.json (the ``phases`` mapping)."""
    name: str
    status: str                  # "ok", "failed", "running", "skipped", ""
    head_sha_at_index: str | None
    chunk_count: int | None
    chunks_embedded: int | None
    elapsed_ms: int | None
    error: str | None


@dataclass(frozen=True)
class TaskStateInfo:
    """Lightweight summary of ``state.json`` from the PR task dir.

    Callers pre-load this with ``read_task_state()`` and pass it into
    ``derive_task_status()`` when they want state.json-precision derivation.
    Omitting it falls back to queue-row-only derivation.
    """
    # Key: phase name e.g. "1_clone", "3_index".
    phases: dict[str, PhaseRecord]
    # Any phase marked "failed"?
    has_failed_phase: bool
    # head_sha recorded in 3_index phase (None if phase not present).
    last_indexed_head_sha: str | None
    # Chunk count from 3_index (for determinate progress).
    index_chunk_count: int | None
    # Has findings.json been written to the task dir?
    has_findings: bool
    # Has triage.json been finalized?
    has_finalized_triage: bool
    # Bucket from merge-status.json: mergeable_now | mergeable_with_caveats | blocked | unknown.
    merge_status_bucket: str | None = None


def read_task_state(
    pr_review_root: Path,
    repo: str,
    number: int,
) -> TaskStateInfo | None:
    """Read ``state.json`` from the PR task dir.  Returns None on any error.

    The task dir layout is ``<pr_review_root>/<repo>_pr-<number>/``.
    ``state.json`` lives at the root of that directory.
    """
    task_dir = pr_review_root / f"{repo}_pr-{number}"
    state_path = task_dir / "state.json"
    if not state_path.exists():
        return None
    try:
        raw: Any = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None

    raw_phases = raw.get("phases") or {}
    phases: dict[str, PhaseRecord] = {}
    has_failed = False
    last_indexed_sha: str | None = None
    index_chunk_count: int | None = None

    for pname, pval in raw_phases.items():
        if not isinstance(pval, dict):
            continue
        status = str(pval.get("status") or "")
        head_sha = pval.get("head_sha_at_index")
        chunk_count = pval.get("chunk_count")
        chunks_embedded = pval.get("chunks_embedded")
        elapsed_ms = pval.get("elapsed_ms")
        error = pval.get("error")
        phases[pname] = PhaseRecord(
            name=pname,
            status=status,
            head_sha_at_index=(str(head_sha) if head_sha else None),
            chunk_count=(int(chunk_count) if chunk_count is not None else None),
            chunks_embedded=(int(chunks_embedded) if chunks_embedded is not None else None),
            elapsed_ms=(int(elapsed_ms) if elapsed_ms is not None else None),
            error=(str(error) if error else None),
        )
        if status == "failed":
            has_failed = True
        # 3_index holds the indexed head sha and chunk stats.
        if "3_index" in pname or pname == "3_index":
            if head_sha:
                last_indexed_sha = str(head_sha)
            if chunk_count is not None:
                index_chunk_count = int(chunk_count)

    has_findings = (task_dir / "pr-review" / "findings.json").exists()

    # Finalized triage: posting-plan.json exists (dispatched) or
    # triage.json with a "finalized" flag.
    posting_plan = task_dir / "pr-review" / "posting-plan.json"
    triage_json = task_dir / "pr-review" / "triage.json"
    has_finalized_triage = posting_plan.exists()
    if not has_finalized_triage and triage_json.exists():
        try:
            traw: Any = json.loads(triage_json.read_text(encoding="utf-8"))
            if isinstance(traw, dict) and traw.get("finalized"):
                has_finalized_triage = True
        except (OSError, json.JSONDecodeError):
            pass

    merge_status_bucket: str | None = None
    merge_status_path = task_dir / "pr-review" / "merge-status.json"
    if merge_status_path.exists():
        try:
            mraw: Any = json.loads(merge_status_path.read_text(encoding="utf-8"))
            if isinstance(mraw, dict):
                bucket = mraw.get("bucket")
                if isinstance(bucket, str):
                    merge_status_bucket = bucket
        except (OSError, json.JSONDecodeError):
            pass

    return TaskStateInfo(
        phases=phases,
        has_failed_phase=has_failed,
        last_indexed_head_sha=last_indexed_sha,
        index_chunk_count=index_chunk_count,
        has_findings=has_findings,
        has_finalized_triage=has_finalized_triage,
        merge_status_bucket=merge_status_bucket,
    )


# ---------------------------------------------------------------------------
# derive_task_status — the core derivation function
# ---------------------------------------------------------------------------

def derive_task_status(
    row: "QueueRow",  # noqa: F821 — forward ref; avoid hard import cycle
    workers: "list[WorkerRow] | None" = None,  # noqa: F821
    *,
    task_state: TaskStateInfo | None = None,
    now: datetime | None = None,
) -> TaskStatus:
    """Derive a developer-facing ``TaskStatus`` from a queue row.

    Priority (highest to lowest):
    1. Terminal queue status (merged → check Slack variant; closed → unknown).
    2. Active non-stale worker → syncing / indexing / reviewing / posting / merging.
    3. Stale lock (taken_at expired).
    4. prep_status == "failed" OR state.json has a failed phase → failed.
    5. prep_status in {"preparing", "waiting_for_base"} → indexing.
    6. state.json head_sha changed since last index → queued_for_index.
    7. Post-review states (ready_to_act / reviewed) from state.json or queue status.
    8. needs_re_review: head moved since last review, or new comment activity.
    9. ready: prep_status == "ready" and ready_for_review.
    10. Fallthrough → unknown.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    queue_status = (row.status or "").lower()

    # ------------------------------------------------------------------
    # 1. Terminal queue status
    # ------------------------------------------------------------------
    if queue_status == "merged":
        return _merged_variant(row)
    if queue_status == "closed":
        # No separate "closed" task_status in the proposal; treat as unknown.
        return "unknown"

    # ------------------------------------------------------------------
    # 2. Active non-stale workers
    # ------------------------------------------------------------------
    if workers:
        pr_url = row.pr_url
        for w in workers:
            if w.pr_url != pr_url:
                continue
            if w.is_stale:
                continue
            tt = (w.task_type or "").lower()
            if tt == "sync":
                return "syncing"
            if tt in {"prepare", "index", "embed"}:
                return "indexing"
            if tt == "review":
                return "reviewing"
            if tt in {"post", "post_comments"}:
                return "posting"
            if tt == "merge":
                return "merging"

    # ------------------------------------------------------------------
    # 3. Stale lock
    # ------------------------------------------------------------------
    if row.taken_at:
        ts = _parse_iso(row.taken_at)
        if ts is not None and (now - ts).total_seconds() >= _TAKEN_LOCK_MAX_AGE_SECONDS:
            return "stale_lock"

    # ------------------------------------------------------------------
    # 4. Explicit failure
    # ------------------------------------------------------------------
    if row.prep_status == "failed":
        return "failed"
    if task_state is not None and task_state.has_failed_phase:
        return "failed"

    # ------------------------------------------------------------------
    # 5. Prep in progress (prep_status-driven)
    # ------------------------------------------------------------------
    if row.prep_status in {"preparing", "waiting_for_base"}:
        return "indexing"

    # ------------------------------------------------------------------
    # 6. Re-index needed (requires state.json for precision)
    # ------------------------------------------------------------------
    if task_state is not None and task_state.last_indexed_head_sha is not None:
        if row.head_sha and task_state.last_indexed_head_sha != row.head_sha:
            return "queued_for_index"

    # ------------------------------------------------------------------
    # 7. Post-review states
    # ------------------------------------------------------------------
    if task_state is not None:
        if task_state.has_finalized_triage:
            # 7a. Approved on host + merge-status confirms mergeable → promote.
            if (queue_status == "approved"
                    and task_state.merge_status_bucket == "mergeable_now"):
                return "ready_to_merge"
            return "reviewed"
        if task_state.has_findings:
            return "ready_to_act"
    # Queue-status proxy: if status is reviewed/comments/approved/reminded,
    # treat as reviewed (no task_state available).
    if queue_status in {"reviewed", "approved", "comments", "reminded"}:
        return "reviewed"

    # ------------------------------------------------------------------
    # 8. needs_re_review: head moved or new unresolved comment activity
    # ------------------------------------------------------------------
    head = row.head_sha
    last_rev = row.last_reviewed_head_sha
    if head and last_rev and head != last_rev:
        return "needs_re_review"
    # New comment activity (comment_activity_hash changed since last review).
    # QueueRow doesn't expose raw entry dicts, so comment_review_needed
    # (from queue_io) cannot be called here.  The head_sha check above
    # covers the most common needs_re_review signal.

    # ------------------------------------------------------------------
    # 9. Ready to review
    # ------------------------------------------------------------------
    if row.prep_status == "ready" and row.ready_for_review:
        return "ready"
    # prep_status == "ready" but not yet ready_for_review (e.g., taken lock)
    if row.prep_status == "ready":
        return "ready"

    # ------------------------------------------------------------------
    # 10. Unknown / no prep yet
    # ------------------------------------------------------------------
    return "unknown"


def _merged_variant(row: "QueueRow") -> TaskStatus:  # noqa: F821
    """Choose the correct merged sub-status based on Slack outcome fields.

    These fields are set by the TUI after a merge+Slack operation completes.
    They are NOT standard queue fields today; callers that add them to the
    queue row will get the richer status automatically.

    Field names (future):
      ``slack_post_status``: one of "ok", "failed", "pending", "skipped"
    """
    # Access extra fields that may not be on the frozen QueueRow dataclass.
    # Use getattr with a default so we never crash on missing fields.
    slack_post_status: str | None = getattr(row, "slack_post_status", None)
    if slack_post_status == "pending":
        return "slack_pending"
    if slack_post_status == "ok":
        return "merged_with_slack"
    if slack_post_status == "failed":
        return "merged_slack_warn"
    return "merged"


# ---------------------------------------------------------------------------
# ProgressEvent — common TUI-internal progress shape
# ---------------------------------------------------------------------------

ProgressKind = Literal[
    "op_start",       # operation began
    "step_start",     # one sub-step began (indeterminate)
    "step_progress",  # determinate: current/total known
    "step_done",      # sub-step finished (ok or error)
    "op_done",        # whole operation finished
    "op_error",       # whole operation failed
]


@dataclass
class ProgressEvent:
    """TUI-internal progress event.  All long-running operations emit these.

    ``pct`` is 0–100 for determinate steps; ``None`` drives a spinner.
    ``links`` carries optional context paths: {"log": path, "pr": url, ...}.
    """
    op_id: str
    pr_url: str
    kind: ProgressKind
    label: str
    detail: str | None = None
    pct: int | None = None
    current: int | None = None
    total: int | None = None
    elapsed_ms: int | None = None
    timestamp: str = field(default_factory=lambda: _now_iso())
    next_action: str | None = None
    error: str | None = None
    links: dict[str, str] = field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# build_progress_from_worker — maps a WorkerRow into ProgressEvent(s)
# ---------------------------------------------------------------------------

def build_progress_from_worker(
    worker: "WorkerRow",  # noqa: F821
) -> list[ProgressEvent]:
    """Translate a live ``WorkerRow`` heartbeat into ``ProgressEvent`` list.

    Produces a single ``step_start`` or ``step_progress`` event depending on
    whether chunk counts are available.  Stale workers produce no events.
    """
    if worker.is_stale:
        return []

    tt = (worker.task_type or "").lower()
    op_id = _op_id_for(tt, worker.pr_url)
    phase = worker.current_phase or ""
    label = _phase_label(tt, phase)

    # Check artifacts for chunk progress (worker may emit current/total).
    current: int | None = None
    total: int | None = None
    pct: int | None = None
    if isinstance(worker.artifacts, dict):
        c = worker.artifacts.get("chunks_embedded")
        t = worker.artifacts.get("chunk_count")
        if isinstance(c, int) and isinstance(t, int) and t > 0:
            current = c
            total = t
            pct = min(100, int(c * 100 / t))

    kind: ProgressKind = "step_progress" if pct is not None else "step_start"

    elapsed_ms: int | None = None
    if worker.age_s is not None:
        elapsed_ms = int(worker.age_s * 1000)

    log_path = worker.log_path
    links: dict[str, str] = {}
    if log_path:
        links["log"] = log_path
    if worker.pr_url:
        links["pr"] = worker.pr_url

    return [
        ProgressEvent(
            op_id=op_id,
            pr_url=worker.pr_url or "",
            kind=kind,
            label=label,
            pct=pct,
            current=current,
            total=total,
            elapsed_ms=elapsed_ms,
            links=links,
        )
    ]


def _op_id_for(task_type: str, pr_url: str) -> str:
    slug = pr_url.rstrip("/").rsplit("/", 2)
    if len(slug) >= 2:
        suffix = "-".join(slug[-2:])
    else:
        suffix = pr_url[-24:].replace("/", "-")
    return f"{task_type or 'op'}-{suffix}"


def _phase_label(task_type: str, phase: str) -> str:
    if task_type in {"prepare", "index", "embed"}:
        if phase:
            return f"indexing: {phase}"
        return "indexing"
    if task_type == "review":
        if phase:
            return f"reviewing: {phase}"
        return "reviewing"
    if task_type == "sync":
        if phase:
            return f"syncing: {phase}"
        return "syncing"
    if task_type in {"post", "post_comments"}:
        return f"posting: {phase}" if phase else "posting"
    if task_type == "merge":
        return f"merging: {phase}" if phase else "merging"
    return phase or task_type or "working"


# ---------------------------------------------------------------------------
# build_progress_from_state — synthesise events from a completed TaskStateInfo
# ---------------------------------------------------------------------------

def build_progress_from_state(
    pr_url: str,
    task_state: TaskStateInfo,
) -> list[ProgressEvent]:
    """Translate phase records in ``state.json`` into ``ProgressEvent`` list.

    Emits ``step_done`` (with ``error`` set on failed phases) for every
    phase that has a terminal status.  Useful for the Log sub-tab and
    Failure Detail Panel.
    """
    events: list[ProgressEvent] = []
    for pname, pr in sorted(task_state.phases.items()):
        if pr.status not in {"ok", "failed", "skipped"}:
            continue
        elapsed_ms = pr.elapsed_ms
        pct: int | None = None
        current: int | None = None
        total: int | None = None
        if pr.chunk_count and pr.chunks_embedded is not None:
            total = pr.chunk_count
            current = pr.chunks_embedded
            pct = min(100, int(current * 100 / total)) if total > 0 else None

        events.append(ProgressEvent(
            op_id=f"state-{pr_url}",
            pr_url=pr_url,
            kind="step_done",
            label=pname,
            detail=pr.error if pr.status == "failed" else None,
            pct=pct,
            current=current,
            total=total,
            elapsed_ms=elapsed_ms,
            error=pr.error if pr.status == "failed" else None,
        ))
    return events


# ---------------------------------------------------------------------------
# review_event_to_progress — bridge from ReviewRunner events to ProgressEvent
# ---------------------------------------------------------------------------

# Maps ReviewEventKind (review_runner.py) to ProgressKind (this module).
# Kept here rather than in review_runner to avoid a TUI-to-CLI cross-import.
# review_runner.ReviewEvent is accepted as Any; callers do not need to import
# ReviewEvent from the CLI scripts tree to use this bridge.
_REVIEW_KIND_TO_PROGRESS_KIND: dict[str, str] = {
    "started":                  "op_start",
    "phase":                    "step_start",
    "progress":                 "step_progress",
    "waiting_for_confirmation": "step_start",   # indeterminate pause
    "completed":                "op_done",
    "failed":                   "op_error",
    "warning":                  "step_done",    # non-fatal; run continues
}


def review_event_to_progress(
    event: Any,
    *,
    pr_url: str = "",
) -> ProgressEvent:
    """Convert a ``ReviewEvent`` from ``review_runner`` into a ``ProgressEvent``.

    ``event`` is typed as ``Any`` so this function can be called without a
    hard import of ``ReviewEvent`` at module level — avoiding a cross-package
    dependency between ``tui/model/`` and ``skills/adk-cli/scripts/``.

    The returned ``ProgressEvent`` is fully usable by any TUI consumer.

    Example::

        from skills.adk-cli.scripts.review_runner import ReviewEvent  # CLI side
        from tui.model.pr_status import review_event_to_progress       # TUI side

        for ev in runner.start(pr_url):
            prog = review_event_to_progress(ev, pr_url=pr_url)
            tui_dispatch(prog)
    """
    kind_str: str = getattr(event, "kind", "progress")
    progress_kind = _REVIEW_KIND_TO_PROGRESS_KIND.get(kind_str, "step_start")
    ev_links: dict[str, str] = dict(getattr(event, "links", {}) or {})
    ev_pr_url: str = ev_links.get("pr") or pr_url
    detail: str | None = getattr(event, "detail", None)
    return ProgressEvent(
        op_id=_op_id_for("review", ev_pr_url),
        pr_url=ev_pr_url,
        kind=progress_kind,  # type: ignore[arg-type]
        label=getattr(event, "label", ""),
        detail=detail,
        pct=getattr(event, "pct", None),
        elapsed_ms=getattr(event, "elapsed_ms", None),
        # Propagate detail as error text only for failure events.
        error=detail if kind_str == "failed" else None,
        links=ev_links,
    )
