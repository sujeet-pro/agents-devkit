"""Tests for general-comment support in comment_resolver + post_comments.

Covers:
  - _extract_general_comments (GitHub issue_comments and Bitbucket non-inline)
  - scan_general_comments_for_signals (acceptable-reply patterns)
  - verify_action using general_signals when no direct-reply signal exists
  - _auto_classify_thread using general_signals
  - build_posting_plan emitting resolve_pre_reply step before the resolve step
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import comment_resolver  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inline_thread(*, resolved=False, path="app.py", line=42, reply: str | None = None):
    items = [
        {"id": "10", "path": path, "line": line, "body": "original reviewer comment",
         "resolved": resolved, "parent_id": None},
    ]
    if reply:
        items.append({"id": "11", "path": None, "line": None, "body": reply,
                      "resolved": False, "parent_id": "10"})
    return {"root_id": "10", "thread": items, "resolved": resolved}


# ---------------------------------------------------------------------------
# _extract_general_comments
# ---------------------------------------------------------------------------

class TestExtractGeneralComments:
    def test_github_extracts_issue_comments(self):
        blob = {
            "review_comments": [{"id": 1, "body": "inline", "path": "f.py", "line": 5,
                                  "user": {"login": "alice"}}],
            "issue_comments": [{"id": 2, "body": "general here", "user": {"login": "bob"}}],
        }
        result = comment_resolver._extract_general_comments(blob, "github")
        assert len(result) == 1
        assert result[0]["id"] == "2"
        assert result[0]["body"] == "general here"
        assert result[0]["user"] == "bob"
        assert result[0]["parent_id"] is None

    def test_github_empty_issue_comments(self):
        blob = {"review_comments": [], "issue_comments": []}
        assert comment_resolver._extract_general_comments(blob, "github") == []

    def test_bitbucket_extracts_non_inline(self):
        blob = {
            "comments": [
                {"id": 1, "content": {"raw": "inline comment"},
                 "user": {"display_name": "alice"},
                 "inline": {"path": "app.py", "to": 10}},
                {"id": 2, "content": {"raw": "general comment"},
                 "user": {"display_name": "bob"},
                 "inline": {}},
                {"id": 3, "content": {"raw": "no inline at all"},
                 "user": {"display_name": "carol"}},
            ]
        }
        result = comment_resolver._extract_general_comments(blob, "bitbucket")
        ids = {r["id"] for r in result}
        assert "2" in ids
        assert "3" in ids
        assert "1" not in ids

    def test_bitbucket_captures_parent_id(self):
        blob = {
            "comments": [
                {"id": 5, "content": {"raw": "reply"},
                 "user": {"display_name": "dave"},
                 "parent": {"id": 4}},
            ]
        }
        result = comment_resolver._extract_general_comments(blob, "bitbucket")
        assert result[0]["parent_id"] == "4"

    def test_unknown_host_returns_empty(self):
        blob = {"comments": [{"id": 1, "content": {"raw": "x"}}]}
        assert comment_resolver._extract_general_comments(blob, "gitlab") == []


# ---------------------------------------------------------------------------
# scan_general_comments_for_signals
# ---------------------------------------------------------------------------

class TestScanGeneralCommentsForSignals:
    def _make(self, body, uid="gc1", user="alice"):
        return [{"id": uid, "body": body, "user": user}]

    def test_offline_marker_detected(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make("Agreed offline, will handle in a follow-up PR.")
        )
        assert len(sigs) == 1
        assert sigs[0]["kind"] == "offline"
        assert sigs[0]["id"] == "gc1"
        assert sigs[0]["user"] == "alice"

    def test_jira_tracking_detected(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make("Tracked all remaining review comments in PROJ-9999.")
        )
        assert len(sigs) == 1
        assert sigs[0]["kind"] == "jira"
        assert sigs[0]["detail"] == "PROJ-9999"

    def test_synced_with_handle_detected(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make("Synced with @bob on all open threads — keeping as-is.")
        )
        assert len(sigs) == 1
        assert sigs[0]["kind"] == "synced"

    def test_no_signal_in_unrelated_comment(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make("Thanks for the review! Merging now.")
        )
        assert sigs == []

    def test_empty_body_skipped(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            [{"id": "x", "body": "   ", "user": "alice"}]
        )
        assert sigs == []

    def test_negation_blocks_signal(self):
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make("Agreed offline, but only if tests pass.")
        )
        assert sigs == []

    def test_body_snippet_truncated_to_160(self):
        long_body = "Agreed offline, will skip for now. " + "x" * 200
        sigs = comment_resolver.scan_general_comments_for_signals(
            self._make(long_body)
        )
        assert len(sigs[0]["body_snippet"]) <= 160


# ---------------------------------------------------------------------------
# verify_action with general_signals
# ---------------------------------------------------------------------------

class TestVerifyActionWithGeneralSignals:
    def _threads(self):
        return {"10": _inline_thread()}

    def _sig(self, kind="offline"):
        return [{
            "id": "gc1", "user": "alice",
            "body_snippet": "Agreed offline, handling in follow-up PR.",
            "kind": kind, "detail": "Agreed offline",
        }]

    def test_general_signal_resolves_open_thread(self):
        out = comment_resolver.verify_action(
            {"comment_id": "10", "decision": "leave-as-is"},
            self._threads(),
            {},
            log=None,
            deleted=set(),
            general_signals=self._sig("offline"),
        )
        assert out["decision"] == "resolve"
        assert out["resolved_via_general_comment"] is True
        assert out["general_comment_id"] == "gc1"
        assert out["general_comment_user"] == "alice"
        assert "Agreed offline" in out["general_comment_snippet"]
        assert out["verified"] is True

    def test_general_signal_not_applied_when_thread_already_resolved(self):
        threads = {"10": _inline_thread(resolved=True)}
        out = comment_resolver.verify_action(
            {"comment_id": "10", "decision": "leave-as-is"},
            threads,
            {},
            log=None,
            deleted=set(),
            general_signals=self._sig("offline"),
        )
        # Thread is already resolved — general signal is moot; leave-as-is.
        assert out["decision"] == "leave-as-is"
        assert not out.get("resolved_via_general_comment")

    def test_direct_reply_takes_precedence_over_general_signal(self):
        # Thread has its own direct acceptable reply (jira).
        threads = {"10": _inline_thread(reply="Tracked in PROJ-42")}
        out = comment_resolver.verify_action(
            {"comment_id": "10", "decision": "leave-as-is"},
            threads,
            {},
            log=None,
            deleted=set(),
            general_signals=self._sig("offline"),
        )
        assert out["decision"] == "resolve"
        assert not out.get("resolved_via_general_comment")
        assert out["valid_reply"]["kind"] == "jira"

    def test_no_general_signal_leaves_open_thread(self):
        out = comment_resolver.verify_action(
            {"comment_id": "10", "decision": "leave-as-is"},
            self._threads(),
            {},
            log=None,
            deleted=set(),
            general_signals=[],
        )
        assert out["decision"] == "leave-as-is"


# ---------------------------------------------------------------------------
# _auto_classify_thread with general_signals
# ---------------------------------------------------------------------------

class TestAutoClassifyThreadWithGeneralSignals:
    def _sig(self):
        return [{
            "id": "gc2", "user": "carol",
            "body_snippet": "Synced with @bob on all comments.",
            "kind": "synced", "detail": "bob",
        }]

    def test_general_signal_resolves_open_orphan_thread(self):
        t = _inline_thread()
        out = comment_resolver._auto_classify_thread(t, {}, deleted=set(),
                                                      general_signals=self._sig())
        assert out["decision"] == "resolve"
        assert out["resolved_via_general_comment"] is True
        assert out["general_comment_id"] == "gc2"
        assert "gc2" in out["reason"]

    def test_general_signal_not_applied_when_diff_touches_anchor(self):
        # Diff already resolves it — no need to credit the general comment.
        t = _inline_thread()
        touched = {"app.py": [(40, 45)]}
        out = comment_resolver._auto_classify_thread(t, touched, deleted=set(),
                                                      general_signals=self._sig())
        assert out["decision"] == "resolve"
        # Could be either diff-based or general; what matters is it resolves.
        assert out["verified"] is True

    def test_general_signal_not_applied_when_already_resolved(self):
        t = _inline_thread(resolved=True)
        out = comment_resolver._auto_classify_thread(t, {}, deleted=set(),
                                                      general_signals=self._sig())
        # Resolved thread with no diff → reopen (no diff to justify resolution).
        assert out["decision"] == "reopen"
        assert not out.get("resolved_via_general_comment")

    def test_no_general_signal_ambiguous(self):
        t = _inline_thread()
        out = comment_resolver._auto_classify_thread(t, {}, deleted=set(),
                                                      general_signals=[])
        assert out["decision"] == "leave-as-is"


# ---------------------------------------------------------------------------
# build_posting_plan — resolve_pre_reply step
# ---------------------------------------------------------------------------

class TestBuildPostingPlanPreReply:
    """Verify that build_posting_plan inserts a resolve_pre_reply step before
    a resolve step when the action was driven by a general comment."""

    def _pr(self, host="github"):
        return {
            "host": host, "owner": "acme", "repo": "web", "pr_number": 7,
            "head_sha": "abc123", "url": "https://github.com/acme/web/pull/7",
        }

    def _findings_blob(self):
        return {"findings": [], "recommendation": "comment_only", "summary": ""}

    def _action_via_general(self):
        return {
            "comment_id": "10",
            "decision": "resolve",
            "verified": True,
            "resolved_via_general_comment": True,
            "general_comment_id": "gc1",
            "general_comment_user": "alice",
            "general_comment_snippet": "Agreed offline, will handle in follow-up.",
            "general_comment_signal_kind": "offline",
            "verifier_evidence": "diff touched app.py:42",
            "reason": "general-comment signal",
        }

    def _action_normal(self):
        return {
            "comment_id": "20",
            "decision": "resolve",
            "verified": True,
            "reason": "diff touched file.py:10",
        }

    def _import_post_comments(self):
        import importlib.util
        path = SCRIPTS_DIR.parent / "scripts" / "post_comments.py"
        spec = importlib.util.spec_from_file_location("post_comments_under_test", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_resolve_pre_reply_inserted_before_resolve_for_general_comment(self):
        pc = self._import_post_comments()
        plan = pc.build_posting_plan(
            pr=self._pr("github"),
            findings_blob=self._findings_blob(),
            actions=[self._action_via_general()],
            no_resolve_existing=False,
            approve_ready=False,
            slack_summary_enabled=False,
            queue_ctx=None,
        )
        kinds = [s["kind"] for s in plan["steps"]]
        assert "resolve_pre_reply" in kinds
        assert "resolve" in kinds
        pre_idx = kinds.index("resolve_pre_reply")
        res_idx = kinds.index("resolve")
        assert pre_idx < res_idx, "pre_reply must come before resolve"

    def test_resolve_pre_reply_body_contains_attribution(self):
        pc = self._import_post_comments()
        plan = pc.build_posting_plan(
            pr=self._pr("github"),
            findings_blob=self._findings_blob(),
            actions=[self._action_via_general()],
            no_resolve_existing=False,
            approve_ready=False,
            slack_summary_enabled=False,
            queue_ctx=None,
        )
        pre = next(s for s in plan["steps"] if s["kind"] == "resolve_pre_reply")
        body = pre["mcp_args"]["body"]
        assert "@alice" in body
        assert "Agreed offline" in body
        assert "general" in body.lower()

    def test_normal_resolve_has_no_pre_reply(self):
        pc = self._import_post_comments()
        plan = pc.build_posting_plan(
            pr=self._pr("github"),
            findings_blob=self._findings_blob(),
            actions=[self._action_normal()],
            no_resolve_existing=False,
            approve_ready=False,
            slack_summary_enabled=False,
            queue_ctx=None,
        )
        kinds = [s["kind"] for s in plan["steps"]]
        assert "resolve_pre_reply" not in kinds
        assert "resolve" in kinds

    def test_resolve_pre_reply_bitbucket_uses_parent_id(self):
        pc = self._import_post_comments()
        plan = pc.build_posting_plan(
            pr=self._pr("bitbucket"),
            findings_blob=self._findings_blob(),
            actions=[self._action_via_general()],
            no_resolve_existing=False,
            approve_ready=False,
            slack_summary_enabled=False,
            queue_ctx=None,
        )
        pre = next(s for s in plan["steps"] if s["kind"] == "resolve_pre_reply")
        assert pre["mcp_args"]["parent_id"] == "10"

    def test_no_resolve_existing_suppresses_pre_reply(self):
        pc = self._import_post_comments()
        plan = pc.build_posting_plan(
            pr=self._pr("github"),
            findings_blob=self._findings_blob(),
            actions=[self._action_via_general()],
            no_resolve_existing=True,
            approve_ready=False,
            slack_summary_enabled=False,
            queue_ctx=None,
        )
        kinds = [s["kind"] for s in plan["steps"]]
        assert "resolve_pre_reply" not in kinds
        assert "resolve" not in kinds


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
