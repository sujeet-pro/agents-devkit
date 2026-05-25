"""Tests for pr_scan.scan() — focused on thread-reply PR-link extraction."""
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
        self.thread_replies: list[tuple[str, str, str]] = []

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

    def post_thread_reply(self, channel_id: str, thread_ts: str, text: str) -> str:
        self.thread_replies.append((channel_id, thread_ts, text))
        return "reply-ts"


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
        assert len(c["related_pr_urls"]) == 1
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
    by_link = {c["pr_url"]: c for c in candidates}
    assert by_link["https://github.com/acme/foo/pull/1"]["slack"]["link_origin"] == "main"
    assert by_link["https://github.com/acme/foo/pull/1"]["slack"]["message_ts"] == "100.000"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["link_origin"] == "reply"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["message_ts"] == "100.001"
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["thread_ts"] == "100.000"
    assert by_link["https://github.com/acme/foo/pull/2"]["related_pr_urls"] == [
        "https://github.com/acme/foo/pull/1",
        "https://github.com/acme/foo/pull/3",
    ]
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


def test_orchestrated_scan_emits_channel_progress(monkeypatch, capsys):
    messages = [
        {"ts": f"{100 + i}.000", "user": "U_alice", "text": "no link", "reply_count": 0}
        for i in range(25)
    ]
    messages.append({
        "ts": "200.000",
        "user": "U_alice",
        "text": "Please review https://github.com/acme/foo/pull/1",
        "reply_count": 0,
    })
    fake = FakeSlackClient({"C1": (messages, {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    monkeypatch.setenv("ADK_ORCHESTRATED", "1")

    candidates, stats = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=logging.getLogger("test"))

    out = capsys.readouterr().out
    assert len(candidates) == 1
    assert stats["messages_seen"] == 26
    assert "ADK_EVENT" in out
    assert "channel 1/1 C1: 25 messages" in out
    assert "found PR thread 1 after 26 messages" in out


def test_gentle_reminder_posts_once_for_unrelated_multi_pr_thread(monkeypatch):
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    rows = [
        {
            "pr_url": "https://github.com/acme/foo/pull/1",
            "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
            "_meta": {"repo": "foo", "title": "FAQ widget", "source_branch": "faq"},
        },
        {
            "pr_url": "https://github.com/acme/foo/pull/2",
            "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
            "_meta": {"repo": "foo", "title": "Best sellers widget", "source_branch": "best-sellers"},
        },
    ]

    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False, logging.getLogger("test")
    )

    assert stats["posted"] == 1
    assert len(fake.thread_replies) == 1
    assert rows[0]["slack"]["gentle_reminder_at"]
    assert rows[1]["slack"]["gentle_reminder_at"]


def test_gentle_reminder_does_not_repost_when_queue_marked(monkeypatch):
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    rows = [{
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
        "_meta": {"title": "FAQ", "source_branch": "faq"},
    }]
    existing = {"prs": [{
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"channel_id": "C1", "thread_ts": "100.000", "gentle_reminder_at": "2026-05-22T00:00:00Z"},
    }]}

    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, existing, {"gentle_reminder_enabled": True}, False, logging.getLogger("test")
    )

    assert stats["skipped_existing"] == 1
    assert fake.thread_replies == []


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

    docs_per_pr = {c["pr_url"]: set(c["supporting_docs"]) for c in candidates}
    expected = {"https://acme.atlassian.net/wiki/spaces/X/pages/42/Spec",
                "https://www.figma.com/file/abc/Designs"}
    assert docs_per_pr["https://github.com/acme/foo/pull/1"] == expected
    assert docs_per_pr["https://github.com/acme/foo/pull/2"] == expected


def test_filter_mentioned_users_matches_bot_authored_messages(monkeypatch):
    main = {
        "ts": "100.000",
        "bot_id": "B999BOT",
        "app_id": "A999APP",
        "text": "Review https://github.com/acme/foo/pull/1",
        "reply_count": 0,
    }
    fake = FakeSlackClient({"C1": ([main], {})})
    fake.resolve_user_token_ids = lambda token: {"U999BOT", "B999BOT", "A999APP"}
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)

    candidates, stats = pr_scan.scan(
        _slack_cfg(channels=("C1",)) | {"filter_mentioned_users": ["@Sujeet's Bot"]},
        oldest_ts="0",
        log=logging.getLogger("test"),
    )

    assert len(candidates) == 1
    assert stats["filtered_out_user"] == 0


def test_find_supporting_docs_excludes_pr_urls():
    text = ("https://github.com/acme/foo/pull/1 "
            "https://acme.atlassian.net/wiki/x "
            "https://docs.google.com/document/d/abc/edit")
    docs = pr_scan.find_supporting_docs(text)
    assert "https://github.com/acme/foo/pull/1" not in docs
    assert any("atlassian" in d for d in docs)
    assert any("docs.google.com" in d for d in docs)


