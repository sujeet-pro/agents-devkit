"""Tests for queue_release._compute_new_status (the mapping that decides
whether a finished review puts the queue row into approved / comments / reviewed).
"""
from __future__ import annotations

import json
import logging
import sys
import types

import pytest

from queue_release import (
    _compute_new_status,
    _compute_slack_reaction_status,
    release_after_review,
    update_slack_reaction,
)
from queue_io import STATUS_APPROVED, STATUS_COMMENTS, STATUS_REVIEWED


def test_findings_make_it_comments_even_when_host_approved():
    """A reviewer who left N>0 comments alongside an approval ends in COMMENTS.
    This is the "approved with open comments" bucket in the ready-to-merge tail.
    """
    assert _compute_new_status(n_findings=3, approved_host=True, recommendation="approve") == STATUS_COMMENTS


def test_zero_findings_plus_host_approved_is_approved():
    """The "approved with no open comments" bucket — safe to merge."""
    assert _compute_new_status(n_findings=0, approved_host=True, recommendation="approve") == STATUS_APPROVED


def test_recommendation_approve_alone_qualifies():
    """No host-side approval yet (CI hasn't seen the review post yet),
    but the review itself recommended approve → still approved."""
    assert _compute_new_status(n_findings=0, approved_host=False, recommendation="approve") == STATUS_APPROVED


def test_no_findings_and_no_approval_is_reviewed():
    """Reviewed but not yet approved (e.g. comment_only recommendation)."""
    assert _compute_new_status(n_findings=0, approved_host=False, recommendation="comment_only") == STATUS_REVIEWED


def test_findings_take_precedence_over_no_approval():
    """The presence of findings always pins the row into COMMENTS — the row needs
    attention from either the author or the reviewer."""
    assert _compute_new_status(n_findings=2, approved_host=False, recommendation="request_changes") == STATUS_COMMENTS


def test_slack_reaction_status_shows_approved_for_approved_with_comments():
    """Queue keeps COMMENTS, but Slack readers should see the host approval."""
    assert _compute_slack_reaction_status(
        STATUS_COMMENTS,
        approved_host=True,
        recommendation="approve",
        approve_ready=True,
        host_requested_changes=False,
    ) == STATUS_APPROVED


def test_slack_reaction_status_uses_comments_until_host_request_changes_exists():
    assert _compute_slack_reaction_status(
        STATUS_COMMENTS,
        approved_host=False,
        recommendation="request_changes",
        approve_ready=False,
        host_requested_changes=False,
    ) == STATUS_COMMENTS


def test_slack_reaction_status_uses_request_changes_when_host_says_so():
    assert _compute_slack_reaction_status(
        STATUS_COMMENTS,
        approved_host=False,
        recommendation="request_changes",
        approve_ready=False,
        host_requested_changes=True,
    ) == "request_changes"


def test_multi_pr_reaction_update_sweeps_status_reactions(monkeypatch):
    """Multi-PR threads should have no per-status reactions left behind."""
    import sys
    import types

    removed: list[tuple[str, str, str]] = []
    added: list[tuple[str, str, str]] = []

    class FakeSlackClient:
        def remove_reaction(self, channel_id, message_ts, emoji):
            removed.append((channel_id, message_ts, emoji))
            return True

        def add_reaction(self, channel_id, message_ts, emoji):
            added.append((channel_id, message_ts, emoji))
            return True

    monkeypatch.setitem(
        sys.modules,
        "slack_helpers",
        types.SimpleNamespace(SlackClient=FakeSlackClient),
    )

    info = update_slack_reaction(
        {
            "channel_id": "C1",
            "message_ts": "100.000",
            "thread_pr_count": 2,
            "last_reaction_status": "comments",
        },
        STATUS_APPROVED,
        {
            "status_emoji": {
                "approved": "white_check_mark",
                "comments": "speech_balloon",
                "request_changes": "octagonal_sign",
            },
        },
    )

    assert added == []
    assert sorted(emoji for _, _, emoji in removed) == [
        "octagonal_sign",
        "speech_balloon",
        "white_check_mark",
    ]
    assert info["last_reaction_status"] is None


def test_release_after_review_posts_reply_to_every_slack_thread(tmp_path, monkeypatch):
    posted: list[tuple[str, str, str]] = []

    class FakeSlackClient:
        pass

    def render_review_reply(**kwargs):
        return f"review reply for {kwargs['pr_url']}"

    def post_review_slack_reply(client, *, channel_id, thread_ts, text, log=None):
        posted.append((channel_id, thread_ts, text))
        return f"{channel_id}-{thread_ts}-reply"

    monkeypatch.setitem(
        sys.modules,
        "slack_helpers",
        types.SimpleNamespace(
            SlackClient=FakeSlackClient,
            render_review_reply=render_review_reply,
            post_review_slack_reply=post_review_slack_reply,
        ),
    )

    pr_url = "https://github.com/acme/foo/pull/1"
    threads = [
        {"channel_id": "C1", "thread_ts": "100.000", "message_ts": "100.000"},
        {"channel_id": "C2", "thread_ts": "200.000", "message_ts": "200.000"},
    ]
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text(json.dumps({"prs": [{
        "pr_url": pr_url,
        "status": "pending",
        "slack": threads[0],
        "slack_threads": threads,
    }]}), encoding="utf-8")

    status = release_after_review(
        queue_path=queue_path,
        pr_url=pr_url,
        head_sha="abc123",
        n_findings=1,
        approved_host=False,
        recommendation="request_changes",
        slack_cfg={"status_emoji": {}},
        pr={"host": "github", "owner": "acme", "repo": "foo",
            "pr_number": 1, "url": pr_url, "head_sha": "abc123"},
        log=logging.getLogger("test"),
    )

    assert status == STATUS_COMMENTS
    assert [(c, t) for c, t, _ in posted] == [("C1", "100.000"), ("C2", "200.000")]
    persisted = json.loads(queue_path.read_text())["prs"][0]
    assert persisted["slack"] == persisted["slack_threads"][0]
    assert [t["slack_reply_ts"] for t in persisted["slack_threads"]] == [
        "C1-100.000-reply",
        "C2-200.000-reply",
    ]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
