"""Tests for the broader acceptable-reply detection in comment_resolver.py.

Covers the three reply kinds:
  - offline   (existing — agreed offline / out-of-band / followup PR)
  - jira      (NEW — tracked in PROJ-1234 / moved to INFRA-42)
  - synced    (NEW — synced with @alice / per chat with @bob)

Plus negation guards: replies ending in "?" or containing "but/however/except"
must NOT be treated as acceptable dispositions.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def cr_mod():
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "adk-pr-review" / "scripts" / "comment_resolver.py"
    )
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("comment_resolver_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- offline (existing) ----------------------------------------------------

def test_offline_agreed_in_meeting(cr_mod):
    assert cr_mod.has_offline_marker("Agreed offline, will skip for now.") is True


def test_offline_followup_pr(cr_mod):
    assert cr_mod.has_offline_marker(
        "We'll address this in a follow-up PR — thanks!"
    ) is True


def test_offline_negation_blocks(cr_mod):
    assert cr_mod.has_offline_marker(
        "Agreed offline, but only if we cover the edge case."
    ) is False


def test_offline_question_blocks(cr_mod):
    assert cr_mod.has_offline_marker("Discussed in standup?") is False


# ---- jira-reply (NEW) -----------------------------------------------------

def test_jira_tracked_in(cr_mod):
    assert cr_mod.extract_jira_reply_ref("Tracked in PROJ-1234") == "PROJ-1234"


def test_jira_moved_to(cr_mod):
    assert cr_mod.extract_jira_reply_ref("Moved to INFRA-42 for next sprint") == "INFRA-42"


def test_jira_filed_as(cr_mod):
    assert cr_mod.extract_jira_reply_ref("Filed BACK-9999 — handing off to platform.") == "BACK-9999"


def test_jira_followup_loose(cr_mod):
    assert cr_mod.extract_jira_reply_ref("Follow-up: SF-77") == "SF-77"


def test_jira_unrelated_key_in_text_no_verb(cr_mod):
    """A bare key without any tracking verb shouldn't count."""
    assert cr_mod.extract_jira_reply_ref("Looks like ABC-123 might be related") is None


def test_jira_negation_blocks(cr_mod):
    assert cr_mod.extract_jira_reply_ref(
        "Tracked in PROJ-1234, but only if security signs off."
    ) is None


def test_jira_question_blocks(cr_mod):
    assert cr_mod.extract_jira_reply_ref("Tracked in PROJ-1234?") is None


# ---- synced-with (NEW) ----------------------------------------------------

def test_synced_with_handle(cr_mod):
    assert cr_mod.extract_synced_with("Synced with @alice on this.") == "alice"


def test_spoke_with(cr_mod):
    assert cr_mod.extract_synced_with("Spoke to @bob earlier — keeping as-is.") == "bob"


def test_per_chat_with(cr_mod):
    assert cr_mod.extract_synced_with("Per chat with @carol") == "carol"


def test_synced_without_handle_misses(cr_mod):
    """If there's no @handle, we don't infer a sync partner from prose alone."""
    assert cr_mod.extract_synced_with("Synced with the team") is None


# ---- classify_reply (the public composer) ---------------------------------

def test_classify_offline(cr_mod):
    kind, detail = cr_mod.classify_reply("Agreed offline, skipping for now.")
    assert kind == "offline"
    assert detail


def test_classify_jira_beats_no_pattern(cr_mod):
    kind, detail = cr_mod.classify_reply("Tracked in PROJ-1234 — closing this thread.")
    assert kind == "jira"
    assert detail == "PROJ-1234"


def test_classify_synced(cr_mod):
    kind, detail = cr_mod.classify_reply("Synced with @dave; we agreed to keep this.")
    # The offline-pattern "agreed" doesn't match the offline regex (no "offline"/"meeting"
    # qualifier), but synced-with @handle does. Either way the thread should be
    # acceptable-disposition.
    assert kind in ("synced", "offline")
    assert detail


def test_classify_unrelated_returns_none(cr_mod):
    kind, detail = cr_mod.classify_reply("Could you also check the test coverage here?")
    assert kind is None
    assert detail is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