# ----- cheap_pr_meta: Bitbucket abbreviated-SHA resolution -------------------

def test_cheap_pr_meta_bitbucket_resolves_short_sha(monkeypatch):
    """Bitbucket Cloud's pullrequests endpoint returns a 12-char SHA in
    source.commit.hash. cheap_pr_meta() must follow up with the /commit
    endpoint to get the full 40-char value; otherwise create_worktree.py's
    `git fetch origin <short>` fails with 'couldn't find remote ref'."""
    monkeypatch.setenv("BITBUCKET_TOKEN_CRED", "fake")
    monkeypatch.setenv("BITBUCKET_USERNAME", "fakeuser")

    short = "a2ab692a4db6"
    full = "a2ab692a4db6e961d7fa7e211e76d6f1d3b750f2"

    pr_body = {
        "source": {"commit": {"hash": short}},
        "destination": {"branch": {"name": "develop"}},
        "state": "OPEN",
        "links": {"html": {"href": "https://bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5597"}},
        "author": {"display_name": "Jane"},
    }
    commit_body = {"hash": full}

    class FakeResp:
        def __init__(self, body):
            self._body = body
        def raise_for_status(self): pass
        def json(self): return self._body

    calls: list[str] = []
    def fake_get(url, **kwargs):
        calls.append(url)
        if "/pullrequests/" in url:
            return FakeResp(pr_body)
        if "/commit/" in url:
            return FakeResp(commit_body)
        raise AssertionError(f"unexpected URL: {url}")

    import requests
    monkeypatch.setattr(requests, "get", fake_get)
    log = logging.getLogger("test")

    out = pr_scan.cheap_pr_meta(
        "https://bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5597", log
    )
    assert out["head_sha"] == full, out
    # Both endpoints must have been hit.
    assert any("/pullrequests/" in u for u in calls), calls
    assert any("/commit/" in u for u in calls), calls


def test_cheap_pr_meta_bitbucket_keeps_short_on_resolve_failure(monkeypatch):
    """If the /commit endpoint fails, keep the abbreviated value rather than
    silently dropping head_sha. create_worktree.py's error message points
    the user at the right diagnostic."""
    monkeypatch.setenv("BITBUCKET_TOKEN_CRED", "fake")
    monkeypatch.setenv("BITBUCKET_USERNAME", "fakeuser")

    short = "a2ab692a4db6"
    pr_body = {
        "source": {"commit": {"hash": short}},
        "destination": {"branch": {"name": "develop"}},
        "state": "OPEN",
        "links": {"html": {"href": "https://bitbucket.org/x/y/pull-requests/1"}},
        "author": {"display_name": "Jane"},
    }

    class FakeResp:
        def __init__(self, body, ok=True):
            self._body = body; self._ok = ok
        def raise_for_status(self):
            if not self._ok:
                raise RuntimeError("404 Not Found")
        def json(self): return self._body

    def fake_get(url, **kwargs):
        if "/pullrequests/" in url:
            return FakeResp(pr_body)
        if "/commit/" in url:
            return FakeResp({}, ok=False)
        raise AssertionError(f"unexpected URL: {url}")

    import requests
    monkeypatch.setattr(requests, "get", fake_get)
    log = logging.getLogger("test")
    out = pr_scan.cheap_pr_meta("https://bitbucket.org/x/y/pull-requests/1", log)
    # Falls back to the abbreviation instead of None — the queue still has a value,
    # and create_worktree.py's enhanced error explains the situation.
    assert out["head_sha"] == short


# ----- thread_pr_count: thread-wide PR detection -----------------------------

def test_thread_pr_count_single_pr_in_main_only(monkeypatch):
    """Main message has 1 PR, no replies with PRs → thread_pr_count = 1.
    This is the only case where a slack reaction is safe.
    """
    fake = FakeSlackClient({
        "C1": (
            [{
                "ts": "100.000", "user": "U_alice",
                "text": "Review https://github.com/acme/foo/pull/1",
                "reply_count": 0,
            }],
            {},
        )
    })
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, _ = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)
    assert len(candidates) == 1
    assert candidates[0]["slack"]["thread_pr_count"] == 1
    assert candidates[0]["slack"]["n_pr_links_in_message"] == 1


