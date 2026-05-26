"""Unit + Pilot tests for the ι end-of-run recap modal."""
from __future__ import annotations

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.app import AdkApp
from tui.screens.recap_screen import RecapScreen, _shorten


# --- 1. _shorten helper ------------------------------------------------------

def test_shorten_github_url() -> None:
    assert _shorten("https://github.com/acme/foo/pull/42") == "acme/foo#42"


def test_shorten_bitbucket_url() -> None:
    assert (
        _shorten("https://bitbucket.org/acme/bar/pull-requests/7")
        == "acme/bar#7"
    )


def test_shorten_unrecognised_url_returns_as_is() -> None:
    assert _shorten("https://example.com/x") == "https://example.com/x"


# --- 2. _format_text unit tests ---------------------------------------------

def _outcome(pr_url: str, outcome: str, rc: int | None = None,
             last_line: str = "") -> dict:
    return {"pr_url": pr_url, "rc": rc, "last_line": last_line, "outcome": outcome}


def test_format_text_empty_outcomes() -> None:
    s = RecapScreen(outcomes=[])
    text = s._format_text()
    assert "Batch recap — 0 rows" in text
    assert "press escape" in text


def test_format_text_mixed_outcomes() -> None:
    outcomes = [
        _outcome("https://github.com/acme/foo/pull/1", "ok", rc=0,
                 last_line="(released: ...)"),
        _outcome("https://github.com/acme/foo/pull/2", "failed", rc=1,
                 last_line="(error: prepare failed)"),
        _outcome("https://github.com/acme/foo/pull/3", "skipped",
                 last_line="not ready"),
    ]
    s = RecapScreen(outcomes=outcomes)
    text = s._format_text()
    assert "Batch recap — 3 rows" in text
    assert "1 ok" in text and "1 failed" in text and "1 skipped" in text
    # Each PR's short form must appear.
    assert "acme/foo#1" in text
    assert "acme/foo#2" in text
    assert "acme/foo#3" in text
    # rc labels show for non-skipped rows.
    assert "rc=0" in text
    assert "rc=1" in text


def test_format_text_ascii_mode_swaps_glyphs() -> None:
    outcomes = [
        _outcome("https://github.com/acme/foo/pull/1", "ok", rc=0),
        _outcome("https://github.com/acme/foo/pull/2", "failed", rc=1),
    ]
    unicode_text = RecapScreen(outcomes=outcomes)._format_text()
    ascii_text = RecapScreen(outcomes=outcomes, ascii_only=True)._format_text()
    assert "✓" in unicode_text and "✗" in unicode_text
    assert "[ok]" in ascii_text and "[fl]" in ascii_text
    assert "✓" not in ascii_text


def test_format_text_truncates_long_last_line() -> None:
    long_line = "a" * 200
    outcomes = [_outcome("https://github.com/acme/foo/pull/1", "ok", rc=0,
                         last_line=long_line)]
    text = RecapScreen(outcomes=outcomes)._format_text()
    # Truncation marker.
    assert "…" in text
    # No line in the rendered body exceeds ~100 chars (60-char cap + prefix).
    for line in text.splitlines():
        assert len(line) <= 120, f"line too long: {line!r}"


# --- 3. Pilot — push/dismiss the modal in a host App ------------------------

class _Harness(App):
    """Minimal app that just pushes a RecapScreen on mount so we can pilot it."""

    def __init__(self, outcomes: list[dict]) -> None:
        super().__init__()
        self._outcomes = outcomes

    def compose(self) -> ComposeResult:
        yield Static("(harness)")

    async def on_mount(self) -> None:
        self.push_screen(RecapScreen(outcomes=self._outcomes))


def test_recap_screen_dismisses_on_escape() -> None:
    outcomes = [_outcome("https://github.com/acme/foo/pull/1", "ok", rc=0)]
    app = _Harness(outcomes=outcomes)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, RecapScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, RecapScreen)

    asyncio.run(_run())


def test_recap_screen_dismisses_on_enter() -> None:
    outcomes = [_outcome("https://github.com/acme/foo/pull/1", "ok", rc=0)]
    app = _Harness(outcomes=outcomes)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, RecapScreen)
            await pilot.press("enter")
            await pilot.pause()
            assert not isinstance(app.screen, RecapScreen)

    asyncio.run(_run())


def test_recap_screen_dismisses_on_q() -> None:
    outcomes: list[dict] = []
    app = _Harness(outcomes=outcomes)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, RecapScreen)
            await pilot.press("q")
            await pilot.pause()
            assert not isinstance(app.screen, RecapScreen)

    asyncio.run(_run())


# --- 4. End-to-end: batch run pushes the recap modal ------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER_SCRIPT = _REPO_ROOT / "tui" / "worker.py"


async def _poll_until(predicate, *, pilot, timeout_s: float = 6.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        if predicate():
            return True
        await asyncio.sleep(tick_s)
        elapsed += tick_s
    return False


def test_sync_review_all_pushes_recap_screen(
    eligible_multi_queue: Path,
    fake_claude_script: Path,
    fake_adk_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """After Sync + Review all finishes, a RecapScreen is pushed onto the stack."""
    app = AdkApp(
        queue_path=eligible_multi_queue,
        agent_bin=fake_claude_script,
        adk_bin=fake_adk_script,
        worker_script=WORKER_SCRIPT,
        heartbeat_dir=worker_heartbeat_dir,
        poll_interval=0.05,
    )

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("R")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RecapScreen),
                pilot=pilot, timeout_s=30.0,
            )
            assert ok, "RecapScreen never appeared after Sync + Review all"
            text = str(app.screen.query_one(Static).render())
            assert "Batch recap — 3 rows" in text

    asyncio.run(_run())
