"""validate_findings.py — Phase 3 of /adk-pr-review.

Sits between the agent's raw `findings.json` (Phase 2 output) and the
triage step (Phase 4). For each finding, asks two cheap questions:

  1. Does the anchor still resolve?
     The cited `file:line_start..line_end` must exist in the worktree.
     If the file is gone or the line range falls outside the file's
     length, the finding refers to drifted state — drop it.

  2. Is there an identifiable, posted-worthy fix?
     A `suggestion` field that's empty, whitespace-only, or trivially
     short (`<8 chars`) means we can't tell the author what to do.
     The user's rule: "If the fix can not be identified, we will not
     have it in the finding comments." We honour that by marking the
     finding `posted: false` while keeping it in `validated-findings.json`
     for audit / future inspection.

     `question` and `appreciation` findings are exempt — they don't
     need a suggested fix, by design.

Pure validator: no LLM call, no network. The agent has already done
the hard work; this is the disciplinary gate before posting.

Outputs (written next to findings.json under <task_dir>/):
  - validated-findings.json   the full finding set with `validation` +
                              `posted` fields per finding (audit trail)
  - initial-findings.json     the subset that will be posted (alias kept
                              even when validation drops zero rows, so the
                              downstream pipeline reads from a stable name)
  - validation-report.json    counts + per-finding reasons

The triage step reads `initial-findings.json`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from _common import die, get_logger, pr_review_file  # noqa: E402


MIN_SUGGESTION_LEN = 8   # below this, "fix" is not actionable
SEVERITIES_WITHOUT_FIX = {"question", "appreciation"}


def _validate_anchor(worktree: Path, finding: dict) -> tuple[bool, str]:
    """Return (ok, reason). ok=False → drop the finding's anchor as drifted."""
    rel = finding.get("file")
    if not rel:
        return False, "no file ref"
    path = worktree / rel
    if not path.exists():
        return False, f"file missing: {rel}"
    try:
        # Cheap: count lines without loading the whole file into memory.
        with path.open("rb") as f:
            n_lines = sum(1 for _ in f)
    except OSError as e:
        return False, f"unreadable: {e}"
    ls = finding.get("line_start") or 1
    le = finding.get("line_end") or ls
    if ls < 1 or le < ls or le > n_lines:
        return False, f"line range {ls}..{le} outside file (1..{n_lines})"
    return True, "anchor ok"


def _validate_suggestion(finding: dict) -> tuple[bool, str]:
    """Return (ok, reason). ok=False → drop from posted set (kept in audit)."""
    severity = finding.get("severity")
    if severity in SEVERITIES_WITHOUT_FIX:
        return True, f"{severity}: no fix required"
    suggestion = (finding.get("suggestion") or "").strip()
    if not suggestion:
        return False, "no suggestion provided"
    if len(suggestion) < MIN_SUGGESTION_LEN:
        return False, f"suggestion too short ({len(suggestion)} chars)"
    return True, "suggestion present"


def validate_findings(task_dir: Path, *, log) -> dict:
    """Run the gate. Returns the summary dict that's also persisted to
    validation-report.json. Never raises for per-finding errors."""
    findings_path = pr_review_file(task_dir, "findings.json")
    if not findings_path.exists():
        die(f"no findings.json under {task_dir} — has the agent finished Phase 2?")
    worktree = task_dir / "code"
    if not worktree.exists():
        die(f"no worktree under {task_dir}/code — was Phase 1 (prepare) run?")

    blob = json.loads(findings_path.read_text(encoding="utf-8"))
    findings = blob.get("findings", []) or []

    validated: list[dict] = []
    posted: list[dict] = []
    dropped_anchor: list[dict] = []
    dropped_no_fix: list[dict] = []

    for f in findings:
        anchor_ok, anchor_reason = _validate_anchor(worktree, f)
        fix_ok, fix_reason = _validate_suggestion(f)
        f = dict(f)  # shallow copy; don't mutate caller's data
        f["validation"] = {
            "anchor_ok": anchor_ok,
            "anchor_reason": anchor_reason,
            "fix_ok": fix_ok,
            "fix_reason": fix_reason,
        }
        if not anchor_ok:
            f["posted"] = False
            f["validation"]["dropped_reason"] = anchor_reason
            dropped_anchor.append(f)
            validated.append(f)
            continue
        if not fix_ok:
            # Anchor's fine but we can't tell the author what to do.
            # Keep for audit; don't post.
            f["posted"] = False
            f["validation"]["dropped_reason"] = fix_reason
            dropped_no_fix.append(f)
            validated.append(f)
            continue
        f["posted"] = True
        validated.append(f)
        posted.append(f)

    # validated-findings.json: full audit trail (everything, with `posted: bool`).
    out_full = dict(blob)
    out_full["findings"] = validated
    (pr_review_file(task_dir, "validated-findings.json")).write_text(
        json.dumps(out_full, indent=2, sort_keys=True), encoding="utf-8")

    # initial-findings.json: the subset triage will walk + post.
    out_initial = dict(blob)
    out_initial["findings"] = posted
    (pr_review_file(task_dir, "initial-findings.json")).write_text(
        json.dumps(out_initial, indent=2, sort_keys=True), encoding="utf-8")

    summary = {
        "n_input": len(findings),
        "n_validated": len(validated),
        "n_posted": len(posted),
        "n_dropped_anchor": len(dropped_anchor),
        "n_dropped_no_fix": len(dropped_no_fix),
        "dropped_anchor_ids": [f.get("id") for f in dropped_anchor],
        "dropped_no_fix_ids": [f.get("id") for f in dropped_no_fix],
    }
    (pr_review_file(task_dir, "validation-report.json")).write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    log.info("validate: %d in → %d posted (%d dropped anchor, %d dropped no-fix)",
             summary["n_input"], summary["n_posted"],
             summary["n_dropped_anchor"], summary["n_dropped_no_fix"])
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="validate_findings.py",
        description="Phase 3: anchor + suggestion-presence gate on the agent's findings.",
    )
    ap.add_argument("--task-dir", required=True,
                    help="path to ~/.agents-devkit/skill-pr-review/<repo>_pr-<n>/")
    ap.add_argument("--json", action="store_true",
                    help="emit a JSON summary on stdout")
    args = ap.parse_args(argv)

    task_dir = Path(args.task_dir).expanduser().resolve()
    if not task_dir.exists():
        die(f"task dir not found: {task_dir}")
    log = get_logger("validate-findings", task_dir)
    summary = validate_findings(task_dir, log=log)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"validated {summary['n_input']} findings; "
              f"{summary['n_posted']} will be posted "
              f"({summary['n_dropped_anchor']} dropped anchor, "
              f"{summary['n_dropped_no_fix']} dropped no-fix)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
