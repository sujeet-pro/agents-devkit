"""Tests for improvement #3: post_comments.py refuses an empty request_changes
review.

When triage rejects every finding, the post step must not transmit a
`request_changes` verdict with zero inline comments — that's a confusing
artifact on the PR. Resolves/reopens are still allowed to proceed.
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


def test_should_post_review_false_when_empty_request_changes(post_comments):
    """The core fix: n_findings=0 + request_changes → suppress."""
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "request_changes"}) is False


def test_should_post_review_false_when_empty_comment_only(post_comments):
    """Empty comment_only is also a no-op."""
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "comment_only"}) is False


def test_should_post_review_true_when_empty_approve(post_comments):
    """Empty 'approve' IS meaningful — author wants the approval recorded."""
    assert post_comments.should_post_review({"findings": [],
                                             "recommendation": "approve"}) is True


def test_plan_only_reflects_suppression(post_comments):
    """plan_only output should show would_post_review=False for the empty case."""
    out = post_comments.plan_only(
        Path("/tmp/x"),
        {"findings": [], "recommendation": "request_changes"},
        actions=[{"decision": "resolve", "verified": True}],
    )
    assert out["would_post_review"] is False
    assert out["n_findings"] == 0
    assert out["n_resolve"] == 1


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
