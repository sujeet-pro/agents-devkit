"""Tests for pr_scan.scan() — focused on thread-reply PR-link extraction."""
from __future__ import annotations

import json
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


def test_gentle_reminder_count_matches_unique_prs_not_occurrences(monkeypatch):
    """Regression for the bug Sujeet hit on 2026-05-26:

    A thread had 2 unique PRs mentioned across main + 2 replies (6 total
    occurrences). The Heads-up text said "I see 6 PRs in this message" when it
    should have said "2" — the count of unique PRs in the THREAD.

    Each candidate row already carries the correct unique count in
    `slack.thread_pr_count` (fix fc10d03). The reminder text just needs to read
    it instead of `len(rows)`.
    """
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    # 6 candidate rows for 2 unique PRs in the same thread.
    # Titles + branches must be clearly UNRELATED so `_looks_related` doesn't
    # short-circuit the reminder — that path has its own test below.
    per_pr = {
        1: {"title": "FAQ widget rollout", "source_branch": "faq-widget"},
        2: {"title": "Best-sellers homepage carousel",
            "source_branch": "homepage-carousel"},
    }
    rows = []
    for occurrence_ts, pr_n in [
        ("100.000", 1), ("100.000", 2),  # main message mentions both
        ("100.001", 1), ("100.001", 2),  # reply 1 re-links both
        ("100.002", 1), ("100.002", 2),  # reply 2 re-links both
    ]:
        rows.append({
            "pr_url": f"https://github.com/acme/foo/pull/{pr_n}",
            "slack": {
                "channel_id": "C1", "thread_ts": "100.000",
                "thread_pr_count": 2,
            },
            "_meta": {"repo": "foo", **per_pr[pr_n]},
        })

    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False,
        logging.getLogger("test"),
    )

    assert stats["posted"] == 1
    assert len(fake.thread_replies) == 1
    _, _, text = fake.thread_replies[0]
    assert "I see 2 PRs" in text, (
        f"Heads-up text must use the unique PR count (2), "
        f"not the raw occurrence count (6). Got: {text!r}"
    )
    assert "6 PRs" not in text


def test_gentle_reminder_skips_when_meta_marks_prs_related_after_pop(monkeypatch):
    """Regression: main() pops `_meta` from every kept candidate BEFORE
    maybe_emit_gentle_reminders runs. That made _looks_related see all-empty
    metas and never short-circuit. After the fix, related-PR detection must
    survive the pop — either by running before the pop, or by the reminder
    re-reading meta-equivalents off the row.

    Two PRs that share a branch (split PR) should not trigger a reminder.
    """
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    rows = [
        {
            "pr_url": "https://github.com/acme/foo/pull/1",
            "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
            # _meta has been popped by main(); _related_hint carries the
            # surviving fields the reminder needs to gauge relatedness.
            "_related_hint": {"repo": "foo", "title": "Add FAQ widget — backend",
                              "source_branch": "faq-widget"},
        },
        {
            "pr_url": "https://github.com/acme/foo/pull/2",
            "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
            "_related_hint": {"repo": "foo", "title": "Add FAQ widget — frontend",
                              "source_branch": "faq-widget"},
        },
    ]

    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False,
        logging.getLogger("test"),
    )
    assert stats["posted"] == 0
    assert stats["skipped_related"] == 1


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


