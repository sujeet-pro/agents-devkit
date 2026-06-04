from __future__ import annotations

import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import comment_resolver


def _thread(*, resolved=False, reply: str | None = None, path="a.py"):
    items = [
        {"id": "1", "path": path, "line": 10, "body": "bot finding",
         "resolved": resolved, "parent_id": None},
    ]
    if reply:
        items.append({"id": "2", "path": None, "line": None, "body": reply,
                      "resolved": False, "parent_id": "1"})
    return {"root_id": "1", "thread": items, "resolved": resolved}


def test_acceptable_reply_resolves_open_thread():
    threads = {"1": _thread(reply="Tracked in STRFRNT-123")}
    out = comment_resolver.verify_action(
        {"comment_id": "1", "decision": "leave-as-is"},
        threads,
        {},
        log=None,
        deleted=set(),
    )

    assert out["verified"] is True
    assert out["decision"] == "resolve"
    assert out["valid_reply"]["kind"] == "jira"


def test_ambiguous_open_actionable_thread_blocks_approve_ready_shape():
    out = comment_resolver._auto_classify_thread(_thread(), {}, deleted=set())

    assert out["decision"] == "leave-as-is"
    assert out["actionable"] is True
    assert out["thread_currently_resolved"] is False


class TestFuturePrDeferralIsOffline:
    """"done in next PR" / "in a follow-up PR" defer the concern elsewhere."""

    @pytest.mark.parametrize("reply", [
        "it will be done in next pr",
        "will be done in the next PR",
        "this will be done in a later PR",
        "addressing in next pr",
        "to be handled in a separate patch",
        "we'll pick this up in a subsequent MR",
    ])
    def test_future_pr_phrasings_mark_offline(self, reply):
        assert comment_resolver.classify_reply(reply)[0] == "offline"

    @pytest.mark.parametrize("reply", [
        "I will fix this in this PR",            # staying in this PR, not deferring
        "pushing a fix in the next commit",      # fix incoming to the same PR
        "will this be done in the next PR?",     # a question — nothing decided
        "done in next PR, but only if tests pass",  # qualifier blocks it
    ])
    def test_non_deferrals_are_not_offline(self, reply):
        assert comment_resolver.classify_reply(reply)[0] is None

    def test_future_pr_reply_resolves_open_thread(self):
        threads = {"1": _thread(reply="No worries, this will be done in the next PR.")}
        out = comment_resolver.verify_action(
            {"comment_id": "1", "decision": "leave-as-is"},
            threads, {}, log=None, deleted=set(),
        )
        assert out["decision"] == "resolve"
        assert out["valid_reply"]["kind"] == "offline"


class TestSyncedWithNamedHuman:
    """"as discussed with <Name>" names an accountable human → synced."""

    @pytest.mark.parametrize("reply,expected", [
        ("as discussed with Sujeet", "Sujeet"),
        ("discussed with Sujeet, leaving as-is", "Sujeet"),
        ("synced with @bob on all threads", "bob"),
        ("as discussed with @sujeet", "sujeet"),
    ])
    def test_named_human_extracted(self, reply, expected):
        assert comment_resolver.extract_synced_with(reply) == expected

    @pytest.mark.parametrize("reply", [
        "as discussed with sujeet",          # bare lowercase — too risky to accept
        "discussed with the team",           # generic group
        "discussed with care here",          # not a person
        "talked with regard to performance",  # not a person
    ])
    def test_bare_lowercase_or_generic_rejected(self, reply):
        assert comment_resolver.extract_synced_with(reply) is None

    def test_named_human_resolves_open_thread(self):
        threads = {"1": _thread(reply="Leaving this as discussed with Sujeet.")}
        out = comment_resolver.verify_action(
            {"comment_id": "1", "decision": "leave-as-is"},
            threads, {}, log=None, deleted=set(),
        )
        assert out["decision"] == "resolve"
        assert out["valid_reply"] == {"kind": "synced", "detail": "Sujeet"}