def test_thread_pr_count_sums_main_and_replies(monkeypatch):
    """Main message has 1 PR, replies add 2 more → thread_pr_count = 3 on
    every row, including the main one. (The MAIN row had only 1 in its own
    message, but the thread total is what gates the reaction.)
    """
    main = {"ts": "100.000", "user": "U_alice",
            "text": "Initial https://github.com/acme/foo/pull/1",
            "reply_count": 2}
    r1 = {"ts": "100.001", "user": "U_bob",
          "text": "Spinoff https://github.com/acme/foo/pull/2"}
    r2 = {"ts": "100.002", "user": "U_carol",
          "text": "Another https://github.com/acme/foo/pull/3"}
    fake = FakeSlackClient({"C1": ([main], {"100.000": [main, r1, r2]})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, _ = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)
    assert len(candidates) == 3
    # Every row carries the SAME thread total.
    for c in candidates:
        assert c["slack"]["thread_pr_count"] == 3
    # But per-message counts still reflect the local message:
    by_link = {c["pr_url"]: c for c in candidates}
    assert by_link["https://github.com/acme/foo/pull/1"]["slack"]["n_pr_links_in_message"] == 1
    assert by_link["https://github.com/acme/foo/pull/2"]["slack"]["n_pr_links_in_message"] == 1


def test_thread_pr_count_two_prs_in_one_message(monkeypatch):
    """Main message has 2 PRs, no replies → thread_pr_count = 2 (not 1) →
    reactions are NOT safe; each row should get a reply with the PR link."""
    fake = FakeSlackClient({
        "C1": (
            [{"ts": "100.000", "user": "U_alice",
              "text": ("Please review https://github.com/acme/foo/pull/1 and "
                       "https://github.com/acme/foo/pull/2"),
              "reply_count": 0}],
            {},
        )
    })
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, _ = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)
    assert len(candidates) == 2
    for c in candidates:
        assert c["slack"]["thread_pr_count"] == 2
        assert c["slack"]["n_pr_links_in_message"] == 2


def test_post_process_skips_reaction_when_thread_has_multi_pr(monkeypatch):
    """post_process must NOT add a merged-emoji reaction to the main message
    when thread_pr_count > 1 — even when the PR itself is merged. The
    reaction would mis-attribute a verdict in a multi-PR thread."""
    reactions: list[tuple[str, str, str]] = []

    class FakeSlackC:
        def add_reaction(self, channel_id, message_ts, name):
            reactions.append((channel_id, message_ts, name))
            return True
        def resolve_channel(self, n): return n

    monkeypatch.setattr(pr_scan, "SlackClient", lambda: FakeSlackC())

    def fake_meta(url, log):
        return {
            "host": "github", "owner": "acme", "repo": "foo",
            "pr_number": int(url.rsplit("/", 1)[1]),
            "head_sha": "deadbeef", "merged_at": "2026-01-01T00:00:00Z",
            "state": "MERGED",
        }
    monkeypatch.setattr(pr_scan, "cheap_pr_meta", fake_meta)

    candidates = [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "slack": {"channel_id": "C1", "message_ts": "100.000",
                   "thread_pr_count": 2, "n_pr_links_in_message": 1}},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "slack": {"channel_id": "C1", "message_ts": "100.001",
                   "thread_pr_count": 2, "n_pr_links_in_message": 1}},
    ]
    slack_cfg = {"status_emoji": {"merged": ":merged:"}}
    log = logging.getLogger("test")
    _, stats = pr_scan.post_process(candidates, slack_cfg, dry_run=False, log=log)

    assert reactions == [], reactions
    assert stats["merged_skipped"] == 2
    assert stats["merged_skipped_multi_pr"] == 2
    assert stats["merged_skipped_multi_pr_examples"] == ["gh:foo#1", "gh:foo#2"]


def test_post_process_reacts_when_thread_has_single_pr(monkeypatch):
    """The single-PR-thread case continues to react as before."""
    reactions: list[tuple[str, str, str]] = []

    class FakeSlackC:
        def add_reaction(self, channel_id, message_ts, name):
            reactions.append((channel_id, message_ts, name))
            return True
        def resolve_channel(self, n): return n

    monkeypatch.setattr(pr_scan, "SlackClient", lambda: FakeSlackC())

    def fake_meta(url, log):
        return {"host": "github", "owner": "acme", "repo": "foo",
                "pr_number": 1, "head_sha": "deadbeef",
                "merged_at": "2026-01-01T00:00:00Z", "state": "MERGED"}
    monkeypatch.setattr(pr_scan, "cheap_pr_meta", fake_meta)

    candidates = [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "slack": {"channel_id": "C1", "message_ts": "100.000",
                   "thread_pr_count": 1, "n_pr_links_in_message": 1}},
    ]
    slack_cfg = {"status_emoji": {"merged": ":merged:"}}
    log = logging.getLogger("test")
    _, stats = pr_scan.post_process(candidates, slack_cfg, dry_run=False, log=log)

    assert reactions == [("C1", "100.000", ":merged:")]
    assert stats["merged_reacted"] == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
