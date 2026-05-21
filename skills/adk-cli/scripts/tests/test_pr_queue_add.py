"""Tests for pr_queue._parse_slack_permalink — the new `adk pr-queue add` flow
distinguishes a slack permalink from a PR URL, then walks the thread.
"""
from __future__ import annotations

import pytest

from pr_queue import _parse_slack_permalink, _looks_like_pr_url


def test_parses_slack_permalink_with_thread_ts():
    url = ("https://acme.slack.com/archives/C123ABC/p1700000123000456"
           "?thread_ts=1700000000.000123&cid=C123ABC")
    parsed = _parse_slack_permalink(url)
    assert parsed is not None
    assert parsed["channel_id"] == "C123ABC"
    assert parsed["message_ts"] == "1700000123.000456"
    assert parsed["thread_ts"] == "1700000000.000123"
    assert parsed["workspace"] == "acme"


def test_parses_slack_permalink_without_thread_ts():
    url = "https://acme.slack.com/archives/G456DEF/p1700000123000456"
    parsed = _parse_slack_permalink(url)
    assert parsed is not None
    assert parsed["channel_id"] == "G456DEF"
    assert parsed["message_ts"] == "1700000123.000456"
    assert "thread_ts" not in parsed


def test_non_slack_url_returns_none():
    assert _parse_slack_permalink("https://github.com/acme/foo/pull/1") is None
    assert _parse_slack_permalink("not a url") is None


def test_pr_url_recognition():
    assert _looks_like_pr_url("https://github.com/acme/foo/pull/1")
    assert _looks_like_pr_url("https://bitbucket.org/team/repo/pull-requests/42")
    assert not _looks_like_pr_url("https://github.com/acme/foo/issues/1")
    assert not _looks_like_pr_url("https://example.com/slack/foo")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
