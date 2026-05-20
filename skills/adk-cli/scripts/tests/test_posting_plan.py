"""Tests for build_posting_plan() in post_comments.py.

Covers:
  - GitHub: review_summary step encodes APPROVE/REQUEST_CHANGES/COMMENT
            in the event field; inline comments are bundled.
  - Bitbucket: review_summary + N inline_comment steps + (when applicable)
               a separate approve_pr step calling approvePullRequest.
  - approve_pr step never appears unless recommendation == "approve"
    AND approve_ready=True.
  - never_merge is always True.
  - resolve / reopen actions emit the right MCP tool per platform.
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
    spec = importlib.util.spec_from_file_location("post_comments_plan_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gh_pr() -> dict:
    return {"host": "github", "owner": "acme", "repo": "foo",
            "pr_number": 42, "head_oid": "abc123", "url": "https://github.com/acme/foo/pull/42"}


def _bb_pr() -> dict:
    return {"host": "bitbucket", "owner": "lastbrand", "repo": "ecomm-ssr",
            "pr_number": 5521, "head_oid": "deadbeef",
            "url": "https://bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5521"}


# ---- universal invariants -------------------------------------------------

def test_never_merge_is_always_true(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[],
        no_resolve_existing=False,
        approve_ready=False,
    )
    assert plan["never_merge"] is True
    assert all(s.get("kind") != "merge" for s in plan["steps"])
    assert all("merge_pull_request" not in str(s.get("mcp_tool", "")) for s in plan["steps"])
    assert all("mergePullRequest" not in str(s.get("mcp_tool", "")) for s in plan["steps"])


def test_plan_carries_pr_link(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[], no_resolve_existing=False, approve_ready=False,
    )
    assert plan["pr_link"] == _bb_pr()["url"]
    assert plan["host"] == "bitbucket"


# ---- GitHub: review_summary event encoding --------------------------------

def test_gh_review_summary_event_approve(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"findings": [{"id": "f-001", "file": "src/a.py",
                                      "line_start": 1, "line_end": 1,
                                      "title": "x", "severity": "may-have",
                                      "dimension": "tests"}],
                       "recommendation": "approve", "summary": "looks good"},
        actions=[], no_resolve_existing=False, approve_ready=True,
    )
    review = next(s for s in plan["steps"] if s.get("kind") == "review_summary")
    assert review["mcp_tool"] == "mcp__adk-mcp-github__pull_request_review_write"
    assert review["mcp_args"]["event"] == "APPROVE"
    # GitHub also emits a discrete approve_pr step for clarity (bundled).
    approve = [s for s in plan["steps"] if s.get("kind") == "approve_pr"]
    assert len(approve) == 1
    assert approve[0].get("via") == "bundled_in_review_summary_event=APPROVE"


def test_gh_review_summary_event_request_changes(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"findings": [{"id": "f-001", "file": "src/a.py",
                                      "line_start": 1, "line_end": 1,
                                      "title": "x", "severity": "blocker",
                                      "dimension": "correctness"}],
                       "recommendation": "request_changes", "summary": "fix this"},
        actions=[], no_resolve_existing=False, approve_ready=False,
    )
    review = next(s for s in plan["steps"] if s.get("kind") == "review_summary")
    assert review["mcp_args"]["event"] == "REQUEST_CHANGES"
    # No approve_pr step when not mergeable.
    assert not any(s.get("kind") == "approve_pr" for s in plan["steps"])


# ---- Bitbucket: separate approve step -------------------------------------

def test_bb_approve_pr_separate_step(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "approve",
                       "summary": "lgtm"},
        actions=[], no_resolve_existing=False, approve_ready=True,
    )
    approve = [s for s in plan["steps"] if s.get("kind") == "approve_pr"]
    assert len(approve) == 1
    assert approve[0]["mcp_tool"] == "mcp__adk-mcp-bitbucket__approvePullRequest"
    assert approve[0]["mcp_args"]["pullRequestId"] == 5521


def test_bb_no_approve_when_not_approve_ready(pc_mod):
    """approve_ready=False (e.g. open thread to reopen) blocks the approve step."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "approve",
                       "summary": ""},
        actions=[], no_resolve_existing=False, approve_ready=False,
    )
    assert not any(s.get("kind") == "approve_pr" for s in plan["steps"])


def test_no_approve_when_recommendation_not_approve(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only",
                       "summary": ""},
        actions=[], no_resolve_existing=False, approve_ready=True,
    )
    assert not any(s.get("kind") == "approve_pr" for s in plan["steps"])


# ---- resolve / reopen MCP tools ------------------------------------------

def test_bb_resolve_uses_resolveComment(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[{"comment_id": "999", "decision": "resolve",
                  "verified": True, "reason": "diff touched line"}],
        no_resolve_existing=False, approve_ready=False,
    )
    resolves = [s for s in plan["steps"] if s.get("kind") == "resolve"]
    assert len(resolves) == 1
    assert resolves[0]["mcp_tool"] == "mcp__adk-mcp-bitbucket__resolveComment"
    assert resolves[0]["mcp_args"]["commentID"] == "999"


def test_bb_reopen_uses_reopenComment(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[{"comment_id": "888", "decision": "reopen",
                  "verified": True, "reason": "diff did not address"}],
        no_resolve_existing=False, approve_ready=False,
    )
    reopens = [s for s in plan["steps"] if s.get("kind") == "reopen"]
    assert len(reopens) == 1
    assert reopens[0]["mcp_tool"] == "mcp__adk-mcp-bitbucket__reopenComment"


def test_gh_resolve_uses_reply(pc_mod):
    """GitHub's REST + most token scopes can't flip resolved state — plan
    emits a textual reply via add_reply_to_pull_request_comment."""
    plan = pc_mod.build_posting_plan(
        pr=_gh_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[{"comment_id": "777", "decision": "resolve",
                  "verified": True, "reason": "fixed"}],
        no_resolve_existing=False, approve_ready=False,
    )
    resolves = [s for s in plan["steps"] if s.get("kind") == "resolve"]
    assert resolves[0]["mcp_tool"] == "mcp__adk-mcp-github__add_reply_to_pull_request_comment"


def test_unverified_actions_excluded(pc_mod):
    """An action with verified=False must not enter the plan — the resolver
    explicitly rejected it."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[{"comment_id": "555", "decision": "resolve",
                  "verified": False, "reason": "could not verify"}],
        no_resolve_existing=False, approve_ready=False,
    )
    assert not any(s.get("kind") in ("resolve", "reopen") for s in plan["steps"])


def test_no_resolve_existing_skips_all_resolves(pc_mod):
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[{"comment_id": "555", "decision": "resolve", "verified": True}],
        no_resolve_existing=True, approve_ready=False,
    )
    assert not any(s.get("kind") in ("resolve", "reopen") for s in plan["steps"])


# ---- empty review suppression flows through ------------------------------

def test_empty_findings_emits_skip_marker(pc_mod):
    """When n_findings==0 and recommendation != approve, the plan records
    review_summary_skipped instead of the review_summary."""
    plan = pc_mod.build_posting_plan(
        pr=_bb_pr(),
        findings_blob={"findings": [], "recommendation": "comment_only"},
        actions=[], no_resolve_existing=False, approve_ready=False,
    )
    assert any(s.get("kind") == "review_summary_skipped" for s in plan["steps"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
