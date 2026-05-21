#!/usr/bin/env python3
"""report.py — write findings.md + report.md + emit the CLI summary.

Reads:
  <task-dir>/pr.json
  <task-dir>/findings.json
  <task-dir>/comment-actions.json (optional)
  <task-dir>/post-result.json   (optional, if a post happened)

Writes:
  <task-dir>/findings.md
  <task-dir>/report.md

Prints the final CLI summary (PR link + 1-line per finding).

Usage:
  python3 report.py --task-dir <path>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import read_json, get_logger, die, pr_review_file  # noqa: E402

# CLI helpers (queue release + ready-to-merge tail) live under adk-cli.
ADK_CLI_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))
try:
    from queue_release import release_after_review  # noqa: E402
    from queue_io import (  # noqa: E402
        DEFAULT_QUEUE_PATH, read_queue, load_slack_config,
    )
    from pr_queue import print_summary  # noqa: E402
    _CLI_AVAILABLE = True
except Exception:
    _CLI_AVAILABLE = False


SEV_ORDER = {"blocker": 0, "critical": 1, "should-have": 2, "may-have": 3,
             "nitpick": 4, "question": 5, "appreciation": 6}
BLOCKING_SEV = {"blocker", "critical"}
APPRECIATION_SEV = "appreciation"
SEV_EMOJI = {
    "blocker": "🛑", "critical": "🛑", "should-have": "⚠️ ",
    "may-have": "💡", "nitpick": "🔹", "question": "❓",
    "appreciation": "🎉",
}


def _read_code_snippet(task_dir: Path, file_path: str,
                       line_start: int, line_end: int,
                       context_lines: int = 4) -> str | None:
    """Return a fenced markdown block with the code around a finding's line range.

    Looks under <task_dir>/code/ (the PR worktree). Returns None when the
    file is absent or the line range is out of bounds — the caller renders
    "code unavailable" in that case.
    """
    if not file_path:
        return None
    p = task_dir / "code" / file_path
    if not p.exists() or not p.is_file():
        return None
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    lines = text.splitlines()
    n_lines = len(lines)
    if n_lines == 0:
        return None
    start = max(1, (line_start or 1) - context_lines)
    end = min(n_lines, (line_end or line_start or 1) + context_lines)
    width = len(str(end))
    rendered: list[str] = []
    for i in range(start, end + 1):
        marker = "→ " if line_start <= i <= line_end else "  "
        rendered.append(f"{marker}{str(i).rjust(width)}  {lines[i - 1]}")
    # Use a language tag derived from extension so syntax highlighting kicks in
    # on viewers that render fenced blocks.
    ext = p.suffix.lstrip(".").lower()
    lang_map = {"ts": "typescript", "tsx": "tsx", "js": "javascript", "jsx": "jsx",
                "py": "python", "go": "go", "rs": "rust", "java": "java",
                "rb": "ruby", "kt": "kotlin", "swift": "swift", "cs": "csharp",
                "cpp": "cpp", "c": "c", "h": "c", "hpp": "cpp",
                "sh": "bash", "sql": "sql", "yaml": "yaml", "yml": "yaml",
                "json": "json", "toml": "toml", "md": "markdown"}
    lang = lang_map.get(ext, "")
    fence = f"```{lang}\n" + "\n".join(rendered) + "\n```"
    return fence


def render_finding_block(fi: dict, *, task_dir: Path, format_comment_body=None) -> str:
    """Render one finding as a rich markdown section.

    Sections (issue): code-context · what · why-this-matters · suggested-fix · evidence · post-preview
    Sections (appreciation): code-context · what's-nice · evidence · post-preview
    """
    sev = fi.get("severity") or "may-have"
    fid = fi.get("id") or "f-?"
    title = fi.get("title") or "(no title)"
    file_path = fi.get("file") or ""
    line_start = fi.get("line_start") or 0
    line_end = fi.get("line_end") or line_start
    dim = fi.get("dimension") or ""
    conf = fi.get("confidence") or ""
    body = (fi.get("body") or "").rstrip()
    suggestion = (fi.get("suggestion") or "").rstrip()
    impact = (fi.get("impact_if_unfixed") or "").rstrip()
    evidence = fi.get("evidence") or []
    emoji = SEV_EMOJI.get(sev, "·")

    lines: list[str] = [
        f"### {emoji} `{fid}` — {title}",
        "",
        f"`{file_path}:{line_start}-{line_end}` · **{sev}** · `{dim}` · confidence `{conf}`",
        "",
    ]

    snippet = _read_code_snippet(task_dir, file_path, int(line_start), int(line_end))
    if snippet:
        lines += ["**Code in question**", "", snippet, ""]

    if sev == APPRECIATION_SEV:
        lines += ["**What's nice about this**", "", body or "(no detail)", ""]
    else:
        lines += ["**What's happening**", "", body or "(no detail)", ""]
        if impact:
            lines += ["**Why this matters**", "", impact, ""]
        if suggestion:
            sug_block = suggestion if suggestion.startswith("```") else f"```\n{suggestion}\n```"
            lines += ["**Suggested fix**", "", sug_block, ""]

    if evidence:
        lines += ["**Evidence**"]
        for e in evidence:
            kind = e.get("kind", "")
            ref = e.get("ref", "")
            state = f" ({e['state']})" if e.get("state") else ""
            lines.append(f"- {kind}: `{ref}`{state}")
        lines.append("")

    if format_comment_body is not None:
        try:
            preview = format_comment_body(fi)
        except Exception:
            preview = None
        if preview:
            lines += [
                "<details><summary><b>What will be posted (preview)</b></summary>",
                "",
                preview,
                "",
                "</details>",
                "",
            ]
    lines.append("---\n")
    return "\n".join(lines)


def render_findings_md(*, task_dir: Path, pr: dict, findings_blob: dict,
                       appreciations: list[dict], issues: list[dict],
                       actions: list[dict]) -> str:
    """Top-level findings.md: header → appreciations → issues → existing-comment actions.

    Imports format_comment_body lazily so the report can be regenerated
    even if post_comments.py is unavailable for some reason.
    """
    try:
        from post_comments import format_comment_body  # noqa: WPS433 — lazy
    except Exception:
        format_comment_body = None

    rec_human = {
        "approve":         "Approving — looks ready to ship.",
        "request_changes": "Holding for changes — see the blocker section below.",
        "comment_only":    "Comments only — author decides.",
    }.get(findings_blob.get("recommendation"), findings_blob.get("recommendation", "—"))

    summary = (findings_blob.get("summary") or "").strip()
    head = [
        f"# {pr.get('repo')}#{pr.get('pr_number')} — review notes",
        "",
        f"**PR:** [{pr.get('title') or '(untitled)'}]({pr.get('url')})",
        f"**Author:** {(pr.get('author') or {}).get('login') or (pr.get('author') or {}).get('display_name') or '—'}",
        f"**Verdict:** {rec_human}",
        "",
    ]
    if summary:
        head += [summary, ""]

    out: list[str] = head[:]

    if appreciations:
        out += [f"## 🎉 Appreciations ({len(appreciations)})",
                "Things worth celebrating in this PR. These post as inline comments so the author sees them where the work happened.",
                ""]
        for fi in appreciations:
            out.append(render_finding_block(fi, task_dir=task_dir,
                                             format_comment_body=format_comment_body))

    if issues:
        out += [f"## Issues ({len(issues)})", ""]
        # Group by severity to give the reader a scannable structure.
        for sev in ("blocker", "critical", "should-have", "may-have", "nitpick", "question"):
            in_sev = [f for f in issues if f.get("severity") == sev]
            if not in_sev:
                continue
            label = sev.replace("-", " ")
            out += [f"### {SEV_EMOJI.get(sev, '')} {label} · {len(in_sev)}", ""]
            for fi in in_sev:
                out.append(render_finding_block(fi, task_dir=task_dir,
                                                 format_comment_body=format_comment_body))
    elif not appreciations:
        out += ["## Issues (0)",
                "No issues found. 🚀", ""]

    # Existing-comment actions section — what we proposed to do with the threads
    # that were already on the PR before this review.
    if actions:
        out += [f"## Existing comment actions ({len(actions)})", ""]
        decisions = {"resolve": "✅ Resolve", "reopen": "🔁 Reopen", "leave-as-is": "—  Leave as-is"}
        for a in actions:
            cid = a.get("comment_id", "—")
            decision = a.get("decision", "leave-as-is")
            reason = (a.get("reason") or a.get("verifier_note") or "").strip()
            valid = a.get("valid_reply") or {}
            tag = decisions.get(decision, decision)
            auto = " · auto-classified" if a.get("auto_classified") else ""
            extra = ""
            if valid.get("kind"):
                extra = f" · acceptable-reply ({valid['kind']}: {valid.get('detail') or '-'})"
            out.append(f"- `comment {cid}` · **{tag}**{auto}{extra}")
            if reason:
                out.append(f"  - reason: {reason}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def derive_recommendation(findings: list[dict], approved_host: bool = False) -> str:
    """Re-derive the post-triage recommendation from the accepted findings.

    Why: the pre-triage findings.json carries the AI reviewer's first guess.
    After triage rejects findings, the recommendation stored in that file
    can contradict the actual posted set (e.g., 'request_changes' with zero
    accepted findings). The post-triage source of truth is the count and
    severity of what survived triage.
    """
    real_issues = [f for f in findings if f.get("severity") != APPRECIATION_SEV]
    if not real_issues:
        return "approve" if approved_host else "comment_only"
    if any(f.get("severity") in BLOCKING_SEV for f in real_issues):
        return "request_changes"
    return "comment_only"
SEV_TAG = {"blocker": "[blocker]", "critical": "[critical]", "should-have": "[should]",
           "may-have": "[may]", "nitpick": "[nit]", "question": "[?]"}
SEV_TO_CATEGORY = {
    "blocker":     "Must-Have/Blocker",
    "critical":    "Must-Have/Blocker",
    "should-have": "Should-Have",
    "may-have":    "May-Have/Nitpicks",
    "nitpick":     "May-Have/Nitpicks",
    "question":    "Clarification needed",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--merge-if-approved", action="store_true",
                    help="when the review recommendation is `approve`, print "
                         "`MERGEABLE — click to merge: <pr-url>` so the human "
                         "can take the action. Constitution §I.3 forbids the "
                         "script from merging itself; this flag is purely "
                         "advisory and never calls the merge API.")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    pr_path = pr_review_file(task_dir, "pr.json")
    f_path = pr_review_file(task_dir, "findings-final.json")
    if not f_path.exists():
        die(f"missing {f_path} — run triage first.")
    if not pr_path.exists():
        die(f"missing {pr_path}")

    log = get_logger("report", task_dir)
    pr = read_json(pr_path)
    findings_blob = read_json(f_path)
    findings = sorted(findings_blob.get("findings", []),
                      key=lambda x: (SEV_ORDER.get(x.get("severity", "may-have"), 9), x.get("file", "")))
    # Re-derive recommendation from the post-triage set when reading findings-final.
    if f_path == final_path:
        review_decision = pr.get("reviewDecision") or pr.get("review_decision")
        approved_host = (review_decision == "APPROVED")
        findings_blob["recommendation"] = derive_recommendation(findings, approved_host=approved_host)
        log.info("post-triage recommendation: %s (n_findings=%d, approved_host=%s)",
                 findings_blob["recommendation"], len(findings), approved_host)
    actions = []
    actions_path = pr_review_file(task_dir, "comment-actions.json")
    if actions_path.exists():
        actions = read_json(actions_path).get("actions", [])
    post_result = read_json(pr_review_file(task_dir, "post-result.json")) if (pr_review_file(task_dir, "post-result.json")).exists() else None

    # findings.md — the rich human-facing artifact. This is what you read
    # months later when re-reading what was found on the PR. The JSON is
    # just the wire-format for triage / post / report; the user lives
    # here. (Per refactor-a Phase 7 + the user's "markdown for tracking"
    # ask.)
    appreciations = [f for f in findings if f.get("severity") == APPRECIATION_SEV]
    issues = [f for f in findings if f.get("severity") != APPRECIATION_SEV]
    f_md = render_findings_md(task_dir=task_dir, pr=pr, findings_blob=findings_blob,
                              appreciations=appreciations, issues=issues, actions=actions)
    (pr_review_file(task_dir, "findings.md")).write_text(f_md, encoding="utf-8")

    # report.md (1-pager)
    n_by_sev = {s: 0 for s in SEV_ORDER}
    for fi in findings:
        n_by_sev[fi.get("severity", "may-have")] = n_by_sev.get(fi.get("severity", "may-have"), 0) + 1
    n_resolved = sum(1 for a in actions if a.get("verified") and a.get("decision") == "resolve")
    n_reopened = sum(1 for a in actions if a.get("verified") and a.get("decision") == "reopen")
    n_left = sum(1 for a in actions if a.get("decision") == "leave-as-is")

    rp = [
        f"# adk-pr-review — {pr.get('repo')}#{pr.get('pr_number')}",
        "",
        f"**PR:** {pr.get('url')}",
        f"**Title:** {pr.get('title')}",
        f"**Recommendation:** {findings_blob.get('recommendation','comment_only')}",
        "",
        "## TL;DR",
        findings_blob.get("summary", "").strip() or "No notable findings.",
        "",
        "## Risk / Blockers / Follow-ups",
    ]
    blockers = [f for f in findings if f.get("severity") == "blocker"]
    if blockers:
        for b in blockers:
            rp.append(f"- **blocker** {b.get('title')} — `{b.get('file')}:{b.get('line_start')}`")
    else:
        rp.append("- none.")

    rp += [
        "",
        "## Findings by severity",
        f"- blocker: {n_by_sev.get('blocker',0)}",
        f"- critical: {n_by_sev.get('critical',0)}",
        f"- should-have: {n_by_sev.get('should-have',0)}",
        f"- may-have: {n_by_sev.get('may-have',0)}",
        f"- nitpick: {n_by_sev.get('nitpick',0)}",
        f"- question: {n_by_sev.get('question',0)}",
        f"- appreciation: {n_by_sev.get('appreciation',0)}",
        "",
        "## Existing comments",
        f"- resolved: {n_resolved}",
        f"- reopened: {n_reopened}",
        f"- left-as-is: {n_left}",
        "",
        "## Posting status",
    ]
    if post_result is None:
        rp.append("- not posted (plan-only or `--no-post`).")
    else:
        for p in post_result.get("posted", []):
            rp.append(f"- posted: {p}")
        for r in post_result.get("resolved", []):
            rp.append(f"- resolved: {r}")
    # Phase 6 — disposition. If the user asked --merge-if-approved AND the
    # recommendation is approve, surface a clear "click to merge" line. The
    # script never calls the merge API (constitution §I.3): the human clicks.
    mergeable_line = None
    if args.merge_if_approved and findings_blob.get("recommendation") == "approve":
        mergeable_line = f"MERGEABLE — click to merge: {pr.get('url')}"
        rp += ["", f"**{mergeable_line}**  (constitution §I.3: human must click)"]
    rp += [
        "",
        "## Artifacts",
        f"- task dir: `{task_dir}`",
        f"- findings.json: `{pr_review_file(task_dir, 'findings.json')}`",
        f"- validated-findings.json: `{pr_review_file(task_dir, 'validated-findings.json')}`",
        f"- initial-findings.json: `{pr_review_file(task_dir, 'initial-findings.json')}`",
        f"- findings.md: `{pr_review_file(task_dir, 'findings.md')}`",
        f"- diff.patch: `{pr_review_file(task_dir, 'diff.patch')}`",
        f"- code worktree: `{task_dir / 'code'}`",
        f"- code-index: `{task_dir / 'code-index'}`",
    ]
    (pr_review_file(task_dir, "report.md")).write_text("\n".join(rp), encoding="utf-8")
    if mergeable_line:
        # Also surface on stdout so the human notices in the terminal tail.
        print(mergeable_line)

    # CLI summary (PR link + 1-liner per finding).
    print(f"\nPR: {pr.get('url')}")
    print(f"Recommendation: {findings_blob.get('recommendation','comment_only')}\n")
    if not findings:
        print("No findings.")
    else:
        for fi in findings:
            tag = SEV_TAG.get(fi.get("severity", ""), "")
            line = f"{tag} {fi.get('title','')} — {fi.get('file','')}:{fi.get('line_start','')}"
            if len(line) > 110:
                line = line[:107] + "…"
            print(line)

    # Queue release + merge-ready tail (no-op if CLI module imports failed).
    if _CLI_AVAILABLE:
        _release_and_print_tail(task_dir, pr, findings_blob, log)

    # Final clickable Links block — printed LAST so it stays on screen after
    # the rest of the tail. Each URL is on its own line so terminals that
    # auto-linkify URL-only lines highlight them cleanly.
    _print_links_tail(task_dir, pr)

    return 0


def _print_links_tail(task_dir: Path, pr: dict) -> None:
    """Print the human-clickable Links block at the end of every review.

    Always shows:
      - PR URL (host-canonical form)
      - Local artifacts (findings.md + report.md + task dir) as file:// URLs
    Conditionally shows (when present):
      - Slack thread permalink (the source message the queue row was scanned from)

    The block is plain text — no ANSI colours, no markdown — so it works in
    every terminal + scrollback / log file. URLs on their own line are
    auto-linkified by iTerm2 / Terminal.app / VS Code / Cursor.
    """
    pr_url = pr.get("url") or ""
    # Pull slack info from queue-context.json — same source the queue release
    # path used.
    slack_url = None
    try:
        ctx_path = pr_review_file(task_dir, "queue-context.json")
        if ctx_path.exists():
            import json as _json
            ctx = _json.loads(ctx_path.read_text(encoding="utf-8"))
            slack_info = ctx.get("slack") or {}
            slack_url = slack_info.get("permalink") or _derive_slack_permalink(slack_info)
    except Exception:
        # Best-effort — never block the report tail on a missing slack URL.
        pass

    print()
    print("── Links " + "─" * 70)
    print(f"PR:        {pr_url}")
    if slack_url:
        print(f"Slack:     {slack_url}")
    findings_md = pr_review_file(task_dir, "findings.md")
    report_md = pr_review_file(task_dir, "report.md")
    if findings_md.exists():
        print(f"Findings:  file://{findings_md.resolve()}")
    if report_md.exists():
        print(f"Report:    file://{report_md.resolve()}")
    print(f"Task dir:  file://{task_dir.resolve()}")
    print("─" * 79)


def _derive_slack_permalink(slack_info: dict) -> str | None:
    """Reconstruct a Slack permalink from slack_info when 'permalink' isn't set.

    Falls back to the canonical Slack URL pattern:
      https://<workspace>.slack.com/archives/<channel_id>/p<ts_no_dot>
    The workspace name isn't in slack_info (only the channel_id is), so this
    returns None unless the caller's permalink is already present. This stub
    exists so the call site is uniform; future enrichment (workspace name
    lookup) can extend it.
    """
    return None


def _release_and_print_tail(task_dir: Path, pr: dict, findings_blob: dict, log) -> None:
    """Release the queue row (if any) and print the cumulative merge-ready list.

    Idempotent: if no queue-context.json was written, we still print the tail
    so the user sees the latest state; we just skip the row update.
    """
    queue_ctx_path = pr_review_file(task_dir, "queue-context.json")
    queue_path = DEFAULT_QUEUE_PATH
    slack_info = None
    pr_url = pr.get("url")
    if queue_ctx_path.exists():
        try:
            ctx = read_json(queue_ctx_path)
            qp = ctx.get("queue_path")
            if qp:
                queue_path = Path(qp)
            slack_info = ctx.get("slack")
            if ctx.get("pr_url"):
                pr_url = ctx["pr_url"]
        except Exception as e:
            log.warning("queue-context.json unreadable: %s", e)

    n_findings = len(findings_blob.get("findings", []) or [])
    recommendation = findings_blob.get("recommendation")
    review_decision = pr.get("reviewDecision") or pr.get("review_decision")
    approved_host = (review_decision == "APPROVED")

    slack_cfg = None
    if slack_info:
        try:
            slack_cfg = load_slack_config()
        except FileNotFoundError:
            slack_cfg = None
        except Exception as e:
            log.warning("could not load slack config for reaction update: %s", e)

    try:
        new_status = release_after_review(
            queue_path=queue_path,
            pr_url=pr_url,
            head_sha=pr.get("head_sha") or pr.get("headRefOid"),
            n_findings=n_findings,
            approved_host=approved_host,
            recommendation=recommendation,
            slack_cfg=slack_cfg,
            slack_info=slack_info,
            log=log,
        )
    except Exception as e:
        log.warning("queue release failed: %s", e)
        new_status = None
    if new_status is not None:
        print(f"\nqueue: {pr_url} → {new_status}")

    # Always show the cumulative merge-ready summary at the tail.
    try:
        queue = read_queue(queue_path)
        prs = queue.get("prs", []) or []
        print()
        print_summary(prs)
    except Exception as e:
        log.warning("could not load queue for ready-to-merge tail: %s", e)


if __name__ == "__main__":
    raise SystemExit(main())
