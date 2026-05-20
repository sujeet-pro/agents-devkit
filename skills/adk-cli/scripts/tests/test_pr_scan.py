"""Tests for pr_scan.scan() — focused on the thread-reply PR-link extraction
that's the headline change vs the legacy scan_slack.py.
"""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

import pr_scan


class FakeSlackClient:
    """Minimal stand-in for slack_helpers.SlackClient.

    Lets each test inject a (channel_id, messages-list, replies-by-thread-ts) tuple,
    instead of mocking the slack_sdk WebClient.
    """

    def __init__(self, channels: dict[str, tuple[list[dict], dict[str, list[dict]]]]):
        # name → (messages, replies-by-thread-ts)
        self._channels = channels
        self.added_reactions: list[tuple[str, str, str]] = []

    def resolve_channel(self, name_or_id: str) -> str:
        return name_or_id  # tests pass channel ids directly

    def iter_channel_messages(self, channel_id: str, oldest_ts: str):
        msgs, _ = self._channels[channel_id]
        return iter(msgs)

    def iter_thread_replies(self, channel_id: str, thread_ts: str):
        _, replies = self._channels[channel_id]
        return iter(replies.get(thread_ts, []))

    def get_message_permalink(self, channel_id: str, ts: str) -> str:
        return f"https://slack/{channel_id}/{ts}"

    def resolve_user_token(self, token: str):
        return None  # tests don't exercise user filtering

    def add_reaction(self, channel_id: str, ts: str, emoji_name: str) -> bool:
        self.added_reactions.append((channel_id, ts, emoji_name))
        return True


def _slack_cfg(url_patterns=None, channels=("C1",)) -> dict:
    return {
        "url_patterns": list(url_patterns or ["https://github.com/"]),
        "filter_mentioned_users": [],
        "status_emoji": {},
        "channels": list(channels),
    }


def test_main_message_with_two_pr_links_emits_two_rows(monkeypatch):
    fake = FakeSlackClient({
        "C1": (
            [{
                "ts": "100.000",
                "user": "U_alice",
                "text": "Please review https://github.com/acme/foo/pull/1 and https://github.com/acme/foo/pull/2",
                "reply_count": 0,
            }],
            {},
        )
    })
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, stats = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)

    assert len(candidates) == 2
    for c in candidates:
        assert c["slack"]["link_origin"] == "main"
        assert c["slack"]["message_ts"] == "100.000"
        assert c["slack"]["n_pr_links_in_message"] == 2
    assert stats["rows_from_main"] == 2
    assert stats["rows_from_replies"] == 0


def test_reply_pr_link_emits_row_with_reply_ts(monkeypatch):
    """The headline new behavior: a PR posted in a thread reply gets its OWN
    row, with message_ts == reply.ts (so reactions land on the reply, not on
    the parent), and link_origin = 'reply'.
    """
    main = {
        "ts": "100.000",
        "user": "U_alice",
        "text": "Initial PR: https://github.com/acme/foo/pull/1",
        "reply_count": 2,
    }
    reply1 = {
        "ts": "100.001",
        "user": "U_bob",
        "text": "Spinoff PR: https://github.com/acme/foo/pull/2",
    }
    reply2 = {
        "ts": "100.002",
        "user": "U_carol",
        "text": "And another: https://github.com/acme/foo/pull/3",
    }
    fake = FakeSlackClient({"C1": ([main], {"100.000": [main, reply1, reply2]})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)

    log = logging.getLogger("test")
    candidates, stats = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)

    # 1 from main + 2 from replies = 3 rows.
    assert len(candidates) == 3
    by_link = {c["pr_link"]: c for c in candidates}
    assert by_link["https://github.com/acme/foo/pull/1"]["slack"]["link_origin"] == "main"
    assert by_link["https://github.com/acme/foo/pull/1"]["slack"]["message_ts"] == "100.000"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["link_origin"] == "reply"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["message_ts"] == "100.001"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["thread_ts"] == "100.000"
    assert by_link["https://github.com/acme/foo/pull/3"]["slack"]["link_origin"] == "reply"
    assert by_link["https://github.com/acme/foo/pull/3"]["slack"]["message_ts"] == "100.002"
    assert stats["rows_from_main"] == 1
    assert stats["rows_from_replies"] == 2


def test_message_without_pr_link_skipped(monkeypatch):
    fake = FakeSlackClient({
        "C1": (
            [{"ts": "100.000", "user": "U_alice", "text": "no link here", "reply_count": 0}],
            {},
        )
    })
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, stats = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)
    assert candidates == []
    assert stats["threads_with_main_pr"] == 0


def test_supporting_docs_are_shared_across_thread_rows(monkeypatch):
    """Atlassian/GDoc/Figma URLs found anywhere in the thread should attach
    to every PR row emitted from that thread.
    """
    main = {
        "ts": "100.000",
        "user": "U_alice",
        "text": ("Review https://github.com/acme/foo/pull/1 — "
                 "spec at https://acme.atlassian.net/wiki/spaces/X/pages/42/Spec"),
        "reply_count": 1,
    }
    reply1 = {
        "ts": "100.001",
        "user": "U_bob",
        "text": ("Spinoff https://github.com/acme/foo/pull/2 — "
                 "designs https://www.figma.com/file/abc/Designs"),
    }
    fake = FakeSlackClient({"C1": ([main], {"100.000": [main, reply1]})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, _ = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)

    docs_per_pr = {c["pr_link"]: set(c["supporting_docs"]) for c in candidates}
    expected = {"https://acme.atlassian.net/wiki/spaces/X/pages/42/Spec",
                "https://www.figma.com/file/abc/Designs"}
    assert docs_per_pr["https://github.com/acme/foo/pull/1"] == expected
    assert docs_per_pr["https://github.com/acme/foo/pull/2"] == expected


def test_find_supporting_docs_excludes_pr_urls():
    text = ("https://github.com/acme/foo/pull/1 "
            "https://acme.atlassian.net/wiki/x "
            "https://docs.google.com/document/d/abc/edit")
    docs = pr_scan.find_supporting_docs(text)
    assert "https://github.com/acme/foo/pull/1" not in docs
    assert any("atlassian" in d for d in docs)
    assert any("docs.google.com" in d for d in docs)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