def test_thread_pr_count_dedupes_same_pr_across_main_and_reply(monkeypatch):
    """A PR linked in BOTH the main message and a reply must count once in
    thread_pr_count. Regression for the bug where users saw 6 PRs in a thread
    with 4 link occurrences and 2 unique PRs."""
    main = {"ts": "100.000", "user": "U_alice",
            "text": "Please review https://github.com/acme/foo/pull/1 "
                    "and https://github.com/acme/foo/pull/2",
            "reply_count": 2}
    r1 = {"ts": "100.001", "user": "U_bob",
          "text": "+1 to https://github.com/acme/foo/pull/1"}  # same PR as main
    r2 = {"ts": "100.002", "user": "U_carol",
          "text": "And https://github.com/acme/foo/pull/2/files"}  # same PR, different shape
    fake = FakeSlackClient({"C1": ([main], {"100.000": [main, r1, r2]})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    log = logging.getLogger("test")
    candidates, _ = pr_scan.scan(_slack_cfg(), oldest_ts="0", log=log)
    for c in candidates:
        assert c["slack"]["thread_pr_count"] == 2, (
            f"4 link occurrences, 2 unique PRs → thread_pr_count must be 2, "
            f"got {c['slack']['thread_pr_count']}"
        )


def test_find_pr_urls_does_not_double_count_slack_label_form():
    """A Slack `<url|label>` form must yield exactly one URL, not two."""
    from slack_helpers import find_pr_urls
    text = "<https://github.com/acme/foo/pull/42|PR-42 (bugfix)>"
    urls = find_pr_urls(text, ["https://github.com/"])
    assert urls == ["https://github.com/acme/foo/pull/42"], urls


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


def test_post_process_single_pr_merged_no_reaction(monkeypatch):
    """Merged single-PR threads are dropped from the actionable set but no
    Slack reaction is added (reactions are dropped globally)."""
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
    kept, stats = pr_scan.post_process(candidates, slack_cfg, dry_run=False, log=log)

    assert reactions == [], "no reaction should be added even for single-PR merged threads"
    assert kept == []
    assert stats["merged_skipped"] == 1
    assert stats["merged_reacted"] == 0


# ----- _parse_since_seconds --------------------------------------------------

def test_parse_since_seconds_hours():
    assert pr_scan._parse_since_seconds("1h") == 3600.0


def test_parse_since_seconds_hours_alias():
    assert pr_scan._parse_since_seconds("30hr") == 30 * 3600.0


def test_parse_since_seconds_fractional_hours():
    assert pr_scan._parse_since_seconds("12h") == 12 * 3600.0


def test_parse_since_seconds_days():
    assert pr_scan._parse_since_seconds("30d") == 30 * 86400.0


def test_parse_since_seconds_weeks():
    assert pr_scan._parse_since_seconds("4w") == 4 * 7 * 86400.0


def test_parse_since_seconds_months():
    assert pr_scan._parse_since_seconds("1m") == 30 * 86400.0


def test_parse_since_seconds_case_insensitive():
    assert pr_scan._parse_since_seconds("12H") == 12 * 3600.0
    assert pr_scan._parse_since_seconds("7D") == 7 * 86400.0


def test_parse_since_seconds_invalid_raises():
    with pytest.raises(ValueError, match="unrecognised"):
        pr_scan._parse_since_seconds("badformat")

    with pytest.raises(ValueError, match="unrecognised"):
        pr_scan._parse_since_seconds("30x")


# ----- configured-repo filter (_filter_by_configured_repos) ------------------

def test_filter_drops_unknown_repo_when_registry_configured(monkeypatch):
    """Candidates for repos not in repos.json5 are dropped when the registry exists."""
    monkeypatch.setattr(pr_scan, "is_configured_repo",
                        lambda host, owner, repo: (host == "github" and repo == "allowed"))

    candidates = [
        {"pr_url": "https://github.com/acme/allowed/pull/1"},
        {"pr_url": "https://github.com/acme/other/pull/2"},
    ]
    log = logging.getLogger("test")
    kept, dropped = pr_scan._filter_by_configured_repos(candidates, log)

    assert len(kept) == 1
    assert kept[0]["pr_url"].endswith("/pull/1")
    assert dropped == 1


def test_filter_passes_all_when_registry_empty(monkeypatch):
    """When is_configured_repo returns True for everything (empty registry), nothing is dropped."""
    monkeypatch.setattr(pr_scan, "is_configured_repo", lambda host, owner, repo: True)

    candidates = [
        {"pr_url": "https://github.com/acme/foo/pull/1"},
        {"pr_url": "https://github.com/acme/bar/pull/2"},
    ]
    log = logging.getLogger("test")
    kept, dropped = pr_scan._filter_by_configured_repos(candidates, log)

    assert len(kept) == 2
    assert dropped == 0


# ----- scan_direct_review_requests -------------------------------------------

def test_scan_direct_gh_pr_shows_up_with_direct_link_origin(tmp_path, monkeypatch):
    """When GH returns a PR for a configured repo, scan_direct_review_requests
    returns a candidate with link_origin='direct' and discovery_source='direct'.
    """
    gh_response = json.dumps({
        "items": [
            {
                "html_url": "https://github.com/acme/foo/pull/42",
                "pull_request": {"html_url": "https://github.com/acme/foo/pull/42"},
            }
        ]
    })

    def fake_run(cmd, **kwargs):
        class FakeCP:
            returncode = 0
            stdout = gh_response
            stderr = ""
        return FakeCP()

    monkeypatch.setattr(pr_scan.subprocess, "run", fake_run)

    # Write a minimal v5 config bundle with the acme/foo github repo.
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "core.json5").write_text(json.dumps({
        "schema_version": 5,
        "user": {"email": "t@e.com", "first_name": "T"},
        "org": {"name": "acme", "primary_workspace": "w"},
        "bot": {"icon_emoji": ":robot:"},
        "defaults": {},
    }), encoding="utf-8")
    (cfg_dir / "workspaces.json5").write_text(json.dumps({
        "workspaces": [{
            "id": "workspace:w", "name": "W", "role": "work",
            "github_org": "acme", "workspace_root": "/tmp",
        }],
    }), encoding="utf-8")
    (cfg_dir / "teams.json5").write_text(json.dumps({
        "teams": [{"id": "team:t", "name": "T"}],
    }), encoding="utf-8")
    (cfg_dir / "repos.json5").write_text(json.dumps({
        "repos": [{
            "id": "repo:foo", "host": "github", "org": "acme", "name": "foo",
            "workspace": "workspace:w", "team": "team:t", "path": "/tmp/foo",
            "primary_language": "ts", "base_branch": "main",
        }],
    }), encoding="utf-8")

    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()

    log = logging.getLogger("test")
    candidates = pr_scan.scan_direct_review_requests(log)

    assert len(candidates) == 1
    c = candidates[0]
    assert c["pr_url"] == "https://github.com/acme/foo/pull/42"
    assert c["link_origin"] == "direct"
    assert c["discovery_source"] == "direct"


def test_scan_direct_skips_bitbucket_with_warning(tmp_path, monkeypatch):
    """Bitbucket repos log a warning and produce no candidates."""
    import json as _json

    # Write a minimal v5 bundle with a single Bitbucket repo.
    cfg = tmp_path / "config"
    cfg.mkdir(parents=True)
    (cfg / "core.json5").write_text(_json.dumps({
        "schema_version": 5,
        "user": {"email": "t@e.com", "first_name": "T"},
        "org": {"name": "acme", "primary_workspace": "w"},
        "bot": {"icon_emoji": ":r:"},
        "defaults": {},
    }))
    (cfg / "workspaces.json5").write_text(_json.dumps({
        "workspaces": [{
            "id": "workspace:w", "name": "W", "role": "work",
            "bitbucket_workspace": "myws", "workspace_root": "/tmp",
        }],
    }))
    (cfg / "teams.json5").write_text(_json.dumps({
        "teams": [{"id": "team:t", "name": "T"}],
    }))
    (cfg / "repos.json5").write_text(_json.dumps({
        "repos": [{
            "id": "repo:myrepo", "host": "bitbucket", "org": "myws", "name": "myrepo",
            "workspace": "workspace:w", "team": "team:t", "path": "/tmp/myrepo",
            "primary_language": "ts", "base_branch": "main",
        }],
    }))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg))
    from config import reset_bundle  # type: ignore
    reset_bundle()

    log = logging.getLogger("test")
    candidates = pr_scan.scan_direct_review_requests(log)
    assert candidates == []


