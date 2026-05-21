"""Tests for `validate_findings.py` — the Phase 3 gate.

The contract:
  - Findings whose `file` doesn't exist in the worktree → dropped.
  - Findings whose `line_start..line_end` falls outside the file → dropped.
  - Findings with empty / trivially-short `suggestion` → dropped (kept in
    audit trail but `posted: false`).
  - `question` and `appreciation` severities are exempt from the suggestion
    check (they're inherently fix-less).
  - Anchor failure trumps suggestion failure (one drop reason, not both).

Output artifacts:
  - validated-findings.json   audit trail (every finding, with `posted` flag)
  - initial-findings.json     posted subset (downstream pipeline reads this)
  - validation-report.json    counts + per-row reasons
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# This file lives at skills/adk-pr-review/scripts/tests/.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_findings as vf


def _mk_task_dir(tmp_path: Path, findings: list[dict],
                 worktree_files: dict[str, str]) -> Path:
    task_dir = tmp_path / "task"
    (task_dir / "code").mkdir(parents=True, exist_ok=True)
    for rel, content in worktree_files.items():
        p = task_dir / "code" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    findings_path = task_dir / "pr-review" / "findings.json"
    findings_path.parent.mkdir(parents=True, exist_ok=True)
    findings_path.write_text(
        json.dumps({
            "findings": findings,
            "existing_comment_actions": [],
            "recommendation": "comment_only",
            "summary": "test fixture",
            "finding_set_hash": "0" * 64,
        }), encoding="utf-8")
    return task_dir


def _finding(**overrides) -> dict:
    base = {
        "id": "f-001",
        "title": "stub",
        "dimension": "correctness",
        "severity": "should-have",
        "confidence": "high",
        "file": "src/main.ts",
        "line_start": 2,
        "line_end": 3,
        "body": "stub body",
        "suggestion": "Use a real fix here, please.",
        "evidence": [{"kind": "diff", "ref": "src/main.ts:2-3"}],
    }
    base.update(overrides)
    return base


def _log():
    from _common import get_logger
    return get_logger("test")


# ----- happy path -----

def test_eligible_finding_keeps_anchor_and_fix(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding()],
        {"src/main.ts": "line1\nline2\nline3\nline4\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_input"] == 1
    assert summary["n_posted"] == 1
    assert summary["n_dropped_anchor"] == 0
    assert summary["n_dropped_no_fix"] == 0
    initial = json.loads((task / "pr-review" / "initial-findings.json").read_text())
    assert len(initial["findings"]) == 1
    assert initial["findings"][0]["posted"] is True


# ----- anchor checks -----

def test_missing_file_drops_finding(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(file="src/does_not_exist.ts")],
        {"src/main.ts": "line1\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_posted"] == 0
    assert summary["n_dropped_anchor"] == 1
    audit = json.loads((task / "pr-review" / "validated-findings.json").read_text())["findings"]
    assert audit[0]["validation"]["anchor_ok"] is False
    assert "file missing" in audit[0]["validation"]["anchor_reason"]


def test_line_range_outside_file_drops_finding(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(line_start=50, line_end=60)],
        {"src/main.ts": "line1\nline2\n"},  # only 2 lines
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_dropped_anchor"] == 1
    assert summary["n_posted"] == 0


def test_empty_file_treated_as_drift(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(line_start=1, line_end=1)],
        {"src/main.ts": ""},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_dropped_anchor"] == 1


# ----- suggestion checks -----

def test_missing_suggestion_drops_from_posted(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(suggestion="")],
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_input"] == 1
    assert summary["n_posted"] == 0
    assert summary["n_dropped_no_fix"] == 1
    # Kept in the audit trail with posted=False.
    audit = json.loads((task / "pr-review" / "validated-findings.json").read_text())["findings"]
    assert len(audit) == 1
    assert audit[0]["posted"] is False
    assert audit[0]["validation"]["fix_ok"] is False


def test_trivial_suggestion_drops_from_posted(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(suggestion="fix it")],   # 6 chars, below MIN_SUGGESTION_LEN
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_dropped_no_fix"] == 1


def test_question_severity_exempt_from_suggestion_check(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(severity="question", suggestion="")],
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    # Questions don't need a fix; they're allowed through.
    assert summary["n_posted"] == 1


def test_appreciation_severity_exempt_from_suggestion_check(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [_finding(severity="appreciation", suggestion="")],
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_posted"] == 1


# ----- multi-finding mix -----

def test_mixed_set_reports_correct_counts(tmp_path):
    task = _mk_task_dir(
        tmp_path,
        [
            _finding(id="f-001"),                                    # ok
            _finding(id="f-002", file="gone.ts"),                    # anchor drift
            _finding(id="f-003", suggestion=""),                     # no fix
            _finding(id="f-004", severity="question", suggestion=""), # exempt
        ],
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    summary = vf.validate_findings(task, log=_log())
    assert summary["n_input"] == 4
    assert summary["n_posted"] == 2
    assert summary["n_dropped_anchor"] == 1
    assert summary["n_dropped_no_fix"] == 1
    assert summary["dropped_anchor_ids"] == ["f-002"]
    assert summary["dropped_no_fix_ids"] == ["f-003"]


# ----- artifact integrity -----

def test_initial_and_validated_diverge_on_drops(tmp_path):
    """validated-findings.json keeps every input (audit); initial-findings.json
    only contains rows with posted=True. Triage reads the latter."""
    task = _mk_task_dir(
        tmp_path,
        [_finding(id="f-001"), _finding(id="f-002", file="gone.ts")],
        {"src/main.ts": "a\nb\nc\nd\n"},
    )
    vf.validate_findings(task, log=_log())
    validated = json.loads((task / "pr-review" / "validated-findings.json").read_text())["findings"]
    initial = json.loads((task / "pr-review" / "initial-findings.json").read_text())["findings"]
    assert len(validated) == 2
    assert len(initial) == 1
    assert initial[0]["id"] == "f-001"


def test_missing_findings_json_exits_clean(tmp_path):
    task_dir = tmp_path / "task"
    (task_dir / "code").mkdir(parents=True)
    # No findings.json written.
    with pytest.raises(SystemExit):
        vf.validate_findings(task_dir, log=_log())


def test_missing_worktree_exits_clean(tmp_path):
    task_dir = tmp_path / "task"
    findings_path = task_dir / "pr-review" / "findings.json"
    findings_path.parent.mkdir(parents=True)
    findings_path.write_text(json.dumps({
        "findings": [], "existing_comment_actions": [],
        "recommendation": "comment_only", "summary": "", "finding_set_hash": "0" * 64,
    }), encoding="utf-8")
    with pytest.raises(SystemExit):
        vf.validate_findings(task_dir, log=_log())


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
