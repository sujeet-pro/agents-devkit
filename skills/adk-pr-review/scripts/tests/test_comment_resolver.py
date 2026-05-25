from __future__ import annotations

import sys
from pathlib import Path

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
