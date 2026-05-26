from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Markdown, Static, TabbedContent, TabPane

from tui.model.queue_model import TERMINAL_STATUSES as _TERMINAL_STATUSES, _PR_REVIEW_ROOT
from tui.model.identity import is_ours as _is_ours
from tui.widgets.activity_pane import ActivityPane
from tui.widgets.diff_pane import DiffPane

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow
    from tui.model.workers_model import WorkerRow

CommentsFilter = Literal["open", "all"]

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
            phase_hint = f" ({worker.current_phase[:40]})"
        return f"Prep:    {bar} {status}{phase_hint}"

    bar = _prep_progress_bar(0)
    return f"Prep:    {bar} {status or 'not started'}"


def _staleness_line(row: "QueueRow") -> str | None:
    if (
        row.head_sha is not None
        and row.last_reviewed_head_sha is not None
        and row.head_sha != row.last_reviewed_head_sha
    ):
        short = row.head_sha[:8]
        return f"Index:   stale — head moved to {short} (re-prepare needed)"
    return None


def _context_actions_line(row: "QueueRow", worker: "WorkerRow | None") -> str:
    worker_note = " (worker active)" if worker is not None else ""
    return f"More: [enter] actions · [l] logs · [o] open{worker_note}"


def _work_line(work_text: str | None) -> str | None:
    if not work_text:
        return None
    return f"Work:    {work_text}"


def _findings_summary(row: "QueueRow") -> str | None:
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "findings.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    findings = data if isinstance(data, list) else (data.get("findings") or [])
    if not findings:
        return "Findings: 0"
    counts: dict[str, int] = {}
    for f in findings:
        sev = (f.get("severity") or "unknown").lower()
        counts[sev] = counts.get(sev, 0) + 1
    parts = []
    for sev in ("blocker", "critical", "should", "may", "nit"):
        if counts.get(sev):
            parts.append(f"{counts[sev]} {sev}")
    return "Findings: " + (" · ".join(parts) if parts else f"{len(findings)} unclassified")


def _read_merge_status(row: "QueueRow") -> dict | None:
    """Return the cached `adk pr merge-status` JSON, or None."""
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "merge-status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _mergeability_line(row: "QueueRow") -> str:
    """Compose the mergeability line using the cached merge-status when present.

    Three positive buckets render distinct messages:

      * ``mergeable_now``      — approved, 0 open comments, no other blockers.
      * ``mergeable_with_caveats`` — approved, **but** open comments are still
        unresolved. The reviewer hasn't blocked merge, but the operator should
        usually wait for those comments to be resolved first.
      * ``blocked``            — hard blockers (not approved, changes_requested,
        checks failing, conflicts, or PR closed).

    Falls back to a status-only heuristic if merge-status.json doesn't exist
    yet (i.e. the user hasn't pressed `m` to refresh merge state).
    """
    if row.status == "merged":
        return "Merge:   ✓ merged"
    if row.status == "closed":
        return "Merge:   ✗ closed (not merged)"

    ms = _read_merge_status(row)
    if ms is not None:
        bucket = ms.get("bucket") or "unknown"
        blockers = ms.get("blockers") or []
        caveats = ms.get("caveats") or []
        open_n = ms.get("open_comments_count") or 0
        if bucket == "mergeable_now":
            return "Merge:   ✓ mergeable now — no open comments + approved · press [M] to merge"
        if bucket == "mergeable_with_caveats":
            if open_n:
                tail = (
                    f"approved, {open_n} open comment(s) unresolved · "
                    "ideally wait, then press [M]"
                )
            elif caveats:
                tail = f"{caveats[0]} · press [M] to merge anyway"
            else:
                tail = "mergeable, but with caveats · press [M] to merge anyway"
            return f"Merge:   ⚠ {tail}"
        if bucket == "blocked":
            joined = ", ".join(str(b) for b in blockers) if blockers else "unknown reasons"
            return f"Merge:   ⛔ blocked — {joined}"
        if bucket == "unknown":
            return "Merge:   ? unknown — press [m] to refresh status"

    if row.status == "approved":
        return "Merge:   ✓ approved · press [m] for merge readiness"
    if row.status in {"reviewed", "comments"}:
        return "Merge:   ⚠ reviewed · not yet approved"
    return f"Merge:   pending · status={row.status or 'unknown'}"


