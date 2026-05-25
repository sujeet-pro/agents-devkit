"""Tests for post_comments.should_post_review.

Policy (2026-05-22): every review takes a verdict (`approve` /
`request_changes`). The review summary post carries that verdict, so we
post it whenever there's a verdict to express. Empty reviews without a verdict
are suppressed.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def post_comments():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "post_comments.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("post_comments_under_test_empty", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_should_post_review_true_when_findings(post_comments):
    assert post_comments.should_post_review({"findings": [{"severity": "blocker"}],
                                             "recommendation": "request_changes"}) is True


def test_should_post_review_true_when_empty_request_changes(post_comments):
    """Empty request_changes IS meaningful — surfaces the verdict. After the
    2026-05-22 policy change, derive_recommendation only emits this when
    there's at least one blocker, so n=0+request_changes should not occur
    in practice — but if it does, post the verdict (it carries information).
    """
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "request_changes"}) is True


def test_should_post_review_false_when_empty_unknown_verdict(post_comments):
    """An empty review without approve/request_changes has nothing to post."""
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "comment_only"}) is False


def test_should_post_review_true_when_empty_approve(post_comments):
    """Empty 'approve' IS meaningful — author wants the approval recorded."""
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "approve"}) is True


def test_plan_only_reflects_post_for_request_changes(post_comments):
    """plan_only should show would_post_review=True for any verdict
    (approve / request_changes), even with zero findings."""
    out = post_comments.plan_only(
        Path("/tmp/x"),
        {"findings": [], "recommendation": "request_changes"},
        actions=[{"decision": "resolve", "verified": True}],
    )
    assert out["would_post_review"] is True
    assert out["n_findings"] == 0
    assert out["n_resolve"] == 1


def test_plan_only_suppresses_empty_unknown_verdict(post_comments):
    """Unknown verdict + zero findings is suppressed."""
    out = post_comments.plan_only(
        Path("/tmp/x"),
        {"findings": [], "recommendation": "comment_only"},
        actions=[],
    )
    assert out["would_post_review"] is False
    assert out["n_findings"] == 0


def test_plan_only_normal_case(post_comments):
    """When findings exist, would_post_review=True."""
    out = post_comments.plan_only(
        Path("/tmp/x"),
        {"findings": [{"severity": "blocker", "id": "f-001"}], "recommendation": "request_changes"},
        actions=[],
    )
    assert out["would_post_review"] is True
    assert out["n_findings"] == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
