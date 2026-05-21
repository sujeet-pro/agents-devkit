"""Tests for Phase 8 — appreciations route to PR-level general comments.

  - format_appreciation_body includes the *Location:* file:line marker.
  - build_posting_plan emits a `general_comment` step per appreciation
    on both platforms with the correct MCP tool + args.
  - GitHub: appreciations DO NOT appear in the review_summary `comments[]`
    inline array (they're not inline).
  - Bitbucket: appreciations DO NOT appear as `inline_comment` steps
    (the only BB steps for them carry `kind=general_comment` and have no
    `inline` arg in mcp_args).
  - Appreciations are posted even when there are no issues + recommendation
    isn't 'approve' (e.g. comment_only with only-appreciations).
  - triage.py --init auto-accepts every appreciation.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def pc_mod():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "post_comments.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("post_comments_phase8", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def triage_mod():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "triage.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("triage_phase8", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gh_pr() -> dict:
    return {"host": "github", "owner": "acme", "repo": "foo",
            "pr_number": 42, "head_sha": "abc123", "url": "https://github.com/acme/foo/pull/42"}


def _bb_pr() -> dict:
    return {"host": "bitbucket", "owner": "acme", "repo": "ecomm-ssr",
            "pr_number": 5521, "head_sha": "deadbeef",
            "url": "https://bitbucket.org/acme/ecomm-ssr/pull-requests/5521"}


def _appr(fid: str = "f-010", file: str = "src/auth.py",
          line_start: int = 88, line_end: int | None = 102) -> dict:
    return {"id": fid, "title": "Clean AuthProvider split",
            "severity": "appreciation", "dimension": "style",
            "confidence": "high", "file": file,
            "line_start": line_start,
            "line_end": line_end if line_end is not None else line_start,
            "body": "Nice — split keeps SessionService easy to swap.",
            "evidence": [{"kind": "code", "ref": f"{file}:{line_start}"}]}


# ---- format_appreciation_body location marker ----------------------------

def test_appreciation_body_has_location_marker(pc_mod):
    out = pc_mod.format_appreciation_body(_appr())
    assert "*Location:* `src/auth.py:88-102`" in out
    assert "🎉" in out


def test_appreciation_body_single_line_location(pc_mod):
    f = _appr(line_start=42, line_end=42)
    out = pc_mod.format_appreciation_body(f)
    assert "*Location:* `src/auth.py:42`" in out


def test_appreciation_body_missing_line_skips_location(pc_mod):
    f = {"id": "f-x", "title": "x", "severity": "appreciation",
         "dimension": "style", "confidence": "high", "file": "",
         "body": "nice", "evidence": [{"kind": "code", "ref": "?"}]}
    out = pc_mod.format_appreciation_body(f)
    assert "Location" not in out  # no false location when we have no file


# ---- posting plan: GitHub general_comment ---------------------------------

def test_gh_appreciation_emits_add_issue_comment(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"recommendation": "comment_only",
                       "findings": [_appr()]},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    gen = [s for s in plan["steps"] if s.get("kind") == "general_comment"]
    assert len(gen) == 1
    assert gen[0]["mcp_tool"] == "mcp__adk-mcp-github__add_issue_comment"
    assert gen[0]["mcp_args"]["issue_number"] == 42
    assert "🎉" in gen[0]["mcp_args"]["body"]
    assert gen[0]["finding_id"] == "f-010"
    assert plan["n_appreciations"] == 1
    assert plan["n_issues"] == 0


def test_gh_appreciation_not_in_review_summary_inline(pc_mod):
    """An appreciation must NOT appear in pull_request_review_write.comments[]."""
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"recommendation": "comment_only",
                       "findings": [
                           _appr("f-010"),
                           {"id": "f-001", "title": "x", "severity": "should-have",
                            "dimension": "tests", "confidence": "med",
                            "file": "b.py", "line_start": 1, "line_end": 1,
                            "body": "no test", "evidence": [{"kind": "diff", "ref": "b.py:1"}]},
                       ]},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    review = next(s for s in plan["steps"] if s.get("kind") == "review_summary")
    inline_paths = [c["path"] for c in review["mcp_args"]["comments"]]
    assert "src/auth.py" not in inline_paths   # appreciation excluded
    assert "b.py" in inline_paths              # issue included


# ---- posting plan: Bitbucket general_comment ------------------------------

def test_bb_appreciation_emits_addPullRequestComment_no_inline(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"recommendation": "comment_only",
                       "findings": [_appr()]},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    gen = [s for s in plan["steps"] if s.get("kind") == "general_comment"]
    assert len(gen) == 1
    assert gen[0]["mcp_tool"] == "mcp__adk-mcp-bitbucket__addPullRequestComment"
    assert "inline" not in gen[0]["mcp_args"]  # critical: NO inline arg
    assert gen[0]["mcp_args"]["pullRequestId"] == 5521
    assert "🎉" in gen[0]["mcp_args"]["content"]["raw"]


def test_bb_appreciation_not_in_inline_steps(pc_mod):
    """A BB appreciation must not produce an `inline_comment` step."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"recommendation": "comment_only",
                       "findings": [_appr()]},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    assert not any(s.get("kind") == "inline_comment" for s in plan["steps"])


