from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

from comment_activity import (
    normalize_comment_activity,
    fetch_unresolved_comments,
    _extract_unresolved_github,
    _extract_unresolved_bitbucket,
)


def _bb_comment(cid, raw, *, parent=None, resolved=False, updated="2026-05-25T00:00:00Z"):
    out = {
        "id": cid,
        "updated_on": updated,
        "content": {"raw": raw},
        "user": {"display_name": "Author"},
        "resolved": resolved,
        "inline": {"path": "a.py", "to": 10},
    }
    if parent:
        out["parent"] = {"id": parent}
    return out


def test_ignores_new_bot_root_comment_noise():
    before = normalize_comment_activity("bitbucket", {"comments": []})
    after = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_")]
    })

    assert before["hash"] == after["hash"]


def test_author_reply_changes_hash():
    before = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_")]
    })
    after = normalize_comment_activity("bitbucket", {
        "comments": [
            _bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_"),
            _bb_comment(2, "Tracked in STRFRNT-123", parent=1),
        ]
    })

    assert before["hash"] != after["hash"]
    assert after["count"] == 1


def test_resolve_reopen_changes_hash_for_bot_root():
    unresolved = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_", resolved=False)]
    })
    resolved = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_", resolved=True)]
    })

    assert unresolved["hash"] != resolved["hash"]
    assert resolved["unresolved_count"] == 0


# ---------------------------------------------------------------------------
# Tests for fetch_unresolved_comments
# ---------------------------------------------------------------------------

def _gh_review_comment(cid, body, *, path="a.py", line=5, parent=None, deleted=False):
    c = {
        "id": cid,
        "body": body,
        "user": {"login": "alice"},
        "path": path,
        "line": line,
        "original_line": line,
        "updated_at": "2026-05-25T10:00:00Z",
    }
    if parent:
        c["in_reply_to_id"] = parent
    if deleted:
        c["deleted"] = True
    return c


def _gh_issue_comment(cid, body, *, deleted=False):
    c = {
        "id": cid,
        "body": body,
        "user": {"login": "bob"},
        "updated_at": "2026-05-25T11:00:00Z",
    }
    if deleted:
        c["deleted"] = True
    return c


def _bb_open(cid, body, *, parent=None, resolved=False):
    out = {
        "id": cid,
        "content": {"raw": body},
        "user": {"display_name": "Caro"},
        "updated_on": "2026-05-25T12:00:00Z",
        "resolved": resolved,
        "inline": {"path": "b.py", "to": 20},
    }
    if parent:
        out["parent"] = {"id": parent}
    return out


