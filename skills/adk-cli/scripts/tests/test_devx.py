"""Tests for Phase 7 — DevX of /adk-pr-review.

Covers:
  - format_comment_body human-voice template (What's happening / Why /
    Suggested fix) and severity opening lines.
  - format_appreciation_body — 🎉 title, no fix-section, no impact.
  - format_review_summary — appreciations called out separately from issues.
  - has_only_appreciations gate.
  - format_slack_summary — emoji verdict + items-to-fix bullets + link.
  - build_posting_plan emits a slack_summary step when queue_ctx has the
    channel/thread; emits slack_summary_skipped otherwise.
  - render_finding_block from report.py emits "Code in question" when
    the file exists under task_dir/code/ and "What will be posted" preview.
"""
from __future__ import annotations

import importlib.util
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
    spec = importlib.util.spec_from_file_location("post_comments_devx", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def report_mod():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "report.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("report_devx", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- format_comment_body (human voice) -----------------------------------

def test_body_has_whats_happening_section(pc_mod):
    f = {"id": "f-001", "title": "Token check skips expiry",
         "severity": "blocker", "dimension": "security",
         "confidence": "high", "file": "src/x.py",
         "line_start": 42, "line_end": 48,
         "body": "validateToken returns true even when exp < now.",
         "impact_if_unfixed": "Expired tokens accepted.",
         "suggestion": "if datetime.now() > exp: return False",
         "evidence": [{"kind": "diff", "ref": "src/x.py:42-48"}]}
    out = pc_mod.format_comment_body(f)
    assert "### What's happening" in out
    assert "### Why this matters" in out
    assert "### Suggested fix" in out
    assert "Must fix before merge" in out  # friendly category label
    assert "Token check skips expiry" in out


def test_body_severity_opening_present(pc_mod):
    """Each non-appreciation severity has a friendly opening line."""
    f_base = {"id": "f-001", "title": "x", "dimension": "tests",
              "confidence": "high", "file": "a.py", "line_start": 1, "line_end": 1,
              "body": "b", "evidence": [{"kind": "diff", "ref": "a:1"}]}
    out = pc_mod.format_comment_body({**f_base, "severity": "nitpick"})
    assert "feel free to ignore" in out.lower()


def test_body_question_replaces_what_with_clarification(pc_mod):
    f = {"id": "f-005", "title": "Unclear on rate limit",
         "severity": "question", "dimension": "feature-flow",
         "confidence": "low", "file": "a.py", "line_start": 1, "line_end": 1,
         "body": "Why use 100 RPM and not the existing config?",
         "evidence": [{"kind": "diff", "ref": "a:1"}]}
    out = pc_mod.format_comment_body(f)
    assert "What I'm not sure about" in out
    assert "Suggested fix" not in out
    assert "Why this matters" not in out


def test_body_appreciation_uses_celebratory_template(pc_mod):
    f = {"id": "f-010", "title": "Clean AuthProvider split",
         "severity": "appreciation", "dimension": "style",
         "confidence": "high", "file": "auth/login.py",
         "line_start": 88, "line_end": 102,
         "body": "Splitting AuthProvider from SessionService makes SSO swap easy.",
         "evidence": [{"kind": "code", "ref": "auth/login.py:88-102"}]}
    out = pc_mod.format_comment_body(f)
    assert "🎉" in out
    assert "Appreciation" in out
    assert "Suggested fix" not in out
    assert "Why this matters" not in out


# ---- format_review_summary ------------------------------------------------

def test_summary_separates_appreciations_from_issues(pc_mod):
    blob = {
        "recommendation": "approve",
        "summary": "Looks ready.",
        "findings": [
            {"severity": "appreciation", "title": "Nice split"},
            {"severity": "appreciation", "title": "Good test boundary"},
            {"severity": "nitpick", "title": "naming"},
        ],
    }
    out = pc_mod.format_review_summary(blob)
    assert "**Appreciations:** 2" in out
    assert "Nice to have" in out  # nitpick maps to "Nice to have"
    assert "Approving" in out


def test_summary_no_findings_says_none(pc_mod):
    blob = {"recommendation": "approve", "summary": "lgtm", "findings": []}
    out = pc_mod.format_review_summary(blob)
    assert "**Issues:** none" in out


# ---- has_only_appreciations ----------------------------------------------

def test_only_appreciations(pc_mod):
    assert pc_mod.has_only_appreciations(
        {"findings": [{"severity": "appreciation"}, {"severity": "appreciation"}]}
    ) is True


def test_appreciation_plus_issue_is_not_only(pc_mod):
    assert pc_mod.has_only_appreciations(
        {"findings": [{"severity": "appreciation"}, {"severity": "blocker"}]}
    ) is False


def test_empty_is_not_only(pc_mod):
    assert pc_mod.has_only_appreciations({"findings": []}) is False


# ---- format_slack_summary -------------------------------------------------

def _pr() -> dict:
    return {"host": "bitbucket", "owner": "acme", "repo": "ecomm-ssr",
            "pr_number": 5521, "url": "https://bitbucket.org/acme/ecomm-ssr/pull-requests/5521"}


def test_slack_summary_approve(pc_mod):
    out = pc_mod.format_slack_summary(
        pr=_pr(),
        findings_blob={"findings": [], "recommendation": "approve"},
        approve_ready=True,
        actions=[],
    )
    assert "white_check_mark" in out
    assert "APPROVE" in out
    assert "ecomm-ssr#5521" in out


def test_slack_summary_blockers_listed(pc_mod):
    out = pc_mod.format_slack_summary(
        pr=_pr(),
        findings_blob={"recommendation": "request_changes", "findings": [
            {"severity": "blocker", "title": "Auth bypass", "file": "a.py", "line_start": 1},
            {"severity": "blocker", "title": "SQL injection", "file": "b.py", "line_start": 2},
        ]},
        approve_ready=False, actions=[],
    )
    assert "Items to fix:" in out
    assert "Auth bypass" in out
    assert "SQL injection" in out
    assert "octagonal_sign" in out


def test_slack_summary_truncates_long_blocker_lists(pc_mod):
    findings = [{"severity": "blocker", "title": f"issue {i}",
                 "file": "x.py", "line_start": i} for i in range(8)]
    out = pc_mod.format_slack_summary(
        pr=_pr(),
        findings_blob={"recommendation": "request_changes", "findings": findings},
        approve_ready=False, actions=[],
    )
    assert "+3 more" in out


def test_slack_summary_mentions_appreciations(pc_mod):
    out = pc_mod.format_slack_summary(
        pr=_pr(),
        findings_blob={"recommendation": "comment_only", "findings": [
            {"severity": "appreciation", "title": "nice"},
            {"severity": "should-have", "title": "small fix", "file": "x.py", "line_start": 1},
        ]},
        approve_ready=False, actions=[],
    )
    assert "1 appreciation" in out
    assert "PR comment" in out  # general comments, not inline


# ---- posting plan slack step -------------------------------------------

def test_plan_includes_slack_step_when_queue_ctx_has_thread(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_pr(),
        findings_blob={"recommendation": "approve", "findings": []},
        actions=[], no_resolve_existing=False, approve_ready=True,
        slack_summary_enabled=True,
        queue_ctx={"slack": {"channel_id": "C12345", "thread_ts": "1700000000.000001"}},
    )
    slack_steps = [s for s in plan["steps"] if s.get("kind") == "slack_summary"]
    assert len(slack_steps) == 1
    assert slack_steps[0]["mcp_tool"] == "mcp__adk-mcp-slack__conversations_add_message"
    # MCP signature uses `channel_id`, not the older `channel` REST naming.
    assert slack_steps[0]["mcp_args"]["channel_id"] == "C12345"
    assert slack_steps[0]["mcp_args"]["thread_ts"] == "1700000000.000001"
    assert "APPROVE" in slack_steps[0]["mcp_args"]["text"]


def test_plan_emits_skipped_without_queue_ctx(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_pr(),
        findings_blob={"recommendation": "approve", "findings": []},
        actions=[], no_resolve_existing=False, approve_ready=True,
        slack_summary_enabled=True,
        queue_ctx=None,
    )
    # No queue ctx → no step at all (the plan doesn't include the slack section).
    assert not any(s.get("kind") == "slack_summary" for s in plan["steps"])


def test_plan_emits_skipped_with_queue_ctx_but_no_channel(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_pr(),
        findings_blob={"recommendation": "approve", "findings": []},
        actions=[], no_resolve_existing=False, approve_ready=True,
        slack_summary_enabled=True,
        queue_ctx={"slack": {}},
    )
    skipped = [s for s in plan["steps"] if s.get("kind") == "slack_summary_skipped"]
    assert len(skipped) == 1


def test_plan_no_slack_when_disabled(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_pr(),
        findings_blob={"recommendation": "approve", "findings": []},
        actions=[], no_resolve_existing=False, approve_ready=True,
        slack_summary_enabled=False,
        queue_ctx={"slack": {"channel_id": "C12345", "thread_ts": "1700.0001"}},
    )
    assert not any(s.get("kind", "").startswith("slack_") for s in plan["steps"])


# ---- rich findings.md rendering -----------------------------------------

def test_render_finding_block_includes_code_snippet(tmp_path, report_mod):
    """When task_dir/code/<file> exists, the rich block includes the snippet."""
    (tmp_path / "code" / "src").mkdir(parents=True)
    (tmp_path / "code" / "src" / "auth.py").write_text(
        "\n".join([f"line {i}" for i in range(1, 30)]) + "\n", encoding="utf-8"
    )
    f = {"id": "f-001", "title": "x", "severity": "blocker", "dimension": "security",
         "confidence": "high", "file": "src/auth.py", "line_start": 10, "line_end": 12,
         "body": "issue", "impact_if_unfixed": "bad", "suggestion": "fix",
         "evidence": [{"kind": "diff", "ref": "src/auth.py:10-12"}]}
    block = report_mod.render_finding_block(f, task_dir=tmp_path, format_comment_body=None)
    assert "Code in question" in block
    assert "line 10" in block
    assert "line 12" in block
    # Context lines around the finding land too.
    assert "line 6" in block or "line 7" in block


def test_render_finding_block_appreciation_skips_fix(tmp_path, report_mod):
    f = {"id": "f-010", "title": "nice", "severity": "appreciation",
         "dimension": "style", "confidence": "high",
         "file": "x.py", "line_start": 1, "line_end": 1,
         "body": "good split", "evidence": [{"kind": "code", "ref": "x.py:1"}]}
    block = report_mod.render_finding_block(f, task_dir=tmp_path)
    assert "What's nice about this" in block
    assert "Suggested fix" not in block
    assert "Why this matters" not in block


def test_render_finding_block_includes_post_preview_when_helper_provided(tmp_path, report_mod, pc_mod):
    f = {"id": "f-001", "title": "x", "severity": "should-have",
         "dimension": "tests", "confidence": "med",
         "file": "y.py", "line_start": 1, "line_end": 2,
         "body": "needs test", "impact_if_unfixed": "regress",
         "evidence": [{"kind": "test", "ref": "y_test.py"}]}
    block = report_mod.render_finding_block(
        f, task_dir=tmp_path, format_comment_body=pc_mod.format_comment_body,
    )
    assert "What will be posted (preview)" in block


def test_render_findings_md_groups_appreciations_separately(tmp_path, report_mod, pc_mod):
    pr = {"host": "bitbucket", "owner": "x", "repo": "y", "pr_number": 1,
          "url": "https://x", "title": "test PR"}
    blob = {"recommendation": "approve", "summary": "looks good",
            "findings": [
                {"id": "f-001", "title": "Nice split", "severity": "appreciation",
                 "dimension": "style", "confidence": "high",
                 "file": "a.py", "line_start": 1, "line_end": 1,
                 "body": "well-named", "evidence": [{"kind": "code", "ref": "a.py:1"}]},
                {"id": "f-002", "title": "Missing edge case", "severity": "should-have",
                 "dimension": "tests", "confidence": "med",
                 "file": "b.py", "line_start": 5, "line_end": 10,
                 "body": "no test for null path", "impact_if_unfixed": "regress",
                 "evidence": [{"kind": "diff", "ref": "b.py:5-10"}]},
            ]}
    md = report_mod.render_findings_md(
        task_dir=tmp_path, pr=pr, findings_blob=blob,
        appreciations=[blob["findings"][0]], issues=[blob["findings"][1]],
        actions=[],
    )
    assert "🎉 Appreciations (1)" in md
    assert "Issues (1)" in md
    # Verdict line is human-readable, not the raw enum.
    assert "Approving" in md
    # findings.md heading is the PR identifier.
    assert "y#1" in md


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