# ----- Bug 1: terminal-PR filter (post_process) ------------------------------

def test_post_process_drops_declined_pr_not_just_merged(monkeypatch):
    """DECLINED bitbucket PRs (and CLOSED/SUPERSEDED) must be filtered out of
    candidates exactly like MERGED PRs. Before, only merged_at was checked,
    leaving declined PRs in the candidate set — and feeding stale rows into
    `maybe_emit_gentle_reminders` weeks after the thread was done.
    """
    def fake_meta(url, log):
        # DECLINED: state set, no merged_at. Real Bitbucket case (PR #5310).
        return {"host": "bitbucket", "owner": "acme", "repo": "foo",
                "pr_number": int(url.rsplit("/", 1)[1]), "head_sha": "deadbeef",
                "merged_at": None, "state": "DECLINED"}
    monkeypatch.setattr(pr_scan, "cheap_pr_meta", fake_meta)

    candidates = [{
        "pr_url": "https://bitbucket.org/acme/foo/pull-requests/5310",
        "slack": {"channel_id": "C1", "message_ts": "100.000",
                  "thread_pr_count": 2, "n_pr_links_in_message": 1},
    }]
    log = logging.getLogger("test")
    kept, stats = pr_scan.post_process(candidates, {}, dry_run=False, log=log)
    assert kept == []
    assert stats["closed_skipped"] == 1
    assert stats["closed_skipped_multi_pr"] == 1
    assert stats["merged_skipped"] == 0  # merged counter untouched
    assert stats["closed_skipped_multi_pr_examples"] == ["bb:foo#5310"]


