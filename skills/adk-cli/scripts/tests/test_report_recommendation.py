"""Tests for improvement #2: report.py reads findings-final.json and
re-derives the recommendation from the post-triage set.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def report():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "report.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("report_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_findings_no_approval_is_comment_only(report):
    assert report.derive_recommendation([], approved_host=False) == "comment_only"


def test_no_findings_with_host_approval_is_approve(report):
    assert report.derive_recommendation([], approved_host=True) == "approve"


def test_any_blocker_is_request_changes(report):
    findings = [{"severity": "should-have"}, {"severity": "blocker"}]
    assert report.derive_recommendation(findings) == "request_changes"


def test_any_critical_is_request_changes(report):
    findings = [{"severity": "critical"}]
    assert report.derive_recommendation(findings) == "request_changes"


def test_only_should_have_is_comment_only(report):
    findings = [{"severity": "should-have"}, {"severity": "may-have"}]
    assert report.derive_recommendation(findings) == "comment_only"


def test_only_nitpick_is_comment_only(report):
    findings = [{"severity": "nitpick"}, {"severity": "question"}]
    assert report.derive_recommendation(findings) == "comment_only"


def test_approved_host_does_not_override_blocker(report):
    """If a blocker survives triage, host approval doesn't downgrade the verdict."""
    findings = [{"severity": "blocker"}]
    assert report.derive_recommendation(findings, approved_host=True) == "request_changes"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