class TestExtractUnresolvedGithub:
    def test_returns_review_comment_with_body(self):
        blob = {"review_comments": [_gh_review_comment(1, "Please fix")], "issue_comments": []}
        items = _extract_unresolved_github(blob)
        assert len(items) == 1
        assert items[0]["body"] == "Please fix"
        assert items[0]["author"] == "alice"
        assert items[0]["path"] == "a.py"
        assert items[0]["line"] == 5

    def test_excludes_deleted_review_comment(self):
        blob = {
            "review_comments": [_gh_review_comment(1, "Old", deleted=True)],
            "issue_comments": [],
        }
        items = _extract_unresolved_github(blob)
        assert items == []

    def test_includes_issue_comment(self):
        blob = {
            "review_comments": [],
            "issue_comments": [_gh_issue_comment(10, "LGTM overall")],
        }
        items = _extract_unresolved_github(blob)
        assert len(items) == 1
        assert items[0]["body"] == "LGTM overall"
        assert items[0]["path"] is None

    def test_excludes_bot_comments(self):
        blob = {
            "review_comments": [_gh_review_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_")],
            "issue_comments": [],
        }
        items = _extract_unresolved_github(blob)
        assert items == []

    def test_includes_reply_with_parent_id(self):
        blob = {
            "review_comments": [
                _gh_review_comment(1, "Root comment"),
                _gh_review_comment(2, "Reply text", parent=1),
            ],
            "issue_comments": [],
        }
        items = _extract_unresolved_github(blob)
        assert len(items) == 2
        reply = next(i for i in items if i["id"] == "2")
        assert reply["parent_id"] == "1"


class TestExtractUnresolvedBitbucket:
    def test_returns_open_comment_with_body(self):
        blob = {"comments": [_bb_open(1, "Needs refactor")]}
        items = _extract_unresolved_bitbucket(blob)
        assert len(items) == 1
        assert items[0]["body"] == "Needs refactor"
        assert items[0]["author"] == "Caro"

    def test_excludes_resolved_comment(self):
        blob = {"comments": [_bb_open(1, "Fixed?", resolved=True)]}
        items = _extract_unresolved_bitbucket(blob)
        assert items == []

    def test_excludes_deleted_comment(self):
        blob = {"comments": [
            {**_bb_open(1, "Gone"), "deleted": True}
        ]}
        items = _extract_unresolved_bitbucket(blob)
        assert items == []


class TestFetchUnresolvedComments:
    PR_URL_GH = "https://github.com/acme/foo/pull/1"
    PR_URL_BB = "https://bitbucket.org/team/foo/pull-requests/5"

    def test_github_returns_structured_result(self, monkeypatch):
        import comment_activity as _ca
        monkeypatch.setattr(_ca, "_fetch_github_comments", lambda *_: {
            "review_comments": [_gh_review_comment(42, "Check this")],
            "issue_comments": [],
        })
        result = fetch_unresolved_comments(self.PR_URL_GH)
        assert result["host"] == "github"
        assert result["count"] == 1
        assert result["items"][0]["body"] == "Check this"
        assert result["resolve_support"] == "github_graphql_only"
        assert "resolve_note" in result

    def test_bitbucket_returns_structured_result(self, monkeypatch):
        import comment_activity as _ca
        monkeypatch.setattr(_ca, "_fetch_bitbucket_comments", lambda *_: {
            "comments": [_bb_open(7, "Consider refactoring")],
        })
        result = fetch_unresolved_comments(self.PR_URL_BB)
        assert result["host"] == "bitbucket"
        assert result["count"] == 1
        assert result["items"][0]["body"] == "Consider refactoring"
        assert result["resolve_support"] == "bitbucket_api"

    def test_returns_error_on_fetch_failure(self, monkeypatch):
        import comment_activity as _ca
        monkeypatch.setattr(_ca, "_fetch_github_comments",
                            lambda *_: (_ for _ in ()).throw(RuntimeError("network error")))
        result = fetch_unresolved_comments(self.PR_URL_GH)
        assert "error" in result
        assert result["host"] == "github"

    def test_unsupported_host_returns_error(self):
        result = fetch_unresolved_comments("https://gitlab.com/acme/foo/-/merge_requests/1")
        assert "error" in result

    def test_resolved_bitbucket_comments_excluded(self, monkeypatch):
        import comment_activity as _ca
        monkeypatch.setattr(_ca, "_fetch_bitbucket_comments", lambda *_: {
            "comments": [
                _bb_open(1, "Open comment", resolved=False),
                _bb_open(2, "Already resolved", resolved=True),
            ],
        })
        result = fetch_unresolved_comments(self.PR_URL_BB)
        assert result["count"] == 1
        assert result["items"][0]["id"] == "1"
    before = normalize_comment_activity("bitbucket", {"comments": []})
    after = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_")]
    })

    assert before["hash"] == after["hash"]


def test_author_reply_changes_hash():
    before = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_")]
    })
    after = normalize_comment_activity("bitbucket", {
        "comments": [
            _bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_"),
            _bb_comment(2, "Tracked in STRFRNT-123", parent=1),
        ]
    })

    assert before["hash"] != after["hash"]
    assert after["count"] == 1


def test_resolve_reopen_changes_hash_for_bot_root():
    unresolved = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_", resolved=False)]
    })
    resolved = normalize_comment_activity("bitbucket", {
        "comments": [_bb_comment(1, "**Finding**\n\n_— adk-pr-review · f-001_", resolved=True)]
    })

    assert unresolved["hash"] != resolved["hash"]
    assert resolved["unresolved_count"] == 0