# ----- Bug 2/3: count drift after filter (gate on len(unique_rows)) ----------

def test_gentle_reminder_skips_when_only_one_unique_pr_after_filter(monkeypatch):
    """Stale `thread_pr_count` is no longer a gate. When only one unique PR
    survives the merged/declined filter, the heads-up post is suppressed —
    not silently posted with "I see 1 PRs" (the 2026-05-22 production bug).
    """
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    # Single surviving row, but the stale per-row thread_pr_count says 4 (the
    # pre-filter thread had 4 PRs; 3 merged/declined and only this one is left).
    rows = [{
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"channel_id": "C1", "thread_ts": "100.000",
                  "thread_pr_count": 4},
        "_meta": {"repo": "foo", "title": "FAQ", "source_branch": "faq"},
    }]
    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False,
        logging.getLogger("test"),
    )
    assert stats["posted"] == 0
    assert stats["skipped_single_unique"] == 1
    assert fake.thread_replies == []


# ----- Bug 4: persistent thread-mark sidecar ---------------------------------

def test_gentle_reminder_dedupes_via_thread_marks_sidecar(monkeypatch, tmp_path):
    """When the queue has no row for a thread (e.g. every PR merged → GC'd),
    the per-thread mark in `pr-thread-marks.json` must still prevent reposting
    within the retention window.
    """
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    # Force the sidecar to a tmp path.
    import thread_marks as tm_mod
    sidecar = tmp_path / "pr-thread-marks.json"
    monkeypatch.setattr(pr_scan, "recent_thread_marks",
                        lambda within_hours=24.0: tm_mod.recent_thread_marks(
                            path=sidecar, within_hours=within_hours))
    monkeypatch.setattr(pr_scan, "record_thread_mark",
                        lambda channel_id, thread_ts, at_iso=None:
                        tm_mod.record_thread_mark(channel_id, thread_ts,
                                                  path=sidecar, at_iso=at_iso))

    # Pre-seed the sidecar with a recent mark for this thread.
    from datetime import datetime, timezone
    recent_iso = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")
    tm_mod.record_thread_mark("C1", "100.000", path=sidecar, at_iso=recent_iso)

    rows = [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
         "_meta": {"repo": "foo", "title": "FAQ", "source_branch": "faq"}},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
         "_meta": {"repo": "foo", "title": "Best", "source_branch": "best"}},
    ]
    # Empty queue — no row-level mark anywhere — yet we must still dedupe.
    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False,
        logging.getLogger("test"),
    )
    assert stats["posted"] == 0
    assert stats["skipped_existing"] == 1
    assert fake.thread_replies == []


def test_gentle_reminder_records_mark_in_sidecar_on_post(monkeypatch, tmp_path):
    """A successful heads-up post must write a mark to the sidecar so future
    scans can dedupe even after the queue row is GC'd.
    """
    fake = FakeSlackClient({"C1": ([], {})})
    monkeypatch.setattr(pr_scan, "SlackClient", lambda: fake)
    import thread_marks as tm_mod
    sidecar = tmp_path / "pr-thread-marks.json"
    monkeypatch.setattr(pr_scan, "recent_thread_marks",
                        lambda within_hours=24.0: tm_mod.recent_thread_marks(
                            path=sidecar, within_hours=within_hours))
    monkeypatch.setattr(pr_scan, "record_thread_mark",
                        lambda channel_id, thread_ts, at_iso=None:
                        tm_mod.record_thread_mark(channel_id, thread_ts,
                                                  path=sidecar, at_iso=at_iso))

    rows = [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
         "_meta": {"repo": "foo", "title": "FAQ widget", "source_branch": "faq"}},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "slack": {"channel_id": "C1", "thread_ts": "100.000", "thread_pr_count": 2},
         "_meta": {"repo": "foo", "title": "Best sellers", "source_branch": "best"}},
    ]
    stats = pr_scan.maybe_emit_gentle_reminders(
        rows, {"prs": []}, {"gentle_reminder_enabled": True}, False,
        logging.getLogger("test"),
    )
    assert stats["posted"] == 1
    # Sidecar now contains the mark.
    marks = tm_mod.recent_thread_marks(path=sidecar, within_hours=24.0)
    assert ("C1", "100.000") in marks


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