def is_mergeable_now(row: "QueueRow") -> bool:
    """Whether the cached merge-status considers this PR mergeable (with or without caveats)."""
    ms = _read_merge_status(row)
    if ms is None:
        return False
    return (ms.get("bucket") or "") in {"mergeable_now", "mergeable_with_caveats"}


def _quick_actions_line(row: "QueueRow") -> str:
    is_terminal = row.status in _TERMINAL_STATUSES
    parts = ["[o]pen"]
    if not is_terminal:
        parts.append("[x] refresh")
    if row.ready_for_review and not is_terminal:
        parts.append("[r]eview")
        parts.append("[v] re-review")
    if not is_terminal:
        parts.append("[a]pprove")
        if is_mergeable_now(row):
            parts.append("[M]erge")
    return "Quick:   " + " · ".join(parts)


def _verdict_pill(row: "QueueRow", worker: "WorkerRow | None") -> str | None:
    """Return a two-line verdict summary or None when no pill applies.

    The pill is always the first content shown in the Overview so the reviewer
    knows the state without scrolling.
    """
    from tui.model.pr_status import derive_task_status
    task_status = derive_task_status(row, [worker] if worker is not None else None)

    findings = _findings_summary(row) or ""
    # Count blockers + criticals from findings.json for the pill detail line.
    blocker_n = 0
    critical_n = 0
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "findings.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else (data.get("findings") or [])
            for f in items:
                sev = (f.get("severity") or "").lower()
                if sev == "blocker":
                    blocker_n += 1
                elif sev == "critical":
                    critical_n += 1
        except (OSError, json.JSONDecodeError):
            pass

    ms = _read_merge_status(row)
    open_n = (ms.get("open_comments_count") or 0) if ms else 0

    if task_status == "ready_to_merge":
        return "**READY TO MERGE** — approved, 0 open, no blockers · press [M]"
    if task_status == "reviewed":
        if (row.status or "") == "approved":
            return "**APPROVED** — wait for comments to resolve · press [x] to refresh state"
        if blocker_n:
            return (
                f"**REQUEST CHANGES** — {blocker_n} blocker finding(s), "
                f"{critical_n} critical · press [r] to re-review"
            )
        if findings:
            return "**APPROVE READY** — only minor findings, no blockers · press [a] to approve"
    if task_status == "reviewing":
        started = row.taken_at or "?"
        return f"**REVIEWING** — agent running, started {started[:16]}"
    if task_status == "indexing":
        return "**INDEXING** — building embedding index"
    if task_status == "queued_for_index":
        return "**QUEUED FOR INDEX** — head moved since last review · press [x] to refresh"
    if task_status == "needs_re_review":
        return "**NEEDS RE-REVIEW** — head moved or new comments · press [v]"
    if task_status == "ready":
        return "**READY** — index built, no review yet · press [r] to review"
    if task_status == "failed":
        return "**FAILED** — see Activity log · press [I] to retry"
    return None


