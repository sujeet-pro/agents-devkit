#!/usr/bin/env python3
"""walk_posting_plan.py — interactive accept/reject per posting step.

The gap this closes: `triage.py` walks NEW findings only. Existing-comment
resolutions (the `resolve` / `reopen` steps emitted by `comment_resolver.py`)
slide straight to `posting-plan.json` without any user review. In `-i` mode
that's the bulk of posting volume — see PR `event-schema-registry/#1` where
16 of 17 posting steps had zero per-item confirmation.

This script sits between `post_comments.py --use-mcp` (which writes
posting-plan.json) and the agent's MCP dispatch loop. The parent agent walks
each step here, sees the full rendered body via `--render`, and marks
accept/reject. `--finalize` emits `posting-plan-final.json` (subset).

Lifecycle (mirrors triage.py):

    walk_posting_plan.py --task-dir <d> --init --default-state {pending|accept}
      pending = interactive (walk every step)
      accept  = auto (no-op pass-through; emits final == input)

    walk_posting_plan.py --task-dir <d> --list [--filter-state ...]
    walk_posting_plan.py --task-dir <d> --render <idx>     # rich preview
    walk_posting_plan.py --task-dir <d> --mark <idx> --state accept|reject
    walk_posting_plan.py --task-dir <d> --finalize

State file: <task-dir>/pr-review/posting-walk-state.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from _common import die, get_logger, read_json, write_json, pr_review_file  # noqa: E402


VALID_STATES = ("accept", "reject", "pending")


def _plan_path(task_dir: Path) -> Path:
    return pr_review_file(task_dir, "posting-plan.json")


def _state_path(task_dir: Path) -> Path:
    return pr_review_file(task_dir, "posting-walk-state.json")


def _final_path(task_dir: Path) -> Path:
    return pr_review_file(task_dir, "posting-plan-final.json")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _step_id(idx: int) -> str:
    return f"s-{idx:03d}"


def _first_line(s: str | None, limit: int) -> str:
    """First line of `s`, truncated. Empty string when `s` is empty/None."""
    if not s:
        return ""
    head, _, _ = s.partition("\n")
    return head[:limit]


def _step_summary(step: dict) -> str:
    """One-line summary used in --list. Pulls the most distinctive field per kind."""
    kind = step.get("kind", "?")
    mcp_args = step.get("mcp_args") or {}
    if kind == "review_summary":
        body = _first_line(mcp_args.get("body"), 80)
        event = mcp_args.get("event", "")
        return f"{kind} ({event}): {body}…"
    if kind == "general_comment":
        body = _first_line(mcp_args.get("body"), 80)
        return f"{kind} ({step.get('subkind', '')}): {body}"
    if kind == "resolve":
        return f"{kind} comment={step.get('comment_id', '?')}: {step.get('reason', '')[:100]}"
    if kind == "reopen":
        return f"{kind} comment={step.get('comment_id', '?')}: {step.get('reason', '')[:100]}"
    if kind == "approve_pr":
        return f"{kind} (via {step.get('via', '?')})"
    if kind == "slack_summary":
        text = _first_line(mcp_args.get("text"), 100)
        return f"{kind}: {text}"
    if kind == "slack_summary_skipped":
        return f"{kind}: {step.get('reason', '')}"
    return f"{kind}: {json.dumps(step)[:100]}"


def cmd_init(task_dir: Path, default_state: str, log) -> dict:
    if default_state not in ("accept", "pending"):
        die("--default-state must be 'accept' (auto) or 'pending' (interactive)")
    plan_path = _plan_path(task_dir)
    if not plan_path.exists():
        die(f"no posting-plan.json under {task_dir}/pr-review — run post_comments.py --use-mcp first")
    plan = read_json(plan_path)
    steps = plan.get("steps") or []
    mode = "auto" if default_state == "accept" else "interactive"
    steps_state: dict[str, dict] = {}
    for idx, step in enumerate(steps):
        kind = step.get("kind", "?")
        # Constitution §I.4: posting is task-required by default. Even in
        # interactive mode, certain step kinds are non-walkable because
        # they're tied to other accepted steps:
        #  - approve_pr is bundled in the review_summary on GitHub; rejecting
        #    it independently means editing the review_summary's event field.
        #    We honor the user's reject by zeroing out the event downstream,
        #    but we leave it pending for explicit acknowledgement.
        steps_state[_step_id(idx)] = {
            "idx": idx,
            "kind": kind,
            "state": default_state,
        }
    state = {
        "task_dir": str(task_dir),
        "mode": mode,
        "ts": _now(),
        "n_steps": len(steps),
        "steps": steps_state,
    }
    write_json(_state_path(task_dir), state)
    log.info("init: mode=%s steps=%d default=%s", mode, len(steps), default_state)
    return {
        "mode": mode,
        "n_steps": len(steps),
        "default_state": default_state,
        "state_path": str(_state_path(task_dir)),
    }


def cmd_list(task_dir: Path, filter_state: str | None, log) -> dict:
    state = read_json(_state_path(task_dir))
    plan = read_json(_plan_path(task_dir))
    steps = plan.get("steps") or []
    out_rows: list[dict] = []
    for idx, step in enumerate(steps):
        sid = _step_id(idx)
        st = state["steps"].get(sid, {})
        if filter_state and st.get("state") != filter_state:
            continue
        out_rows.append({
            "step_id": sid,
            "idx": idx,
            "kind": step.get("kind"),
            "state": st.get("state"),
            "summary": _step_summary(step),
        })
    return {"count": len(out_rows), "rows": out_rows}


def cmd_mark(task_dir: Path, step_id: str, new_state: str, log) -> dict:
    if new_state not in VALID_STATES:
        die(f"--state must be one of {VALID_STATES}")
    state = read_json(_state_path(task_dir))
    if step_id not in state["steps"]:
        die(f"unknown step_id: {step_id}")
    state["steps"][step_id]["state"] = new_state
    state["steps"][step_id]["marked_at"] = _now()
    write_json(_state_path(task_dir), state)
    log.info("mark: %s → %s", step_id, new_state)
    return {"step_id": step_id, "state": new_state}


_CONTEXT_LINES_BEFORE = 5
_CONTEXT_LINES_AFTER = 10


def _load_pr_comments(task_dir: Path) -> dict[str, dict]:
    """Return {comment_id: comment_dict} from pr-comments.json. Empty on miss."""
    p = pr_review_file(task_dir, "pr-comments.json")
    if not p.exists():
        return {}
    try:
        blob = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, dict] = {}
    for c in blob.get("review_comments") or []:
        out[str(c.get("id"))] = c
    for c in blob.get("issue_comments") or []:
        out[str(c.get("id"))] = c
    return out


def _worktree_snippet(task_dir: Path, rel_path: str, line: int | None) -> str:
    """Read code/<rel_path> around `line`. Returns a fenced snippet or a note."""
    if not rel_path:
        return "(no file path on the original comment — cannot show worktree context)"
    if not line or line < 1:
        # Some GH comments come back with line=None and original_line=None.
        # Fall back to the file's top.
        line = 1
    fp = task_dir / "code" / rel_path
    if not fp.exists():
        return f"(file missing in worktree: `{rel_path}` — may have been deleted in the PR)"
    try:
        all_lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return f"(unreadable {rel_path}: {e})"
    n = len(all_lines)
    if n == 0:
        return f"(empty file: `{rel_path}`)"
    # If the comment's original_line is past EOF (file was shortened in the
    # diff), surface that explicitly and pin the window to the file's tail
    # so the agent can see "what's there now."
    note = ""
    anchor = line
    if line > n:
        note = (f"(note: original_line {line} is past EOF — file now has "
                f"{n} line{'s' if n != 1 else ''}; showing the file's tail.)\n\n")
        anchor = n
    lo = max(1, anchor - _CONTEXT_LINES_BEFORE)
    hi = min(n, anchor + _CONTEXT_LINES_AFTER)
    body_lines = []
    for ln in range(lo, hi + 1):
        marker = " →" if ln == anchor else "  "
        body_lines.append(f"{ln:>5}{marker} {all_lines[ln - 1]}")
    lang_hint = fp.suffix.lstrip(".") or ""
    return (f"{note}`{rel_path}` (lines {lo}-{hi}, anchor at L{anchor}):\n"
            f"```{lang_hint}\n" + "\n".join(body_lines) + "\n```")


def _existing_comment_context(task_dir: Path, comment_id: str) -> str:
    """Render the original comment + the current worktree at its anchor.
    Used by --render for resolve / reopen steps so the agent can re-check
    whether the diff actually addresses the original concern."""
    comments = _load_pr_comments(task_dir)
    c = comments.get(comment_id)
    if not c:
        return f"(comment `{comment_id}` not found in pr-comments.json)"
    user = (c.get("user") or {}).get("login", "?")
    rel = c.get("path") or ""
    line = c.get("line") or c.get("original_line") or c.get("original_position")
    body = (c.get("body") or "").strip()
    snippet = _worktree_snippet(task_dir, rel, line)
    return "\n".join([
        f"**Original comment ({user}, {rel}:{line or '?'}):**",
        "```",
        body,
        "```",
        "",
        "**Current worktree at that anchor:**",
        snippet,
    ])


def _finding_context(task_dir: Path, step: dict) -> str:
    """Render a finding's worktree context for general_comment (appreciation
    or other) steps so the agent can confirm the praised behaviour / flagged
    issue is still present in the worktree."""
    fid = step.get("finding_id")
    if not fid:
        return "(no finding_id on this general_comment — cannot show worktree context)"
    final = pr_review_file(task_dir, "findings-final.json")
    if not final.exists():
        return "(findings-final.json not yet written — run triage --finalize first)"
    try:
        blob = json.loads(final.read_text(encoding="utf-8"))
    except Exception:
        return "(could not parse findings-final.json)"
    f = next((x for x in (blob.get("findings") or []) if x.get("id") == fid), None)
    if f is None:
        return f"(finding `{fid}` not in findings-final.json — was it rejected by triage?)"
    rel = f.get("file") or ""
    ls = f.get("line_start") or 1
    le = f.get("line_end") or ls
    anchor_line = (ls + le) // 2 if le > ls else ls
    snippet = _worktree_snippet(task_dir, rel, anchor_line)
    return "\n".join([
        f"**Finding `{fid}` — {f.get('title', '')}**",
        f"Severity: `{f.get('severity', '?')}`  ·  Dimension: `{f.get('dimension', '?')}`  ·  Confidence: `{f.get('confidence', '?')}`",
        "",
        f"**Worktree at finding anchor ({rel}:{ls}-{le}):**",
        snippet,
    ])


def _render_step(step: dict, task_dir: Path | None = None) -> str:
    """Rich markdown render of one step — what would actually post.

    For resolve/reopen and general_comment steps, also includes the worktree
    context at the affected anchor so the agent can re-verify the underlying
    claim (bug 3: LLM-backed re-validation happens during this walk).
    """
    kind = step.get("kind", "?")
    transport = step.get("transport", "mcp")
    if transport == "rest":
        rest = step.get("rest") or {}
        transport_line = (f"**Transport:** REST direct — `{rest.get('method', '?')} "
                          f"{rest.get('host', '')}{rest.get('path', '')}` "
                          f"(MCP `{step.get('mcp_broken', '?')}` is broken: "
                          f"{step.get('mcp_broken_reason', 'see feedback memory')})")
    else:
        mcp_tool = step.get("mcp_tool") or "(no MCP tool — bundled)"
        transport_line = f"**MCP tool:** `{mcp_tool}`"
    lines = [
        f"### Posting step — `{kind}`",
        "",
        transport_line,
    ]
    if kind == "review_summary":
        a = step.get("mcp_args", {})
        lines += [
            f"**Target:** {a.get('owner')}/{a.get('repo')} PR #{a.get('pullNumber')}",
            f"**Event:** `{a.get('event')}`  ·  commit `{(a.get('commitID') or '')[:12]}`",
            "",
            "**Body (markdown that will post):**",
            "```markdown",
            a.get("body") or "",
            "```",
        ]
    elif kind == "general_comment":
        a = step.get("mcp_args", {})
        lines += [
            f"**Target:** {a.get('owner')}/{a.get('repo')} issue #{a.get('issue_number')}",
            f"**Subkind:** `{step.get('subkind', '?')}`  ·  finding_id: `{step.get('finding_id', '?')}`",
            "",
            "**Body (markdown that will post):**",
            "```markdown",
            a.get("body") or "",
            "```",
        ]
        if task_dir is not None and step.get("finding_id"):
            lines += [
                "",
                "**Re-validation context:**",
                _finding_context(task_dir, step),
            ]
    elif kind in ("resolve", "reopen"):
        cid = step.get("comment_id", "?")
        lines += [
            f"**Comment:** `{cid}`",
            f"**Reason:** {step.get('reason', '')}",
        ]
        if step.get("transport") == "rest":
            # Bitbucket — REST resolution toggle, no reply body.
            pass
        else:
            # GitHub — posts a textual reply.
            a = step.get("mcp_args", {})
            lines += [
                "",
                "**Reply body that will post:**",
                "```markdown",
                a.get("body") or "",
                "```",
            ]
        if task_dir is not None and cid != "?":
            heading = ("**Re-validation context — does the worktree actually address the concern?**"
                       if kind == "resolve"
                       else "**Re-validation context — is the concern actually unresolved?**")
            lines += ["", heading, _existing_comment_context(task_dir, str(cid))]
    elif kind == "approve_pr":
        if step.get("transport") == "rest":
            rest = step.get("rest") or {}
            lines += [
                f"**Action:** `{rest.get('method')} {rest.get('host', '')}{rest.get('path', '')}`",
                f"**Auth:** {rest.get('auth', '?')}",
                f"**Success codes:** {rest.get('treat_as_success', [200])}",
                "",
                "**Note:** Routed through REST because the Bitbucket MCP "
                f"`{step.get('mcp_broken', '?')}` returns 400.",
            ]
        else:
            lines += [
                f"**Bundled via:** `{step.get('via', '?')}`",
                "",
                "**Note:** " + (step.get("note") or "GitHub bundles approve in review event field"),
                "",
                "Rejecting this step demotes the review_summary event from APPROVE to COMMENT.",
            ]
    elif kind == "slack_summary":
        a = step.get("mcp_args", {})
        lines += [
            f"**Channel:** `{a.get('channel')}`  ·  thread `{a.get('thread_ts', '')}`",
            "",
            "**Slack message body:**",
            "```",
            a.get("text") or "",
            "```",
        ]
    elif kind == "slack_summary_skipped":
        lines += [
            f"**Reason:** {step.get('reason', '')}",
            "",
            "(no-op step — kept for audit trail)",
        ]
    else:
        lines += ["```json", json.dumps(step, indent=2), "```"]
    return "\n".join(lines)


def cmd_render(task_dir: Path, step_id: str, log) -> dict:
    state = read_json(_state_path(task_dir))
    plan = read_json(_plan_path(task_dir))
    steps = plan.get("steps") or []
    if step_id not in state["steps"]:
        die(f"unknown step_id: {step_id}")
    idx = state["steps"][step_id]["idx"]
    if idx >= len(steps):
        die(f"step_id {step_id} index {idx} out of range (plan has {len(steps)} steps)")
    return {
        "step_id": step_id,
        "idx": idx,
        "state": state["steps"][step_id]["state"],
        "rendered_md": _render_step(steps[idx], task_dir=task_dir),
        "raw_step": steps[idx],
    }


def cmd_finalize(task_dir: Path, log) -> dict:
    """Write posting-plan-final.json containing only `accept`ed steps.

    Special-case: if the review_summary is accepted but approve_pr is rejected,
    demote the review_summary's `event` from APPROVE to COMMENT in the final
    plan so the approve doesn't ride along.
    """
    state = read_json(_state_path(task_dir))
    plan = read_json(_plan_path(task_dir))
    steps = plan.get("steps") or []

    pending = [sid for sid, st in state["steps"].items() if st["state"] == "pending"]
    if pending:
        die(f"cannot finalize — {len(pending)} step(s) still pending: "
            f"{', '.join(pending[:5])}{'…' if len(pending) > 5 else ''}")

    accepted_indices: list[int] = []
    rejected_indices: list[int] = []
    for sid, st in state["steps"].items():
        if st["state"] == "accept":
            accepted_indices.append(st["idx"])
        elif st["state"] == "reject":
            rejected_indices.append(st["idx"])
    accepted_indices.sort()
    rejected_indices.sort()

    # Build the final plan: subset of accepted steps, preserving original order.
    final_steps: list[dict] = []
    rejected_set = set(rejected_indices)
    review_summary_idx: int | None = None
    approve_pr_idx: int | None = None
    for idx, step in enumerate(steps):
        if step.get("kind") == "review_summary":
            review_summary_idx = idx
        elif step.get("kind") == "approve_pr":
            approve_pr_idx = idx
    review_summary_accepted = (review_summary_idx is not None
                               and review_summary_idx not in rejected_set)
    approve_pr_accepted = (approve_pr_idx is not None
                           and approve_pr_idx not in rejected_set)

    # Special case: review_summary accepted + approve_pr rejected → demote event.
    demoted_event = False
    for idx in accepted_indices:
        step = json.loads(json.dumps(steps[idx]))  # deep copy
        if (step.get("kind") == "review_summary"
                and review_summary_accepted
                and approve_pr_idx is not None
                and not approve_pr_accepted):
            args = step.setdefault("mcp_args", {})
            if args.get("event") == "APPROVE":
                args["event"] = "COMMENT"
                step.setdefault("notes", []).append(
                    "event demoted APPROVE → COMMENT because approve_pr step was rejected"
                )
                demoted_event = True
        final_steps.append(step)

    out = {
        "host": plan.get("host"),
        "pr_url": plan.get("pr_url"),
        "owner": plan.get("owner"),
        "repo": plan.get("repo"),
        "pr_number": plan.get("pr_number"),
        "never_merge": plan.get("never_merge", True),
        "walk": {
            "mode": state.get("mode"),
            "accepted": len(accepted_indices),
            "rejected": len(rejected_indices),
            "demoted_event": demoted_event,
        },
        "steps": final_steps,
    }
    write_json(_final_path(task_dir), out)
    log.info("finalize: accepted=%d rejected=%d demoted_event=%s",
             len(accepted_indices), len(rejected_indices), demoted_event)
    return {
        "final_path": str(_final_path(task_dir)),
        "accepted": len(accepted_indices),
        "rejected": len(rejected_indices),
        "demoted_event": demoted_event,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    ap.add_argument("--task-dir", required=True, type=Path)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--init", action="store_true")
    g.add_argument("--finalize", action="store_true")
    g.add_argument("--list", action="store_true")
    g.add_argument("--render", help="step_id to render as rich markdown")
    g.add_argument("--mark", help="step_id to mark")
    ap.add_argument("--default-state", choices=("accept", "pending"), default="pending",
                    help="for --init")
    ap.add_argument("--state", choices=VALID_STATES, help="for --mark")
    ap.add_argument("--filter-state", choices=VALID_STATES, help="for --list")
    args = ap.parse_args()

    task_dir = args.task_dir.expanduser().resolve()
    log = get_logger("walk-posting-plan")

    if args.init:
        print(json.dumps(cmd_init(task_dir, args.default_state, log), indent=2))
        return 0
    if args.list:
        print(json.dumps(cmd_list(task_dir, args.filter_state, log), indent=2))
        return 0
    if args.render:
        print(json.dumps(cmd_render(task_dir, args.render, log), indent=2))
        return 0
    if args.mark:
        if not args.state:
            die("--mark requires --state")
        print(json.dumps(cmd_mark(task_dir, args.mark, args.state, log), indent=2))
        return 0
    if args.finalize:
        print(json.dumps(cmd_finalize(task_dir, log), indent=2))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