# ---- appreciation-only PR still posts -------------------------------------

def test_only_appreciations_still_post(pc_mod):
    """A PR with ZERO issues + only appreciations must still emit general_comment steps."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"recommendation": "comment_only",
                       "findings": [_appr("f-010"), _appr("f-011", file="b.py", line_start=5)]},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    gen = [s for s in plan["steps"] if s.get("kind") == "general_comment"]
    assert len(gen) == 2
    # No review_summary_skipped marker — appreciations are present so the
    # plan isn't empty. (BB skips the review_summary entirely; GH doesn't
    # bundle anything either because issues_only is empty AND recommendation
    # isn't approve.)
    skipped = [s for s in plan["steps"] if s.get("kind") == "review_summary_skipped"]
    assert len(skipped) == 0


def test_only_appreciations_skipped_when_disabled_via_no_findings(pc_mod):
    """If issues_only is empty AND no appreciations either, we get the skip marker."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"recommendation": "comment_only", "findings": []},
        actions=[], no_resolve_existing=False, approve_ready=False,
        slack_summary_enabled=False, queue_ctx=None,
    )
    assert any(s.get("kind") == "review_summary_skipped" for s in plan["steps"])


# ---- triage auto-accepts appreciations -----------------------------------

def test_triage_init_auto_accepts_appreciations(tmp_path, triage_mod):
    """Even with --default-state pending (interactive mode), appreciations
    start at `accept` — they never enter the walk."""
    findings_blob = {
        "findings": [
            {"id": "f-001", "severity": "blocker", "title": "x"},
            {"id": "f-010", "severity": "appreciation", "title": "nice"},
            {"id": "f-011", "severity": "appreciation", "title": "good test"},
        ],
        "recommendation": "request_changes",
    }
    (tmp_path / "findings.json").write_text(json.dumps(findings_blob), encoding="utf-8")
    import logging
    log = logging.getLogger("test")
    result = triage_mod.cmd_init(tmp_path, "pending", log)
    assert result["n_auto_accepted_appreciations"] == 2
    state = json.loads((tmp_path / "triage-state.json").read_text(encoding="utf-8"))
    assert state["findings"]["f-001"]["state"] == "pending"
    assert state["findings"]["f-010"]["state"] == "accept"
    assert state["findings"]["f-010"]["auto_accepted"] is True
    assert state["findings"]["f-011"]["state"] == "accept"


def test_triage_init_auto_mode_works_unchanged(tmp_path, triage_mod):
    """--default-state accept: everything accepted, appreciations same."""
    findings_blob = {
        "findings": [
            {"id": "f-001", "severity": "blocker", "title": "x"},
            {"id": "f-010", "severity": "appreciation", "title": "nice"},
        ],
        "recommendation": "request_changes",
    }
    (tmp_path / "findings.json").write_text(json.dumps(findings_blob), encoding="utf-8")
    import logging
    log = logging.getLogger("test")
    result = triage_mod.cmd_init(tmp_path, "accept", log)
    assert result["n_auto_accepted_appreciations"] == 1
    state = json.loads((tmp_path / "triage-state.json").read_text(encoding="utf-8"))
    assert state["findings"]["f-001"]["state"] == "accept"
    assert state["findings"]["f-010"]["state"] == "accept"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
