from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane

from tui.model.queue_model import TERMINAL_STATUSES as _TERMINAL_STATUSES

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow
    from tui.model.workers_model import WorkerRow

# Human-readable suffixes for Slack-related merged sub-states.
_SLACK_STATE_SUFFIX: dict[str, str] = {
    "slack_pending":    " (Slack queued)",
    "merged_with_slack": " (Slack notified)",
    "merged_slack_warn": " (Slack FAILED)",
}

# Prep pipeline has 6 phases (0-5); map known prep_status strings to a
# filled-block fraction for the progress bar.
_PREP_PHASE_FRACTIONS: dict[str, int] = {
    "pending":         0,
    "preparing":       3,
    "waiting_for_base": 1,
    "ready":           6,
    "failed":          0,
}
_PREP_TOTAL = 6


def _prep_progress_bar(filled: int, total: int = _PREP_TOTAL) -> str:
    filled = max(0, min(filled, total))
    return "[" + "█" * filled + "·" * (total - filled) + "]"


def _prep_line(row: "QueueRow", worker: "WorkerRow | None") -> str:
    """Single line summarising the prep-pipeline state for the detail pane."""
    status = row.prep_status
    fraction = _PREP_PHASE_FRACTIONS.get(status or "pending", 0)

    if status == "ready":
        bar = _prep_progress_bar(6)
        return f"Prep:    {bar} ready"

    if status == "failed":
        err = (row.prep_error or "unknown error")[:60]
        bar = _prep_progress_bar(0)
        return f"Prep:    {bar} FAILED — {err}"

    if status in {"preparing", "waiting_for_base"}:
        bar = _prep_progress_bar(fraction)
        phase_hint = ""
        if worker is not None and worker.current_phase:
            # Show the live phase name from the active worker, capped for width.
            phase_hint = f" ({worker.current_phase[:40]})"
        return f"Prep:    {bar} {status}{phase_hint}"

    bar = _prep_progress_bar(0)
    return f"Prep:    {bar} {status or 'not started'}"


def _staleness_line(row: "QueueRow") -> str | None:
    """Return a staleness warning line or None when the index is current."""
    if (
        row.head_sha is not None
        and row.last_reviewed_head_sha is not None
        and row.head_sha != row.last_reviewed_head_sha
    ):
        short = row.head_sha[:8]
        return f"Index:   stale — head moved to {short} (re-prepare needed)"
    return None


def _context_actions_line(row: "QueueRow", worker: "WorkerRow | None") -> str:
    """Secondary actions available via the action menu or hidden keys."""
    worker_note = " (worker active)" if worker is not None else ""
    return f"More: [enter] actions · [l] logs · [o] open{worker_note}"


def _work_line(work_text: str | None) -> str | None:
    if not work_text:
        return None
    return f"Work:    {work_text}"


def _compute_overview_text(
    row: "QueueRow | None",
    worker: "WorkerRow | None",
    *,
    work_text: str | None = None,
) -> str:
    """Return concise status + log-oriented detail for the selected PR."""
    if row is None:
        return "(no row selected)"

    head = row.head_sha or "—"
    head_short = head[:8] if head != "—" else "—"
    target = row.target_branch or "—"
    title = row.title or "(no title fetched)"
    last_reviewed = row.last_reviewed_at or "never"

    from tui.model.pr_status import derive_task_status
    task_status = derive_task_status(row, [worker] if worker is not None else None)
    task_label = task_status + _SLACK_STATE_SUFFIX.get(task_status, "")

    lines = [
        f"{row.repo}#{row.number}",
        f"Title:   {title}",
        f"Branch:  {head_short} → {target}",
        f"Status:  {row.status or 'unknown'}  ·  Task: {task_label}",
    ]

    work = _work_line(work_text)
    if work:
        lines.append(work)

    if worker is not None:
        lines.append(f"Worker:  {worker.status} · {worker.agent}")
        if worker.current_phase:
            lines.append(f"Phase:   {worker.current_phase}")
        if worker.log_path:
            lines.append(f"Log:     {worker.log_path}")
    else:
        lines.append(f"Last review: {last_reviewed}")

    lines.append(_context_actions_line(row, worker))
    return "\n".join(lines)


