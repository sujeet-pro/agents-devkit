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


SEV_ORDER = {"blocker": 0, "critical": 1, "should-have": 2, "may-have": 3, "nitpick": 4, "question": 5}
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
    f_path = task_dir / "findings.json"
    if not pr_path.exists():
        die(f"missing {pr_path}")
    if not f_path.exists():
        die(f"missing {f_path}")

    log = get_logger("report", task_dir)
    pr = read_json(pr_path)
    findings_blob = read_json(f_path)
    findings = sorted(findings_blob.get("findings", []),
                      key=lambda x: (SEV_ORDER.get(x.get("severity", "may-have"), 9), x.get("file", "")))
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
