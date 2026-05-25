from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from textual.coordinate import Coordinate
from textual.widgets import DataTable, OptionList

from tui.app import AdkApp
from tui.screens.info_screen import InfoScreen
from tui.screens.pr_action_screen import PrActionScreen
from tui.widgets.log_pane import LogPane
from tui.widgets.queue_table import QueueTable


def _log_text(app: AdkApp) -> str:
    pane = app.screen_stack[0].query_one(LogPane)
    lines = getattr(pane, "lines", [])
    return "\n".join(getattr(line, "text", None) or str(line) for line in lines)


async def _poll_until(predicate, *, pilot, timeout_s: float = 5.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        await asyncio.sleep(tick_s)
        if predicate():
            return True
        elapsed += tick_s
    return False


def _recording_adk(tmp_path: Path, log_path: Path) -> Path:
    p = tmp_path / "adk"
    p.write_text(
        f"#!/bin/sh\n"
        f"echo \"$@\" >> \"{log_path}\"\n"
        "echo ok\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


def test_sync_pr_key_1_updates_and_prepares(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("1")
            ok = await _poll_until(
                lambda: "prepare index exited rc=0" in _log_text(app),
                pilot=pilot,
                timeout_s=8.0,
            )
            assert ok, _log_text(app)

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "pr-queue --queue" in calls
    assert " update " in f" {calls} "
    assert "pr-task prepare" in calls


def test_A_runs_sync_then_sequential_reviews(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    _REPO_ROOT = Path(__file__).resolve().parent.parent.parent
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        agent_bin=fake_claude_script,
        worker_script=_REPO_ROOT / "tui" / "worker.py",
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("A")
            ok = await _poll_until(
                lambda: "Sync + Review all done" in _log_text(app),
                pilot=pilot,
                timeout_s=25.0,
            )
            assert ok, _log_text(app)

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "pr-sync" in calls
    assert "pr-review-all" not in calls


def test_l_shows_selected_pr_worker_log(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_file = tmp_path / "review.log"
    log_file.write_text("phase 1: context\nphase 2: review\n", encoding="utf-8")
    workers = tmp_path / "workers"
    workers.mkdir()
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (workers / "123.json").write_text(json.dumps({
        "pid": 123,
        "worker_id": "w123",
        "run_id": "run-1",
        "pr_url": "https://github.com/foo/bar/pull/200",
        "subject": "https://github.com/foo/bar/pull/200",
        "task_type": "review",
        "status": "running",
        "agent": "claude",
        "queue": str(eligible_queue_path),
        "started_at": now,
        "last_heartbeat": now,
        "current_phase": "phase 2: review",
        "log_path": str(log_file),
        "rc": None,
    }), encoding="utf-8")
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        heartbeat_dir=workers,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("l")
            await pilot.pause()
            text = _log_text(app)
            assert "active worker" in text
            assert "phase 2: review" in text

    asyncio.run(_run())


def test_clicking_pr_number_opens_that_pr(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.screen_stack[0].query_one(QueueTable)
            url = table.pr_url_for_row(0)
            table.post_message(QueueTable.PrNumberClicked(url or ""))
            ok = await _poll_until(lambda: "open PR exited rc=0" in _log_text(app), pilot=pilot)
            assert ok, _log_text(app)
            assert url is not None

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "pr --queue" in calls
    assert " open " in f" {calls} "


def test_clicking_non_pr_column_does_not_open(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.screen_stack[0].query_one(QueueTable)
            # Non-PR cells don't emit the custom PrNumberClicked message.
            await pilot.pause()

    asyncio.run(_run())
    assert not log_path.exists()


def test_enter_opens_pr_action_menu_and_default_opens_pr(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_modal = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_modal, "PR action menu did not open"
            await pilot.press("enter")
            ok = await _poll_until(lambda: "open PR exited rc=0" in _log_text(app), pilot=pilot)
            assert ok, _log_text(app)

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "pr --queue" in calls
    assert " open " in f" {calls} "


def test_M_merge_sends_tui_confirmed_flag(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """After the user confirms the ConfirmScreen, the CLI merge command must
    include --yes and --tui-confirmed so the config-gate is bypassed."""
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    from tui.screens.confirm_screen import ConfirmScreen

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_menu = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_menu, "PR action menu did not open"
            for _ in range(9):
                await pilot.press("down")
            await pilot.press("enter")
            ok_modal = await _poll_until(
                lambda: any(isinstance(s, ConfirmScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_modal, "ConfirmScreen did not open"
            await pilot.press("y")
            ok = await _poll_until(lambda: "merge PR exited rc=0" in _log_text(app), pilot=pilot)
            assert ok, _log_text(app)

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "--tui-confirmed" in calls
    assert "--yes" in calls


def test_m_shows_info_screen_for_merge_status(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """Pressing m (merge-status) must open an InfoScreen, not dump output into LogPane."""
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_menu = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_menu, "PR action menu did not open"
            for _ in range(8):
                await pilot.press("down")
            await pilot.press("enter")
            ok = await _poll_until(
                lambda: any(isinstance(s, InfoScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, (
                f"InfoScreen did not open after pressing 'm'.\n"
                f"screens={[type(s).__name__ for s in app.screen_stack]}\n"
                f"log={_log_text(app)}"
            )
            # Activity log must still record the invocation and exit code.
            log = _log_text(app)
            assert "merge status exited rc=0" in log, (
                f"Exit-code line missing from LogPane.\nlog={log}"
            )

    asyncio.run(_run())
    calls = log_path.read_text()
    assert "merge-status" in calls


def test_merge_status_log_has_command_but_not_output_lines(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """The LogPane should get $ cmd and exit code, but NOT the output body.

    The recording adk script echoes 'ok'; that line should appear only in the
    InfoScreen content, not get written into the LogPane.
    """
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_menu = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_menu, "PR action menu did not open"
            for _ in range(8):
                await pilot.press("down")
            await pilot.press("enter")
            ok = await _poll_until(
                lambda: any(isinstance(s, InfoScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "InfoScreen did not open"
            log = _log_text(app)
            # The command echo line must be present (activity trace).
            assert "$ " in log, "Command echo line missing from LogPane"
            # 'ok' is what the recording_adk script echoes as body output;
            # it must NOT appear as a raw body line in LogPane — the whole
            # body goes to InfoScreen instead.
            log_lines = log.splitlines()
            body_lines = [
                ln for ln in log_lines
                if ln.strip() == "ok"
            ]
            assert not body_lines, (
                f"Body output 'ok' leaked into LogPane.\nlog={log}"
            )

    asyncio.run(_run())


def test_info_screen_dismisses_on_escape(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """InfoScreen must be dismissable with escape, returning to the main screen."""
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_menu = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_menu, "PR action menu did not open"
            for _ in range(8):
                await pilot.press("down")
            await pilot.press("enter")
            ok = await _poll_until(
                lambda: any(isinstance(s, InfoScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, "InfoScreen did not open"
            await pilot.press("escape")
            await pilot.pause()
            assert not any(isinstance(s, InfoScreen) for s in app.screen_stack), (
                "InfoScreen should be gone after escape"
            )

    asyncio.run(_run())


def test_merge_status_via_action_menu_shows_info_screen(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    """Choosing merge-status from the Enter action menu must also open InfoScreen."""
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_modal = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_modal, "PR action menu did not open"
            # Navigate down to "Show merge readiness" (merge-status).
            # merge-status is at index 8 (0-based) for eligible rows.
            for _ in range(8):
                await pilot.press("down")
            await pilot.press("enter")
            ok = await _poll_until(
                lambda: any(isinstance(s, InfoScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok, (
                f"InfoScreen did not open via action menu.\n"
                f"screens={[type(s).__name__ for s in app.screen_stack]}\n"
                f"log={_log_text(app)}"
            )

    asyncio.run(_run())


def test_datatable_row_selected_opens_pr_action_menu(
    eligible_queue_path: Path,
    fake_plan_path: Path,
    tmp_path: Path,
) -> None:
    log_path = tmp_path / "calls.log"
    adk = _recording_adk(tmp_path, log_path)
    app = AdkApp(
        queue_path=eligible_queue_path,
        plan_path=fake_plan_path,
        adk_bin=adk,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.screen_stack[0].query_one(QueueTable)
            event = DataTable.RowSelected(
                table,
                cursor_row=0,
                row_key=table.coordinate_to_cell_key(Coordinate(0, 0)).row_key,
            )
            app.on_data_table_row_selected(event)
            ok_modal = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_modal, "PR action menu did not open from DataTable.RowSelected"

    asyncio.run(_run())
    # Opening the action menu now triggers an action-availability pre-fetch.
    # No action commands (pr open, pr-queue update, etc.) should have been
    # dispatched — only the pre-fetch call is allowed.
    if log_path.exists():
        calls = log_path.read_text()
        assert "action-availability" in calls, (
            f"Only action-availability pre-fetch is expected.\nCalls:\n{calls}"
        )
        # Make sure no action was actually dispatched.
        for forbidden in (" open ", " update ", " merge ", " prepare "):
            assert forbidden not in f" {calls} ", (
                f"Action command unexpectedly dispatched: {forbidden!r}\nCalls:\n{calls}"
            )


# ---------------------------------------------------------------------------
# Action-filtering tests (DX improvement — context-aware action list)
# ---------------------------------------------------------------------------

def _make_queue_row_obj(
    *,
    status: str = "pending",
    prep_status: str = "ready",
    ready_for_review: bool = True,
    last_reviewed_at: str | None = "2026-05-19T10:00:00Z",
    slack_permalink: str | None = "https://example.slack.com/p1",
    taken_at: str | None = None,
    head_sha: str | None = "abc0001",
    last_reviewed_head_sha: str | None = "abc0002",
):
    """Build a minimal QueueRow for action-filtering unit tests."""
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
        head_sha=head_sha,
        status=status,
        prep_status=prep_status,
        prep_error=None,
        taken_at=taken_at,
        last_checked_at=None,
        last_reviewed_at=last_reviewed_at,
        last_reviewed_head_sha=last_reviewed_head_sha,
        ready_for_review=ready_for_review,
        slack_permalink=slack_permalink,
    )


def test_build_actions_all_visible_for_eligible_row() -> None:
    """A pending, ready, previously-reviewed PR with Slack should show all 10 actions."""
    from tui.screens.pr_action_screen import _build_actions
    row = _make_queue_row_obj()
    actions = _build_actions(row)
    ids = [a[0] for a in actions]
    assert ids == [
        "open-pr", "open-slack", "update-pr", "refresh-context", "update-index",
        "review", "rereview", "show-logs", "merge-status", "merge",
    ]


def test_build_actions_hides_open_slack_without_permalink() -> None:
    from tui.screens.pr_action_screen import _build_actions
    row = _make_queue_row_obj(slack_permalink=None)
    ids = [a[0] for a in _build_actions(row)]
    assert "open-slack" not in ids
    assert "open-pr" in ids


def test_build_actions_terminal_pr_hides_mutating_actions() -> None:
    """Merged/closed PRs must not offer review, merge, or sync operations."""
    from tui.screens.pr_action_screen import _build_actions
    for terminal_status in ("merged", "closed"):
        row = _make_queue_row_obj(status=terminal_status, ready_for_review=False)
        ids = [a[0] for a in _build_actions(row)]
        for hidden in ("review", "rereview", "update-pr", "refresh-context",
                       "update-index", "merge", "merge-status"):
            assert hidden not in ids, (
                f"Action '{hidden}' should be hidden for status={terminal_status!r}"
            )
        for visible in ("open-pr", "show-logs"):
            assert visible in ids, (
                f"Action '{visible}' should remain visible for status={terminal_status!r}"
            )


def test_build_actions_hides_review_when_not_ready() -> None:
    """A non-terminal PR that is not yet ready_for_review should hide 'Full review'."""
    from tui.screens.pr_action_screen import _build_actions
    row = _make_queue_row_obj(
        status="pending",
        prep_status="preparing",
        ready_for_review=False,
    )
    ids = [a[0] for a in _build_actions(row)]
    assert "review" not in ids
    assert "update-index" in ids


def test_build_actions_uses_developer_intent_labels() -> None:
    """Spot-check that labels use user-facing phrasing, not ADK internal names."""
    from tui.screens.pr_action_screen import _build_actions
    row = _make_queue_row_obj()
    labels = {a[0]: a[1] for a in _build_actions(row)}
    assert labels["review"] == "Full review"
    assert labels["update-index"] == "Prepare review index"
    assert labels["show-logs"] == "View review log"
    assert "index" not in labels.get("update-pr", "").lower()


def test_build_actions_none_row_returns_all() -> None:
    """When no row is selected the full list is returned (modal always renders)."""
    from tui.screens.pr_action_screen import _build_actions, _ALL_ACTIONS
    assert _build_actions(None) == list(_ALL_ACTIONS)


# ---------------------------------------------------------------------------
# filter_by_availability — CLI adapter boundary
# ---------------------------------------------------------------------------

def test_filter_by_availability_none_returns_unchanged() -> None:
    """When availability is None the action list is returned unmodified."""
    from tui.screens.pr_action_screen import _build_actions, filter_by_availability
    row = _make_queue_row_obj()
    actions = _build_actions(row)
    assert filter_by_availability(actions, None) == actions


def test_filter_by_availability_removes_unavailable_actions() -> None:
    """Actions whose CLI gate has available=False must be removed."""
    from tui.screens.pr_action_screen import filter_by_availability
    actions = [
        ("open-pr", "Open PR in browser"),
        ("review", "Full review"),
        ("merge", "Merge PR (guarded)"),
    ]
    availability = {
        "actions": {
            "open_pr":    {"available": True,  "gate": "read_only"},
            "full_review": {"available": False, "gate": "shared_state", "reason": "locked"},
            "merge":       {"available": False, "gate": "merge_gate",   "reason": "not approved"},
        }
    }
    result_ids = [a[0] for a in filter_by_availability(actions, availability)]
    assert "open-pr" in result_ids
    assert "review" not in result_ids      # full_review unavailable
    assert "merge" not in result_ids       # merge unavailable


def test_filter_by_availability_keeps_unmapped_actions() -> None:
    """Actions without a CLI gate mapping pass through unchanged."""
    from tui.screens.pr_action_screen import filter_by_availability
    actions = [("custom", "Custom action")]
    result = filter_by_availability(actions, {"actions": {}})
    assert result == actions


def test_tui_to_availability_key_covers_all_actions() -> None:
    """Every action in _ALL_ACTIONS must have an entry in _TUI_TO_AVAILABILITY_KEY."""
    from tui.screens.pr_action_screen import _ALL_ACTIONS, _TUI_TO_AVAILABILITY_KEY
    for action_id, _label in _ALL_ACTIONS:
        assert action_id in _TUI_TO_AVAILABILITY_KEY, (
            f"Action '{action_id}' is missing from _TUI_TO_AVAILABILITY_KEY"
        )


def test_action_menu_filters_for_terminal_pr(
    tmp_path: Path,
    fake_plan_path: Path,
) -> None:
    """End-to-end: the action menu for a merged PR must not include 'review' or 'merge'."""
    import json
    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": [{
        "pr_url": "https://github.com/acme/foo/pull/99",
        "status": "merged",
        "prep_status": "ready",
        "head_sha": "dead0000",
        "last_reviewed_head_sha": "dead0000",
        "last_reviewed_at": "2026-05-19T10:00:00Z",
        "taken_at": None,
        "title": "merged PR",
        "author": "alice",
        "slack": {"permalink": "https://example.slack.com/p99"},
    }]}))
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            ok_modal = await _poll_until(
                lambda: any(isinstance(s, PrActionScreen) for s in app.screen_stack),
                pilot=pilot,
            )
            assert ok_modal, "PR action menu did not open"
            modal = next(s for s in app.screen_stack if isinstance(s, PrActionScreen))
            opts = modal.query_one(OptionList)
            option_ids = [
                str(opts.get_option_at_index(i).id) for i in range(opts.option_count)
            ]
            assert "review" not in option_ids, "review must be hidden for merged PR"
            assert "merge" not in option_ids, "merge must be hidden for merged PR"
            assert "open-pr" in option_ids, "open-pr must always be present"

    asyncio.run(_run())
