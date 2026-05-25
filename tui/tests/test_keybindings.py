from __future__ import annotations

import asyncio
import json

from tui.widgets.footer_bar import FooterBar
from tui.widgets.queue_table import QueueTable


def _footer_text(app) -> str:
    return str(app.query_one(FooterBar).render())


def test_f_cycles_filter(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _footer_text(tui_app)
            assert "filter:all" in before
            await pilot.press("f")
            await pilot.pause()
            after = _footer_text(tui_app)
            assert "filter:open" in after
            assert before != after

    asyncio.run(_run())


def test_footer_shows_primary_actions(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            footer = _footer_text(tui_app)
            assert "[1] Sync PR" in footer
            assert "[2] Sync+Review" in footer
            assert "[s] Sync all" in footer
            assert "[A] Sync+Review all" in footer
            assert "runner:claude" in footer

    asyncio.run(_run())


def test_main_uses_configured_runner_when_flag_absent(tmp_path, monkeypatch):
    from tui import app as app_module

    adk_home = tmp_path / ".agents-devkit"
    cfg_dir = adk_home / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"pr_review_all": {"runner": "cursor"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_HOME", str(adk_home))
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

    adk_home = tmp_path / ".agents-devkit"
    cfg_dir = adk_home / "config"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"pr_review_all": {"runner": "cursor"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_HOME", str(adk_home))
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


def test_capital_s_cycles_sort(tui_app):
    async def _run() -> None:
        async with tui_app.run_test() as pilot:
            await pilot.pause()
            before = _footer_text(tui_app)
            assert "sort:queue" in before
            # Capital S — Textual maps shift+s to the literal `S` key.
            await pilot.press("S")
            await pilot.pause()
            after = _footer_text(tui_app)
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
# Primary action footer tests
# ---------------------------------------------------------------------------

def test_footer_has_no_legacy_review_or_batch_keys(fake_plan_path, tmp_path):
    """Footer must not advertise removed multi-select / parallel / review keys."""
    import json
    from tui.app import AdkApp

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
            footer = _footer_text(app)
            assert "[r] review" not in footer
            assert "run-sel" not in footer
            assert "[space]" not in footer
            assert "[p]" not in footer

    asyncio.run(_run())