def _compute_overview_text(
    row: "QueueRow | None",
    worker: "WorkerRow | None",
    *,
    work_text: str | None = None,
) -> str:
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

    author_obj = row.author if isinstance(row.author, dict) else {}
    author_display = (
        author_obj.get("display_name")
        or author_obj.get("login")
        or author_obj.get("host_user_id")
        or "(unknown)"
    )

    pill = _verdict_pill(row, worker)
    lines = []
    if pill:
        lines.append(pill)
        lines.append("")  # blank separator before the key:value block
    lines += [
        f"{row.repo}#{row.number}",
        f"Title:   {title}",
        f"Author:  {author_display}",
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

    prep = _prep_line(row, worker)
    lines.append(prep)

    findings = _findings_summary(row)
    if findings is not None:
        lines.append(findings)

    lines.append(_mergeability_line(row))

    staleness = _staleness_line(row)
    if staleness is not None:
        lines.append(staleness)

    lines.append(_quick_actions_line(row))
    lines.append(_context_actions_line(row, worker))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Comments — unified rendering as markdown
# ---------------------------------------------------------------------------

def _read_pr_comments(row: "QueueRow") -> dict:
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "pr-comments.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _read_posting_plan(row: "QueueRow") -> dict:
    path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "posting-plan.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _short_id(raw_id) -> str:
    """Last 8 chars of a comment id, suitable for the user to reference."""
    if raw_id is None:
        return "?"
    s = str(raw_id)
    return s[-8:] if len(s) > 8 else s


def _render_diff_hunk(hunk: str | None) -> str:
    """Return a markdown ```diff fenced block, trimmed to 12 lines."""
    if not hunk:
        return ""
    lines = hunk.splitlines()
    if len(lines) > 12:
        lines = lines[-12:]  # last few lines are usually the most relevant
    cleaned = "\n".join(lines).rstrip()
    if not cleaned:
        return ""
    return f"\n  ```diff\n  {cleaned.replace(chr(10), chr(10) + '  ')}\n  ```"


def _gh_comment_to_markdown(c: dict, *, is_reply: bool = False) -> str:
    author = (c.get("user") or {}).get("login") or "(unknown)"
    ts = (c.get("created_at") or c.get("updated_at") or "")[:16]
    path = c.get("path") or ""
    line = c.get("line") or c.get("original_line") or ""
    cid = _short_id(c.get("id"))

    # Tag: inline (anchored to a file:line) vs general (PR-level).
    if path:
        tag = f"`[inline {path}:{line}]`" if line else f"`[inline {path}]`"
    else:
        tag = "`[general]`"

    body = (c.get("body") or "").strip() or "*(no body)*"
    resolved = bool(c.get("resolved") or c.get("isResolved"))
    state = "🔒 resolved" if resolved else "🔓 open"
    ours = " · **OURS**" if _is_ours(author) else ""
    header_bits = [
        tag,
        f"**@{author}**{ours}",
        ts,
        state,
        f"`id:{cid}`",
    ]
    header = " · ".join(b for b in header_bits if b)
    prefix = "  ↪ " if is_reply else "- "
    indented_body = body.replace("\n", "\n  ")
    md = f"{prefix}{header}\n\n  {indented_body}"

    # Diff hunk for inline comments — gives the reviewer the code context.
    if path:
        hunk_md = _render_diff_hunk(c.get("diff_hunk"))
        if hunk_md:
            md += hunk_md
    return md


def _bb_comment_to_markdown(c: dict, *, is_reply: bool = False) -> str:
    author_obj = c.get("author") or {}
    author = (
        author_obj.get("display_name")
        or author_obj.get("nickname")
        or "(unknown)"
    )
    ts = (c.get("created_on") or c.get("updated_on") or "")[:16]
    inline = c.get("inline") or {}
    path = inline.get("path") or ""
    line = inline.get("to") or inline.get("from") or ""
    cid = _short_id(c.get("id"))

    if path:
        tag = f"`[inline {path}:{line}]`" if line else f"`[inline {path}]`"
    else:
        tag = "`[general]`"

    body = (c.get("content", {}).get("raw") or "").strip() or "*(no body)*"
    resolution = c.get("resolution") or {}
    resolved = bool(resolution)
    state = "🔒 resolved" if resolved else "🔓 open"
    ours = " · **OURS**" if _is_ours(author_obj.get("nickname") or author) else ""
    header_bits = [
        tag,
        f"**@{author}**{ours}",
        ts,
        state,
        f"`id:{cid}`",
    ]
    header = " · ".join(b for b in header_bits if b)
    prefix = "  ↪ " if is_reply else "- "
    indented_body = body.replace("\n", "\n  ")
    md = f"{prefix}{header}\n\n  {indented_body}"

    # Bitbucket comments don't carry diff context in the API response; we
    # surface only the inline location in the tag (above).
    return md


def _group_gh_replies(comments: list[dict]) -> list[tuple[dict, list[dict]]]:
    """Group GH review_comments into (parent, [reply, reply, ...]) tuples.

    GH replies set ``in_reply_to_id`` to the root comment of the thread.
    Comments without ``in_reply_to_id`` are roots. The result preserves the
    original chronological order of the roots.
    """
    by_id = {c.get("id"): c for c in comments if c.get("id") is not None}
    roots: list[dict] = []
    replies_by_parent: dict[object, list[dict]] = {}
    for c in comments:
        parent_id = c.get("in_reply_to_id")
        if parent_id and parent_id in by_id:
            replies_by_parent.setdefault(parent_id, []).append(c)
        else:
            roots.append(c)
    grouped: list[tuple[dict, list[dict]]] = []
    for root in roots:
        rid = root.get("id")
        replies = sorted(
            replies_by_parent.get(rid, []),
            key=lambda c: c.get("created_at") or "",
        )
        grouped.append((root, replies))
    return grouped


def _group_bb_replies(comments: list[dict]) -> list[tuple[dict, list[dict]]]:
    """Bitbucket: comments may carry ``parent.id`` referencing the parent."""
    by_id = {c.get("id"): c for c in comments if c.get("id") is not None}
    roots: list[dict] = []
    replies_by_parent: dict[object, list[dict]] = {}
    for c in comments:
        parent = c.get("parent") or {}
        parent_id = parent.get("id") if isinstance(parent, dict) else None
        if parent_id and parent_id in by_id:
            replies_by_parent.setdefault(parent_id, []).append(c)
        else:
            roots.append(c)
    grouped: list[tuple[dict, list[dict]]] = []
    for root in roots:
        rid = root.get("id")
        replies = sorted(
            replies_by_parent.get(rid, []),
            key=lambda c: c.get("created_on") or "",
        )
        grouped.append((root, replies))
    return grouped


def _render_gh_thread(root: dict, replies: list[dict]) -> str:
    parts = [_gh_comment_to_markdown(root)]
    for r in replies:
        parts.append(_gh_comment_to_markdown(r, is_reply=True))
    return "\n\n".join(parts)


def _render_bb_thread(root: dict, replies: list[dict]) -> str:
    parts = [_bb_comment_to_markdown(root)]
    for r in replies:
        parts.append(_bb_comment_to_markdown(r, is_reply=True))
    return "\n\n".join(parts)


def _posting_plan_step_to_markdown(
    step: dict,
    *,
    step_index: int = 0,
    total_steps: int = 0,
) -> str | None:
    kind = step.get("kind") or "?"
    args = step.get("mcp_args") or {}
    body = (args.get("body") or "").strip()
    path = args.get("path") or ""
    line = args.get("line") or args.get("position") or ""
    loc = f"`{path}:{line}`" if path else ""
    badge = f"[{step_index}/{total_steps}]" if step_index and total_steps else ""
    state_tag = step.get("state") or ""
    state_label = f" · `{state_tag}`" if state_tag else ""

    if kind == "review_summary":
        header_bits = [badge, "**[draft · unposted]**", "review summary"]
        rendered = body[:400] + ("…" if len(body) > 400 else "") if body else "*(empty)*"
        header = " · ".join(b for b in header_bits if b)
        return f"- {header}{state_label}\n\n  {rendered}"
    if kind == "inline_comment":
        header_bits = [badge, "**[draft · unposted]**", "inline comment", loc]
        header = " · ".join(b for b in header_bits if b)
        rendered = body[:300] + ("…" if len(body) > 300 else "") if body else "*(empty)*"
        return f"- {header}{state_label}\n\n  {rendered}"
    if kind == "resolve":
        tid = args.get("comment_id") or args.get("thread_id") or ""
        return f"- {badge} **[draft · unposted]** · resolve thread {tid}{state_label}".strip(" ·")
    if kind == "reopen":
        tid = args.get("comment_id") or args.get("thread_id") or ""
        return f"- {badge} **[draft · unposted]** · reopen thread {tid}{state_label}".strip(" ·")
    if kind == "approve":
        return f"- {badge} **[draft · unposted]** · submit approval{state_label}".strip()
    return None


_COMMENTS_EMPTY_HINT = "*(no comments yet)* · press `[x]` to refresh"

# Divider rendered between comments in the unified view. The blank lines on
# either side make the markdown horizontal rule render as a visible rule.
_COMMENT_DIVIDER = "\n\n---\n\n"


def _join_comments(heading: str, rendered: list[str]) -> str:
    """Compose a section: heading + rendered comments separated by HR dividers."""
    if not rendered:
        return ""
    return heading + "\n\n" + _COMMENT_DIVIDER.join(rendered)


def _gh_thread_is_open(root: dict, replies: list[dict]) -> bool:
    """Return True if any comment in the thread is not resolved."""
    for c in [root, *replies]:
        if not (c.get("resolved") or c.get("isResolved")):
            return True
    return False


def _bb_thread_is_open(root: dict, replies: list[dict]) -> bool:
    """Return True if the root (or any reply) lacks a resolution."""
    for c in [root, *replies]:
        if not c.get("resolution"):
            return True
    return False


def _format_comments_markdown(
    row: "QueueRow",
    *,
    comments_filter: CommentsFilter = "open",
) -> str:
    """Compose a markdown document combining posted comments + unposted drafts + Slack thread.

    Comments are grouped into threads: each root comment carries a list of
    replies (rendered indented with ↪). Tags ([inline file:line] or [general])
    sit at the start of every header so the reviewer can scan the thread shape.
    Inline GitHub comments include their diff_hunk as a fenced code block.

    ``comments_filter`` controls which threads to show:
    - ``"open"``: only threads with at least one unresolved comment.
    - ``"all"``: all threads regardless of resolution state.
    Issue comments (general PR-level) are always shown — they carry no
    resolved state; drafts and Slack context are also always shown.
    """
    raw = _read_pr_comments(row)

    # GitHub shape
    review_comments = raw.get("review_comments") or []
    issue_comments = raw.get("issue_comments") or []
    # Bitbucket shape
    bb_comments = [c for c in (raw.get("comments") or []) if not c.get("deleted")]

    posted_count = len(review_comments) + len(issue_comments) + len(bb_comments)

    # Build full thread lists before filtering so posted_count is accurate.
    gh_threads_all = _group_gh_replies(review_comments) if review_comments else []
    bb_threads_all = _group_bb_replies(bb_comments) if bb_comments else []

    if comments_filter == "open":
        gh_threads = [(r, reps) for r, reps in gh_threads_all if _gh_thread_is_open(r, reps)]
        bb_threads = [(r, reps) for r, reps in bb_threads_all if _bb_thread_is_open(r, reps)]
    else:
        gh_threads = gh_threads_all
        bb_threads = bb_threads_all

    open_gh = sum(1 for r, reps in gh_threads_all if _gh_thread_is_open(r, reps))
    open_bb = sum(1 for r, reps in bb_threads_all if _bb_thread_is_open(r, reps))
    open_count = open_gh + open_bb

    posted_sections: list[str] = []
    if gh_threads:
        posted_sections.append(_join_comments(
            f"### Review comments · {len(review_comments)} "
            f"({len(gh_threads)} thread(s) shown)",
            [_render_gh_thread(root, replies) for root, replies in gh_threads],
        ))
    if issue_comments:
        # Issue (PR-level general) comments aren't threaded in GH's API.
        # Always shown: no resolved state exists for these.
        posted_sections.append(_join_comments(
            f"### Issue comments · {len(issue_comments)} `[general — always shown]`",
            [_gh_comment_to_markdown(c) for c in issue_comments],
        ))
    if bb_threads:
        posted_sections.append(_join_comments(
            f"### Comments · {len(bb_comments)} "
            f"({len(bb_threads)} thread(s) shown)",
            [_render_bb_thread(root, replies) for root, replies in bb_threads],
        ))

    # Unposted drafts from posting-plan.json — always shown regardless of filter.
    plan = _read_posting_plan(row)
    steps = plan.get("steps") or []
    total_drafts = len([s for s in steps if isinstance(s, dict)])
    rendered_drafts: list[str] = []
    step_num = 0
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_num += 1
        md = _posting_plan_step_to_markdown(step, step_index=step_num, total_steps=total_drafts)
        if md:
            rendered_drafts.append(md)
    draft_section = _join_comments(
        f"### Unposted drafts · {len(rendered_drafts)}",
        rendered_drafts,
    )

    slack_md = _format_slack_context_markdown(row)

    sections: list[str] = []
    filter_label = f"[filter: {comments_filter}]"
    header = (
        f"# Comments — `{row.repo}#{row.number}` · {posted_count} posted"
        f" ({open_count} open) · {filter_label} · press [o] to toggle"
    )
    if rendered_drafts:
        header += f" · {len(rendered_drafts)} draft(s)"
    sections.append(header)

    sections.extend(s for s in posted_sections if s)
    if draft_section:
        sections.append(draft_section)
    if slack_md:
        sections.append(slack_md)

    if not posted_sections and not draft_section and not slack_md:
        sections.append(_COMMENTS_EMPTY_HINT)

    return "\n\n".join(sections)


def _format_slack_context_markdown(row: "QueueRow") -> str:
    """Read queue-context.json and render the Slack thread block as markdown."""
    task_dir = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}"
    ctx_path = task_dir / "pr-review" / "queue-context.json"
    if not ctx_path.exists():
        return ""
    try:
        ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    lines: list[str] = ["### Slack thread"]
    slack = ctx.get("slack") or {}
    workspace = slack.get("workspace") or ""
    channel = slack.get("channel") or ""
    permalink = slack.get("permalink") or ""
    if workspace or channel:
        lines.append(f"- Workspace: `{workspace}` · Channel: `{channel}`")
    if permalink:
        lines.append(f"- Thread: [{permalink}]({permalink})")

    starter = ctx.get("thread_starter") or ctx.get("message_preview") or ""
    if starter:
        preview = starter[:200].replace("\n", " ")
        lines.append(f"- Message: {preview}")

    supporting = ctx.get("supporting_docs") or []
    if supporting:
        lines.append(f"- Docs: {len(supporting)} supporting document(s)")

    if len(lines) == 1:
        return ""
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Review — markdown rendering
# ---------------------------------------------------------------------------