def _compute_log_tab_text(
    row: "QueueRow | None",
    worker: "WorkerRow | None",
) -> str:
    """Content for the Log tab: worker state summary + hint to load full log."""
    if row is None:
        return "(no row selected)\n\nPress [l] on the main screen to stream the review log."

    lines: list[str] = [f"Log  ·  {row.repo}#{row.number}"]

    if worker is not None:
        lines.append(f"Worker:  {worker.status} · {worker.agent} · {worker.task_type or '?'}")
        if worker.current_phase:
            lines.append(f"Phase:   {worker.current_phase}")
        if worker.log_path:
            lines.append(f"Path:    {worker.log_path}")
        lines.append("")
        lines.append("Press [l] to stream the last 120 lines into the activity log.")
    else:
        last_rev = row.last_reviewed_at or "never"
        lines.append(f"Last review: {last_rev}")
        lines.append("")
        lines.append("Press [l] to load the most recent review log into the activity log.")

    return "\n".join(lines)


_COMMENTS_PLACEHOLDER = (
    "Comments\n"
    "\n"
    "PR review comments and Slack thread replies will appear here\n"
    "after running:\n"
    "\n"
    "  adk pr update <pr_url>\n"
    "\n"
    "Press [u] to sync PR metadata now.\n"
    "Press [O] to open the Slack thread."
)

_REVIEW_PLACEHOLDER = (
    "Review findings\n"
    "\n"
    "Structured findings from the last adk pr-review run will appear\n"
    "here once the review index is built and the review is complete.\n"
    "\n"
    "  Prep:    press [I] to prepare (build the embedding index)\n"
    "  Review:  press [r] / [v] to start / re-run the review\n"
    "  Triage:  use `adk pr triage <pr_url>` to walk findings\n"
)


class DetailPane(Static):
    """PR detail pane — plain overview text for backward compat with unit tests.

    The *public* API is ``show(row, worker=)`` which computes and stores the
    overview text.  The ``overview_text`` property exposes the current value
    without requiring a mounted DOM (used by unit tests).

    When mounted inside a real Textual app, ``show()`` also updates the live
    ``Static`` renderable in-place so changes are visible immediately.
    """

    # Keep as Static so that the unit tests can call pane.render() or
    # pane.overview_text without a full Textual app context.  The tabbed
    # surface lives in TabbedDetailPane (see below) which wraps this widget.

    def __init__(self) -> None:
        super().__init__("(no row selected)", markup=False)
        self._overview_text: str = "(no row selected)"

    @property
    def overview_text(self) -> str:
        """The current overview content (for tests and the overview tab)."""
        return self._overview_text

    def show(self, row: "QueueRow | None", *, worker: "WorkerRow | None" = None,
             work_text: str | None = None) -> None:
        text = _compute_overview_text(row, worker, work_text=work_text)
        self._overview_text = text
        self.update(text)


class TabbedDetailPane(Widget):
    """Tabbed detail pane: Overview / Comments / Review / Log.

    This is the widget that ``app.py`` mounts.  ``DetailPane`` is its
    Overview sub-widget.  ``show()`` forwards to both the overview sub-widget
    and updates the Log tab content.
    """

    DEFAULT_CSS = """
    TabbedDetailPane {
        width: 1fr;
        height: 1fr;
        background: $surface;
    }
    TabbedDetailPane TabbedContent {
        height: 1fr;
    }
    TabbedDetailPane TabPane {
        padding: 0 1;
        height: 1fr;
    }
    TabbedDetailPane Static {
        height: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._log_text: str = _compute_log_tab_text(None, None)

    def compose(self) -> ComposeResult:
        with TabbedContent(id="detail-tabs"):
            with TabPane("Overview", id="tab-overview"):
                yield DetailPane()
            with TabPane("Comments", id="tab-comments"):
                yield Static(
                    _COMMENTS_PLACEHOLDER,
                    id="detail-comments",
                    markup=False,
                )
            with TabPane("Review", id="tab-review"):
                yield Static(
                    _REVIEW_PLACEHOLDER,
                    id="detail-review",
                    markup=False,
                )
            with TabPane("Log", id="tab-log"):
                yield Static(
                    self._log_text,
                    id="detail-log",
                    markup=False,
                )

    def show(self, row: "QueueRow | None", *, worker: "WorkerRow | None" = None,
             work_text: str | None = None) -> None:
        """Update Overview and Log tabs for the newly selected PR row."""
        try:
            self.query_one(DetailPane).show(row, worker=worker, work_text=work_text)
        except Exception:
            pass
        # Log tab.
        self._log_text = _compute_log_tab_text(row, worker)
        try:
            self.query_one("#detail-log", Static).update(self._log_text)
        except Exception:
            pass
