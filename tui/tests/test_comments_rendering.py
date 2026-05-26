"""Tests for the unified Comments view rendering.

Covers:
- Inline vs general tag prepended to each comment header.
- Short comment IDs displayed (`id:<last 8>`).
- Replies grouped under their root comment, indented with `↪`.
- GitHub `diff_hunk` rendered as a ```diff fenced block after inline comment bodies.
- All comments in the JSON appear in the rendered markdown — guards the
  "8 posted but only 1 visible" data bug from regressing.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def fake_pr_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect ADK_DATA_HOME to a tmp dir and return the PR's task_dir."""
    tmp = Path(tempfile.mkdtemp())
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(tmp / "config"))
    pr_dir = tmp / "skill-pr-review" / "foo_pr-42" / "pr-review"
    pr_dir.mkdir(parents=True, exist_ok=True)
    return pr_dir


class _Row:
    """Minimal QueueRow stand-in: only repo + number are used."""
    repo = "foo"
    number = 42


def _force_no_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADK_TUI_SKIP_IDENTITY", "1")


def test_all_comments_appear_in_rendered_markdown(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression guard for the '8 posted, 1 visible' bug — every comment in
    pr-comments.json must appear in the rendered markdown (the user can
    scroll to see them all)."""
    _force_no_identity(monkeypatch)
    comments = [
        {
            "id": 1000 + i,
            "user": {"login": f"user{i}"},
            "body": f"body of comment {i}",
            "created_at": f"2026-05-{20 + (i % 5):02d}T10:00:00Z",
        }
        for i in range(8)
    ]
    (fake_pr_dir / "pr-comments.json").write_text(
        json.dumps({"issue_comments": comments}), encoding="utf-8"
    )

    # Re-import to pick up the new ADK_DATA_HOME.
    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)

    out = dp._format_comments_markdown(_Row())
    for i in range(8):
        assert f"body of comment {i}" in out, f"comment {i} missing from rendered markdown"


def test_inline_comment_carries_inline_tag_and_path(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _force_no_identity(monkeypatch)
    (fake_pr_dir / "pr-comments.json").write_text(json.dumps({
        "review_comments": [{
            "id": 7777,
            "user": {"login": "alice"},
            "body": "consider null guard",
            "path": "src/foo.py",
            "line": 42,
            "diff_hunk": "@@ -40,3 +40,3 @@\n-def f(x):\n+def f(x: int):",
            "created_at": "2026-05-21T10:00:00Z",
        }],
    }), encoding="utf-8")

    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)

    out = dp._format_comments_markdown(_Row())
    assert "[inline src/foo.py:42]" in out, "inline tag missing"
    assert "id:" in out, "comment id missing"


def test_general_comment_carries_general_tag(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _force_no_identity(monkeypatch)
    (fake_pr_dir / "pr-comments.json").write_text(json.dumps({
        "issue_comments": [{
            "id": 5555,
            "user": {"login": "bob"},
            "body": "ship it",
            "created_at": "2026-05-21T10:00:00Z",
        }],
    }), encoding="utf-8")

    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)

    out = dp._format_comments_markdown(_Row())
    assert "[general]" in out, "general tag missing"


def test_inline_comment_renders_diff_hunk(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _force_no_identity(monkeypatch)
    (fake_pr_dir / "pr-comments.json").write_text(json.dumps({
        "review_comments": [{
            "id": 1,
            "user": {"login": "alice"},
            "body": "use type hint",
            "path": "src/foo.py",
            "line": 42,
            "diff_hunk": "@@ -40,3 +40,3 @@\n-def f(x):\n+def f(x: int):",
            "created_at": "2026-05-21T10:00:00Z",
        }],
    }), encoding="utf-8")

    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)

    out = dp._format_comments_markdown(_Row())
    assert "```diff" in out, "diff fenced block missing"
    assert "def f(x: int):" in out, "diff_hunk content missing"


def test_replies_nested_under_root(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Replies are indented (↪) and immediately follow their root comment."""
    _force_no_identity(monkeypatch)
    (fake_pr_dir / "pr-comments.json").write_text(json.dumps({
        "review_comments": [
            {"id": 100, "user": {"login": "alice"}, "body": "root", "path": "f.py", "line": 1,
             "created_at": "2026-05-21T10:00:00Z"},
            {"id": 101, "user": {"login": "bob"},   "body": "reply-1",
             "in_reply_to_id": 100, "path": "f.py", "line": 1,
             "created_at": "2026-05-21T10:01:00Z"},
            {"id": 102, "user": {"login": "alice"}, "body": "reply-2",
             "in_reply_to_id": 100, "path": "f.py", "line": 1,
             "created_at": "2026-05-21T10:02:00Z"},
        ],
    }), encoding="utf-8")

    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)

    out = dp._format_comments_markdown(_Row())
    root_idx = out.index("root")
    r1_idx = out.index("reply-1")
    r2_idx = out.index("reply-2")
    assert root_idx < r1_idx < r2_idx, "replies must follow the root in order"
    assert "↪" in out, "reply prefix glyph missing"


def test_short_id_is_last_8_chars() -> None:
    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)
    assert dp._short_id(123456789012345) == "89012345"
    assert dp._short_id("abc") == "abc"
    assert dp._short_id(None) == "?"
