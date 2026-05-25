"""Tests for pr_queue._parse_slack_permalink — the new `adk pr-queue add` flow
distinguishes a slack permalink from a PR URL, then walks the thread.
"""
from __future__ import annotations

import json
import logging
from types import SimpleNamespace

import pytest

import pr_queue
import pr_scan
import queue_io
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


def test_add_from_pr_url_backfills_existing_slack_threads(tmp_path, monkeypatch, capsys):
    pr_url = "https://github.com/acme/foo/pull/1"
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text(json.dumps({"filters": None, "prs": []}), encoding="utf-8")

    monkeypatch.setattr(
        pr_scan,
        "cheap_pr_meta",
        lambda url, log: {"head_sha": "abc123", "state": "OPEN", "merged_at": None},
    )
    monkeypatch.setattr(
        queue_io,
        "load_slack_config",
        lambda _path=None: {
            "channels": ["C1", "C2"],
            "url_patterns": ["https://github.com/"],
            "scan_days_default": 14,
        },
    )

    def fake_scan(slack_cfg, oldest_ts, log):
        return [
            {
                "pr_url": pr_url,
                "slack": {"channel_id": "C1", "message_ts": "100.000",
                          "thread_ts": "100.000"},
            },
            {
                "pr_url": pr_url,
                "slack": {"channel_id": "C2", "message_ts": "200.000",
                          "thread_ts": "200.000"},
            },
            {
                "pr_url": "https://github.com/acme/foo/pull/2",
                "slack": {"channel_id": "C3", "thread_ts": "300.000"},
            },
        ], {"channels_scanned": 2}

    monkeypatch.setattr(pr_scan, "scan", fake_scan)

    rc = pr_queue._add_from_pr_url(
        pr_url,
        queue_path,
        SimpleNamespace(yes=True),
        logging.getLogger("test"),
    )

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["slack_lookup"]["matches"] == 2
    [row] = json.loads(queue_path.read_text())["prs"]
    assert [(t["channel_id"], t["thread_ts"]) for t in row["slack_threads"]] == [
        ("C1", "100.000"),
        ("C2", "200.000"),
    ]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
