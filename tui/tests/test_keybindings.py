from __future__ import annotations

import asyncio
import json

from tui.widgets.queue_action_bar import QueueActionBar
from tui.widgets.queue_table import QueueTable


def _queue_action_text(app) -> str:
    return str(app.query_one(QueueActionBar).render())


def test_f_cycles_filter(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _queue_action_text(tui_app)
            assert "filter:all" in before
            await pilot.press("f")
            await pilot.pause()
            after = _queue_action_text(tui_app)
            assert "filter:open" in after
            assert before != after

    asyncio.run(_run())


def test_queue_action_bar_shows_primary_actions(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            bar = _queue_action_text(tui_app)
            assert "runner:claude" in bar

    asyncio.run(_run())


def test_main_uses_configured_runner_when_flag_absent(tmp_path, monkeypatch):
    from tui import app as app_module

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"pr_review_all": {"runner": "cursor"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    captured = {}

    class FakeApp:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            captured["ran"] = True

    monkeypatch.setattr(app_module, "AdkApp", FakeApp)

    rc = app_module.main([])

    assert rc == 0
    assert captured["agent"] == "cursor"
    assert captured["ran"] is True


def test_main_runner_flag_overrides_config(tmp_path, monkeypatch):
    from tui import app as app_module

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"pr_review_all": {"runner": "cursor"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    captured = {}

    class FakeApp:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def run(self):
            return None

    monkeypatch.setattr(app_module, "AdkApp", FakeApp)

    rc = app_module.main(["--runner", "codex"])

    assert rc == 0
    assert captured["agent"] == "codex"


def test_capital_k_cycles_sort(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _queue_action_text(tui_app)
            assert "sort:queue" in before
            await pilot.press("K")
            await pilot.pause()
            after = _queue_action_text(tui_app)
            assert "sort:newest" in after
            assert before != after

    asyncio.run(_run())


def test_jk_moves_cursor(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            table = tui_app.query_one(QueueTable)
            before = table.cursor_row
            await pilot.press("j")
            await pilot.pause()
            after = table.cursor_row
            assert after == before + 1

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Primary action bars do not have legacy keys
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Binding map assertions — key → action_name
# ---------------------------------------------------------------------------

import pytest


@pytest.mark.parametrize("key,expected_action", [
    ("s", "sync_pr"),
    ("S", "sync_all"),
    ("r", "rereview"),
    ("R", "sync_review_all"),
    ("x", "remove_pr"),
    ("u", "refresh_cascade"),
    ("t", "pick_agent"),
    ("o", "open_links"),
    ("a", "approve_pr"),
    ("m", "merge_status"),
    ("M", "merge_pr"),
    ("l", "show_logs"),
    ("L", "show_run_logs"),
])
def test_binding_key_to_action(key, expected_action):
    from textual.binding import Binding
    from tui.app import AdkApp
    bindings = [b for b in AdkApp.BINDINGS if isinstance(b, Binding) and b.key == key]
    assert bindings, f"No binding found for key {key!r}"
    assert bindings[0].action == expected_action, (
        f"Key {key!r}: expected action {expected_action!r}, got {bindings[0].action!r}"
    )


def test_legacy_keys_not_bound():
    from textual.binding import Binding
    from tui.app import AdkApp
    actions = {b.action for b in AdkApp.BINDINGS if isinstance(b, Binding)}
    for removed_action in ("sync_review_pr", "cycle_theme"):
        assert removed_action not in actions, (
            f"Legacy action {removed_action!r} should not appear in BINDINGS"
        )
    keys = {b.key for b in AdkApp.BINDINGS if isinstance(b, Binding)}
    assert "v" not in keys, "Key 'v' (old rereview) should be removed"
    assert "A" not in keys, "Key 'A' (old sync_review_all) should be removed"


def test_bars_have_no_legacy_review_or_batch_keys(fake_plan_path, tmp_path):
    """Action bars must not advertise removed multi-select / parallel / review keys."""
    import json
    from tui.app import AdkApp
    from tui.widgets.pr_action_bar import PRActionBar

    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": [{
        "pr_url": "https://github.com/foo/bar/pull/200",
        "status": "pending",
        "prep_status": "ready",
        "head_sha": "abc0001",
        "prep_head_sha": "abc0001",
        "last_reviewed_head_sha": "abc0002",
        "last_reviewed_at": "2026-05-19T10:00:00Z",
        "taken_at": None,
        "title": "ready PR",
        "author": "alice",
    }]}))
    app = AdkApp(queue_path=q, plan_path=fake_plan_path, poll_interval=0.05)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            for bar_text in (
                str(app.query_one(QueueActionBar).render()),
                str(app.query_one(PRActionBar).render()),
            ):
                assert "[r] review" not in bar_text
                assert "run-sel" not in bar_text
                assert "[space]" not in bar_text
                assert "[p]" not in bar_text

    asyncio.run(_run())