def _format_review_markdown(row: "QueueRow") -> str:
    """Read findings.md verbatim; fall back to synthesised markdown from JSON."""
    task_dir = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}"
    md_path = task_dir / "pr-review" / "findings.md"
    if md_path.exists():
        try:
            text = md_path.read_text(encoding="utf-8").strip()
            if text:
                return text
        except OSError:
            pass

    json_path = task_dir / "pr-review" / "findings.json"
    if not json_path.exists():
        return ""
    try:
        findings = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    if not isinstance(findings, list):
        findings = findings.get("findings") or []

    if not findings:
        return f"# Review — `{row.repo}#{row.number}`\n\n*No findings recorded.*"

    out: list[str] = [f"# Review — `{row.repo}#{row.number}` · {len(findings)} finding(s)"]
    for f in findings:
        severity = (f.get("severity") or "?").lower()
        title = f.get("title") or f.get("id") or "(untitled)"
        path = f.get("path") or ""
        loc = f" · `{path}`" if path else ""
        out.append(f"\n## [{severity}] {title}{loc}")
        suggestion = (f.get("suggestion") or "").strip()
        if suggestion:
            out.append(f"\n{suggestion}")
    return "\n".join(out)


async def _mark_draft_step(task_dir: Path, step_id: str, state: str) -> None:
    """Shell out to walk_posting_plan.py to mark a draft step as accepted/rejected."""
    script = Path(__file__).resolve().parents[2] / "skills" / "adk-cli" / "scripts" / "walk_posting_plan.py"
    if not script.exists():
        return
    try:
        proc = await asyncio.create_subprocess_exec(
            "python3", str(script),
            "--task-dir", str(task_dir),
            "--mark", step_id,
            "--state", state,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.wait_for(proc.communicate(), timeout=10)
    except Exception:
        pass


_COMMENTS_PLACEHOLDER_MD = (
    "# Comments\n\n"
    "*(no comments yet)* · press `[x]` to refresh PR metadata + comments.\n\n"
    "Once `adk pr sync <pr_url>` has populated `pr-comments.json`, posted comments,\n"
    "unposted drafts, and the Slack thread will all appear here."
)

_REVIEW_PLACEHOLDER_MD = (
    "# Review findings\n\n"
    "Structured findings from the last `adk pr-review` run will appear here once\n"
    "the review index is built and the review is complete.\n\n"
    "- **Prep:** press `[I]` to prepare (build the embedding index)\n"
    "- **Review:** press `[r]` / `[v]` to start / re-run the review\n"
    "- **Triage:** use `adk pr triage <pr_url>` to walk findings\n"
)


# Backward-compat: tests still reference the plain placeholders.
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
    """PR detail pane — plain overview text for the Overview tab."""

    def __init__(self) -> None:
        super().__init__("(no row selected)", markup=False)
        self._overview_text: str = "(no row selected)"

    @property
    def overview_text(self) -> str:
        return self._overview_text

    def show(self, row: "QueueRow | None", *, worker: "WorkerRow | None" = None,
             work_text: str | None = None) -> None:
        text = _compute_overview_text(row, worker, work_text=work_text)
        self._overview_text = text
        self.update(text)


class CommentsTabPane(TabPane):
    """TabPane subclass for the Comments tab.

    Owns keybinds for:
      o       — toggle comments filter (open / all)
      y / d   — accept / discard the focused draft step
      e       — not yet implemented (edit draft)
      j / k   — move focus between draft steps (scroll)
    `n` is intentionally reserved for app-level next-comment-divider scroll.
    """

    BINDINGS = [
        Binding("o", "toggle_comments_filter", "Open/All", show=True),
        Binding("y", "accept_draft", "Accept draft", show=False),
        Binding("d", "reject_draft", "Discard draft", show=False),
    ]

    def __init__(self, title: str, *, id: str) -> None:
        super().__init__(title, id=id)
        # Reference to the owning TabbedDetailPane — set after mount.
        self._owner: "TabbedDetailPane | None" = None

    def action_toggle_comments_filter(self) -> None:
        if self._owner is not None:
            self._owner._toggle_comments_filter()

    def action_accept_draft(self) -> None:
        if self._owner is not None:
            self._owner._walk_focused_draft(state="accept")

    def action_reject_draft(self) -> None:
        if self._owner is not None:
            self._owner._walk_focused_draft(state="reject")


class TabbedDetailPane(Widget):
    """Tabbed detail pane: Overview / Review / Comments / Activity.

    Overview is a plain Static (fixed key:value layout).
    Review + Comments are Markdown widgets so PR/finding bodies render properly.
    Activity is a custom widget (Workers / Runs / SyncPlan / Log).
    """

    DEFAULT_CSS = """
    TabbedDetailPane { width: 1fr; height: 1fr; background: $surface; }
    TabbedDetailPane TabbedContent { height: 1fr; }
    TabbedDetailPane TabPane { padding: 0 1; height: 1fr; }
    TabbedDetailPane VerticalScroll { height: 1fr; background: $surface; }
    TabbedDetailPane Static { height: auto; }
    TabbedDetailPane Markdown { height: auto; background: $surface; }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._comments_filter: CommentsFilter = "open"
        self._current_row: "QueueRow | None" = None
        # Index of the currently focused draft step (0-based).
        self._focused_draft_idx: int = 0

    def compose(self) -> ComposeResult:
        with TabbedContent(id="detail-tabs"):
            with TabPane("Overview", id="tab-overview"):
                with VerticalScroll(id="overview-scroll"):
                    yield DetailPane()
            with TabPane("Review", id="tab-review"):
                with VerticalScroll(id="review-scroll"):
                    yield Markdown(_REVIEW_PLACEHOLDER_MD, id="detail-review")
            with CommentsTabPane("Comments", id="tab-comments"):
                with VerticalScroll(id="comments-scroll"):
                    yield Markdown(_COMMENTS_PLACEHOLDER_MD, id="detail-comments")
            with TabPane("Diff", id="tab-diff"):
                yield DiffPane(id="diff-pane")
            with TabPane("Activity", id="tab-activity"):
                yield ActivityPane()

    def on_mount(self) -> None:
        try:
            pane = self.query_one(CommentsTabPane)
            pane._owner = self
        except Exception:
            pass
        # Load persisted filter preference.
        try:
            from tui.model.prefs import load_prefs
            prefs = load_prefs()
            self._comments_filter = prefs.comments_filter
        except Exception:
            pass

    def _toggle_comments_filter(self) -> None:
        self._comments_filter = "all" if self._comments_filter == "open" else "open"
        # Persist the new preference.
        try:
            from tui.model.prefs import load_prefs, save_prefs
            prefs = load_prefs()
            import dataclasses
            save_prefs(dataclasses.replace(prefs, comments_filter=self._comments_filter))
        except Exception:
            pass
        self._refresh_comments_tab()

    def _refresh_comments_tab(self) -> None:
        if self._current_row is None:
            return
        try:
            md = _format_comments_markdown(
                self._current_row, comments_filter=self._comments_filter
            )
            self.query_one("#detail-comments", Markdown).update(md or _COMMENTS_PLACEHOLDER_MD)
        except Exception:
            pass

    def _walk_focused_draft(self, *, state: str) -> None:
        """Mark the currently focused draft step via walk_posting_plan.py."""
        row = self._current_row
        if row is None:
            return
        task_dir = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}"
        plan_path = task_dir / "pr-review" / "posting-plan.json"
        if not plan_path.exists():
            return
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        steps = [s for s in (plan.get("steps") or []) if isinstance(s, dict)]
        if not steps:
            return
        idx = max(0, min(self._focused_draft_idx, len(steps) - 1))
        step = steps[idx]
        step_id = str(step.get("id") or step.get("step_id") or idx)

        async def _run() -> None:
            await _mark_draft_step(task_dir, step_id, state)
            self._focused_draft_idx = min(idx + 1, len(steps) - 1)
            self._refresh_comments_tab()

        self.call_after_refresh(_run)

    def show(self, row: "QueueRow | None", *, worker: "WorkerRow | None" = None,
             work_text: str | None = None) -> None:
        """Update Overview, Comments, and Review tabs for the selected PR row."""
        self._current_row = row
        self._focused_draft_idx = 0

        try:
            self.query_one(DetailPane).show(row, worker=worker, work_text=work_text)
        except Exception:
            pass

        if row is not None:
            try:
                md = _format_comments_markdown(row, comments_filter=self._comments_filter)
                self.query_one("#detail-comments", Markdown).update(md or _COMMENTS_PLACEHOLDER_MD)
            except Exception:
                pass

            try:
                review_md = _format_review_markdown(row)
                self.query_one("#detail-review", Markdown).update(
                    review_md if review_md else _REVIEW_PLACEHOLDER_MD
                )
            except Exception:
                pass

            try:
                self.query_one(DiffPane).show(row)
            except Exception:
                pass

    def activity_pane(self) -> ActivityPane:
        return self.query_one(ActivityPane)

    def select_tab(self, tab_id: str) -> None:
        tabs = self.query_one("#detail-tabs", TabbedContent)
        tabs.active = tab_id


# Back-compat shim for older tests that imported these names.
def _format_comments(row: "QueueRow") -> str:  # noqa: D401 - back-compat
    """Return the unified Comments markdown for a row (back-compat shim)."""
    return _format_comments_markdown(row)


def _format_slack_context(row: "QueueRow") -> str:  # noqa: D401 - back-compat
    return _format_slack_context_markdown(row)


def _format_review(row: "QueueRow") -> str:  # noqa: D401 - back-compat
    return _format_review_markdown(row)
