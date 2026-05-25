"""Tests for async action-availability pre-fetch (Item 1 of PR review DX).

Covers:
- PrActionScreen accepts availability= param and applies filter_by_availability.
- app.py._fetch_action_availability returns None gracefully on subprocess failure.
- PrActionScreen hint text differs when availability is live vs. None.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from tui.screens.pr_action_screen import (
    PrActionScreen,
    _ALL_ACTIONS,
    filter_by_availability,
)


# ---------------------------------------------------------------------------
# PrActionScreen with availability= kwarg
# ---------------------------------------------------------------------------

def _make_queue_row(
    *,
    status: str = "pending",
    prep_status: str = "ready",
    ready_for_review: bool = True,
    slack_permalink: str | None = "https://example.slack.com/p1",
):
    from tui.model.queue_model import QueueRow
    return QueueRow(
        queue_index=0,
        pr_url="https://github.com/acme/foo/pull/42",
        host="github",
        repo="acme/foo",
        number=42,
        title="test PR",
        author="alice",
        target_branch="main",
        head_sha="abc0001",
        status=status,
        prep_status=prep_status,
        prep_error=None,
        taken_at=None,
        last_checked_at=None,
        last_reviewed_at="2026-05-19T10:00:00Z",
        last_reviewed_head_sha="abc0002",
        ready_for_review=ready_for_review,
        slack_permalink=slack_permalink,
    )


def test_pr_action_screen_no_availability_shows_all_local_actions() -> None:
    """When availability=None, only local state filtering applies (existing behaviour)."""
    row = _make_queue_row()
    screen = PrActionScreen(pr_label="acme/foo#42", row=row, availability=None)
    # All 10 secondary actions should be present for an eligible row.
    assert len(screen._actions) == 10


def test_pr_action_screen_with_availability_filters_unavailable() -> None:
    """When availability has gates, unavailable actions are removed."""
    row = _make_queue_row()
    availability = {
        "pr_url": "https://github.com/acme/foo/pull/42",
        "actions": {
            "open_pr":    {"available": True,  "gate": "read_only"},
            "open_slack": {"available": True,  "gate": "read_only"},
            "full_review": {"available": False, "gate": "shared_state",
                            "reason": "not ready"},
            "re_review":  {"available": False, "gate": "shared_state",
                           "reason": "not ready"},
            "merge":      {"available": False, "gate": "merge_gate",
                           "reason": "not approved"},
            "status_update": {"available": True, "gate": "shared_state"},
            "global_refresh": {"available": True, "gate": "shared_state"},
            "view_log":   {"available": True, "gate": "read_only"},
        },
    }
    screen = PrActionScreen(pr_label="acme/foo#42", row=row, availability=availability)
    action_ids = [a[0] for a in screen._actions]
    # Gated as unavailable
    assert "review" not in action_ids, "review must be filtered by CLI gate"
    assert "rereview" not in action_ids, "rereview shares re_review gate"
    assert "merge" not in action_ids, "merge must be filtered by CLI gate"
    # Always kept
    assert "open-pr" in action_ids


def test_pr_action_screen_hint_differs_with_live_availability() -> None:
    """Modal title includes '[live gates]' when availability is provided."""
    row = _make_queue_row()
    screen_live = PrActionScreen(
        pr_label="acme/foo#42",
        row=row,
        availability={"actions": {}},
    )
    screen_none = PrActionScreen(pr_label="acme/foo#42", row=row, availability=None)
    assert "[live gates]" in screen_live._availability_hint
    assert screen_none._availability_hint == ""


# ---------------------------------------------------------------------------
# _fetch_action_availability helper — integration via fake adk binary
# ---------------------------------------------------------------------------

def _make_app(tmp_path: Path, fake_plan_path: Path, adk: Path):
    from tui.app import AdkApp
    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": [{
        "pr_url": "https://github.com/acme/foo/pull/42",
        "status": "pending",
        "prep_status": "ready",
        "head_sha": "abc001",
        "last_reviewed_at": None,
        "taken_at": None,
        "title": "test",
        "author": "alice",
    }]}))
    return AdkApp(
        queue_path=q,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )


def test_fetch_availability_returns_none_on_nonzero_exit(
    tmp_path: Path, fake_plan_path: Path
) -> None:
    """A failing adk binary must yield None (graceful fallback)."""
    adk = tmp_path / "adk"
    adk.write_text("#!/bin/sh\nexit 1\n")
    adk.chmod(0o755)
    app = _make_app(tmp_path, fake_plan_path, adk)

    async def _run() -> dict | None:
        return await app._fetch_action_availability(
            "https://github.com/acme/foo/pull/42"
        )

    result = asyncio.run(_run())
    assert result is None


def test_fetch_availability_returns_none_on_bad_json(
    tmp_path: Path, fake_plan_path: Path
) -> None:
    """Non-JSON output must yield None."""
    adk = tmp_path / "adk"
    adk.write_text("#!/bin/sh\necho 'not json'\nexit 0\n")
    adk.chmod(0o755)
    app = _make_app(tmp_path, fake_plan_path, adk)

    async def _run() -> dict | None:
        return await app._fetch_action_availability(
            "https://github.com/acme/foo/pull/42"
        )

    result = asyncio.run(_run())
    assert result is None


def test_fetch_availability_parses_valid_json(
    tmp_path: Path, fake_plan_path: Path
) -> None:
    """A well-formed JSON response is returned as a dict."""
    payload = json.dumps({
        "pr_url": "https://github.com/acme/foo/pull/42",
        "actions": {"open_pr": {"available": True, "gate": "read_only"}},
    })
    adk = tmp_path / "adk"
    adk.write_text(f"#!/bin/sh\necho '{payload}'\nexit 0\n")
    adk.chmod(0o755)
    app = _make_app(tmp_path, fake_plan_path, adk)

    async def _run() -> dict | None:
        return await app._fetch_action_availability(
            "https://github.com/acme/foo/pull/42"
        )

    result = asyncio.run(_run())
    assert result is not None
    assert result["actions"]["open_pr"]["available"] is True


def test_fetch_availability_passes_queue_flag(
    tmp_path: Path, fake_plan_path: Path
) -> None:
    """--queue path must be forwarded to the adk subprocess."""
    calls_log = tmp_path / "calls.txt"
    adk = tmp_path / "adk"
    adk.write_text(
        f"#!/bin/sh\necho \"$@\" >> \"{calls_log}\"\necho '{{\"actions\":{{}}}}'\nexit 0\n"
    )
    adk.chmod(0o755)
    app = _make_app(tmp_path, fake_plan_path, adk)

    async def _run() -> dict | None:
        return await app._fetch_action_availability(
            "https://github.com/acme/foo/pull/42"
        )

    asyncio.run(_run())
    calls = calls_log.read_text()
    assert "--queue" in calls
    assert "action-availability" in calls
