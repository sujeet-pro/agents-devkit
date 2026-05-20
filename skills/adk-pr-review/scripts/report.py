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
from _common import read_json, get_logger, die  # noqa: E402

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


SEV_ORDER = {"blocker": 0, "critical": 1, "should-have": 2, "may-have": 3, "nitpick": 4, "question": 5}
BLOCKING_SEV = {"blocker", "critical"}


def derive_recommendation(findings: list[dict], approved_host: bool = False) -> str:
    """Re-derive the post-triage recommendation from the accepted findings.

    Why: the pre-triage findings.json carries the AI reviewer's first guess.
    After triage rejects findings, the recommendation stored in that file
    can contradict the actual posted set (e.g., 'request_changes' with zero
    accepted findings). The post-triage source of truth is the count and
    severity of what survived triage.
    """
    if not findings:
        return "approve" if approved_host else "comment_only"
    if any(f.get("severity") in BLOCKING_SEV for f in findings):
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
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    pr_path = task_dir / "pr.json"
    # Prefer the post-triage source of truth so the report matches what
    # actually gets posted. Falls back to the pre-triage file for back-compat
    # with task dirs from before triage shipped.
    final_path = task_dir / "findings-final.json"
    legacy_path = task_dir / "findings.json"
    if final_path.exists():
        f_path = final_path
    elif legacy_path.exists():
        f_path = legacy_path
    else:
        die(f"missing {final_path} (preferred) and {legacy_path} (fallback)")
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
    actions_path = task_dir / "comment-actions.json"
    if actions_path.exists():
        actions = read_json(actions_path).get("actions", [])
    post_result = read_json(task_dir / "post-result.json") if (task_dir / "post-result.json").exists() else None

    # findings.md
    f_md = [
        f"# Findings — {pr.get('host')}:{pr.get('owner')}/{pr.get('repo')}#{pr.get('pr_number')}",
        f"\n[{pr.get('title')}]({pr.get('url')})\n",
        f"**Recommendation:** {findings_blob.get('recommendation','comment_only')}",
        f"\n{findings_blob.get('summary','')}\n",
        f"## Findings ({len(findings)})\n",
    ]
    for fi in findings:
        sev = fi.get("severity", "")
        cat = SEV_TO_CATEGORY.get(sev, "May-Have/Nitpicks")
        f_md.append(f"### {SEV_TAG.get(sev, '')} {fi.get('title','')}")
        f_md.append(f"`{fi.get('file','')}:{fi.get('line_start','')}-{fi.get('line_end','')}` "
                    f"· **{cat}** · dim={fi.get('dimension','')} · conf={fi.get('confidence','')}")
        f_md.append("")
        f_md.append(fi.get("body", "").rstrip())
        if fi.get("suggestion"):
            f_md.append("\n```suggestion\n" + fi["suggestion"].rstrip() + "\n```")
        if fi.get("impact_if_unfixed"):
            f_md.append(f"\n*Impact if unfixed:* {fi['impact_if_unfixed']}")
        if fi.get("evidence"):
            f_md.append("\n*Evidence:*")
            for e in fi["evidence"]:
                kind = e.get("kind", "")
                ref = e.get("ref", "")
                state = f" ({e['state']})" if e.get("state") else ""
                f_md.append(f"- {kind}: `{ref}`{state}")
        f_md.append("")
    (task_dir / "findings.md").write_text("\n".join(f_md), encoding="utf-8")

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
    rp += [
        "",
        "## Artifacts",
        f"- task dir: `{task_dir}`",
        f"- findings.json: `{task_dir / 'findings.json'}`",
        f"- findings.md: `{task_dir / 'findings.md'}`",
        f"- diff.patch: `{task_dir / 'diff.patch'}`",
        f"- code worktree: `{task_dir / 'code'}`",
        f"- code-index: `{task_dir / 'code-index'}`",
    ]
    (task_dir / "report.md").write_text("\n".join(rp), encoding="utf-8")

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

    return 0


def _release_and_print_tail(task_dir: Path, pr: dict, findings_blob: dict, log) -> None:
    """Release the queue row (if any) and print the cumulative merge-ready list.

    Idempotent: if no queue-context.json was written, we still print the tail
    so the user sees the latest state; we just skip the row update.
    """
    queue_ctx_path = task_dir / "queue-context.json"
    queue_path = DEFAULT_QUEUE_PATH
    slack_info = None
    pr_link = pr.get("url")
    if queue_ctx_path.exists():
        try:
            ctx = read_json(queue_ctx_path)
            qp = ctx.get("queue_path")
            if qp:
                queue_path = Path(qp)
            slack_info = ctx.get("slack")
            if ctx.get("pr_link"):
                pr_link = ctx["pr_link"]
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
            pr_link=pr_link,
            head_oid=pr.get("head_oid") or pr.get("headRefOid"),
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
        print(f"\nqueue: {pr_link} → {new_status}")

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
