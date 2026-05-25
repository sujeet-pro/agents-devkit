"""Tests for report.py:derive_recommendation.

Policy (2026-05-22): every review takes a verdict — `approve` or
`request_changes`. The `comment_only` middle ground is gone, and our verdict
is independent of other reviewers' state on the host.
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


def test_no_findings_defaults_to_approve(report):
    """Zero findings → approve."""
    assert report.derive_recommendation([]) == "approve"


def test_only_appreciations_is_approve(report):
    """Appreciations don't count as real issues — clean approve."""
    findings = [{"severity": "appreciation"}, {"severity": "appreciation"}]
    assert report.derive_recommendation(findings) == "approve"


def test_any_blocker_is_request_changes(report):
    findings = [{"severity": "should-have"}, {"severity": "blocker"}]
    assert report.derive_recommendation(findings) == "request_changes"


def test_any_critical_is_request_changes(report):
    findings = [{"severity": "critical"}]
    assert report.derive_recommendation(findings) == "request_changes"


def test_only_should_have_is_approve(report):
    """Non-blocking severities (should-have/may-have) ride along on an approve."""
    findings = [{"severity": "should-have"}, {"severity": "may-have"}]
    assert report.derive_recommendation(findings) == "approve"


def test_only_nitpick_is_approve(report):
    """Nitpicks and questions are non-blocking — approve."""
    findings = [{"severity": "nitpick"}, {"severity": "question"}]
    assert report.derive_recommendation(findings) == "approve"


def test_blocker_requests_changes(report):
    """If a blocker survives triage, the verdict is request_changes."""
    findings = [{"severity": "blocker"}]
    assert report.derive_recommendation(findings) == "request_changes"


def test_non_blocking_finding_approves(report):
    findings = [{"severity": "should-have"}]
    assert report.derive_recommendation(findings) == "approve"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
