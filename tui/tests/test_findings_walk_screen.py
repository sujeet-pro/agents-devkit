"""Tests for FindingsWalkScreen and FindingsEditScreen.

Uses subprocess.run monkey-patching to capture triage.py calls without
executing the real script.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from tui.screens.findings_walk_screen import (
    FindingsWalkScreen,
    _finding_text,
    _load_findings,
    _run_triage,
)
from tui.screens.findings_edit_screen import FindingsEditScreen


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SAMPLE_FINDINGS: list[dict[str, Any]] = [
    {
        "id": "f-001",
        "severity": "blocker",
        "dimension": "security",
        "file": "src/auth.ts",
        "line": 42,
        "title": "Token check skips expiry",
        "body": "The token validation does not check the expiry field.",
        "suggestion": "Add `if token.exp < now: raise AuthError`",
    },
    {
        "id": "f-002",
        "severity": "warning",
        "dimension": "correctness",
        "file": "src/db.ts",
        "line": 17,
        "title": "Missing null check",
        "body": "result may be null here",
        "suggestion": "Guard with `if result is None: return`",
    },
    {
        "id": "f-003",
        "severity": "info",
        "dimension": "style",
        "file": "README.md",
        "line": 5,
        "title": "Typo in heading",
        "body": "\"Installtion\" should be \"Installation\"",
        "suggestion": "Fix the typo.",
    },
]


@pytest.fixture
def findings_json(tmp_path: Path) -> Path:
    p = tmp_path / "pr-review" / "validated-findings.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(_SAMPLE_FINDINGS))
    return p


@pytest.fixture
def task_dir(tmp_path: Path) -> Path:
    d = tmp_path / "task"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Unit tests (no TUI)
# ---------------------------------------------------------------------------

def test_load_findings_list_format(findings_json: Path) -> None:
    findings = _load_findings(findings_json)
    assert len(findings) == 3
    assert findings[0]["id"] == "f-001"


def test_load_findings_dict_format(tmp_path: Path) -> None:
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"findings": _SAMPLE_FINDINGS, "meta": {}}))
    findings = _load_findings(p)
    assert len(findings) == 3


def test_load_findings_missing_file(tmp_path: Path) -> None:
    findings = _load_findings(tmp_path / "nonexistent.json")
    assert findings == []


def test_finding_text_includes_key_fields() -> None:
    f = _SAMPLE_FINDINGS[0]
    text = _finding_text(f, 0, 3)
    assert "f-001" in text
    assert "blocker" in text
    assert "Token check skips expiry" in text
    assert "Finding 1 of 3" in text


def test_run_triage_captures_args(tmp_path: Path) -> None:
    """Verify _run_triage builds the correct subprocess args."""
    calls: list[list[str]] = []
    fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

    def _fake_run(cmd, **kwargs):
        calls.append(cmd)
        return fake_result

    with patch("tui.screens.findings_walk_screen.subprocess.run", _fake_run):
        rc, out = _run_triage(tmp_path, "--mark", "f-001", "--state", "accept")

    assert rc == 0
    assert len(calls) == 1
    assert "--task-dir" in calls[0]
    assert "--mark" in calls[0]
    assert "f-001" in calls[0]
    assert "--state" in calls[0]
    assert "accept" in calls[0]
    # The old broken form must not appear.
    assert "--id" not in calls[0]


# ---------------------------------------------------------------------------
# TUI integration tests
# ---------------------------------------------------------------------------

class _WalkHarness(App):
    """Harness that pushes FindingsWalkScreen on mount."""

    def __init__(self, findings_path: Path, task_dir: Path, pr_url: str | None = None) -> None:
        super().__init__()
        self._findings_path = findings_path
        self._task_dir = task_dir
        self._pr_url = pr_url
        self.triage_calls: list[list[str]] = []

    def compose(self) -> ComposeResult:
        yield Static("(base)", markup=False)

    def on_mount(self) -> None:
        self.push_screen(
            FindingsWalkScreen(
                findings_path=self._findings_path,
                task_dir=self._task_dir,
                pr_url=self._pr_url,
            )
        )


def _make_triage_mock(calls: list):
    fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

    def _fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        return fake_result

    return _fake_run


def test_findings_walk_screen_opens(findings_json: Path, task_dir: Path) -> None:
    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir)

    async def _run() -> None:
        with patch("tui.screens.findings_walk_screen.subprocess.run", _make_triage_mock([])):
            async with app.run_test() as pilot:
                await pilot.pause()
                # The modal should be on the screen stack.
                assert len(app.screen_stack) == 2
                assert isinstance(app.screen_stack[-1], FindingsWalkScreen)
                # First finding text should be visible.
                body = str(app.screen_stack[-1].query_one("#fw-body", Static).content)
                assert "f-001" in body
                assert "Token check skips expiry" in body

    asyncio.run(_run())


def test_findings_walk_accept_calls_triage(findings_json: Path, task_dir: Path) -> None:
    calls: list[list[str]] = []
    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir)

    async def _run() -> None:
        with patch("tui.screens.findings_walk_screen.subprocess.run", _make_triage_mock(calls)):
            async with app.run_test() as pilot:
                await pilot.pause()
                # Press A to accept f-001.
                await pilot.press("a")
                await pilot.pause()

    asyncio.run(_run())

    # Should call triage.py --mark <fid> --state accept (correct CLI form).
    accept_calls = [c for c in calls if "--mark" in c and "--state" in c and "accept" in c]
    assert len(accept_calls) >= 1
    idx = accept_calls[0].index("--mark")
    assert accept_calls[0][idx + 1] == "f-001", "finding id must be the --mark value"
    assert "--id" not in accept_calls[0], "--id flag must not appear (it does not exist in triage.py)"


def test_findings_walk_skip_advances_index(findings_json: Path, task_dir: Path) -> None:
    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir)

    async def _run() -> None:
        with patch("tui.screens.findings_walk_screen.subprocess.run", _make_triage_mock([])):
            async with app.run_test() as pilot:
                await pilot.pause()
                screen = app.screen_stack[-1]
                assert isinstance(screen, FindingsWalkScreen)
                # Initially at f-001.
                body_before = str(screen.query_one("#fw-body", Static).content)
                assert "Finding 1 of 3" in body_before
                # Skip to f-002.
                await pilot.press("right")
                await pilot.pause()
                body_after = str(screen.query_one("#fw-body", Static).content)
                assert "Finding 2 of 3" in body_after
                assert "f-002" in body_after

    asyncio.run(_run())


def test_findings_walk_save_quit_calls_finalize(findings_json: Path, task_dir: Path) -> None:
    calls: list[list[str]] = []
    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir)

    async def _run() -> None:
        with patch("tui.screens.findings_walk_screen.subprocess.run", _make_triage_mock(calls)):
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("q")
                await pilot.pause()

    asyncio.run(_run())

    finalize_calls = [c for c in calls if "--finalize" in c]
    assert len(finalize_calls) >= 1


def test_findings_walk_reject_calls_triage_reject(findings_json: Path, task_dir: Path) -> None:
    """Reject via 'r' key: should call --mark <fid> --state reject."""
    calls: list[list[str]] = []
    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir)

    async def _run() -> None:
        fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

        def _fake_run(cmd, **kwargs):
            calls.append(list(cmd))
            return fake_result

        with patch("tui.screens.findings_walk_screen.subprocess.run", _fake_run):
            async with app.run_test() as pilot:
                await pilot.pause()
                # Press R, then submit the prompt with a reason.
                await pilot.press("r")
                await pilot.pause()
                # Type a reason and submit.
                await pilot.press("t", "e", "s", "t", " ", "r", "e", "a", "s", "o", "n")
                await pilot.press("enter")
                await pilot.pause(delay=0.3)

    asyncio.run(_run())

    reject_calls = [c for c in calls if "--mark" in c and "--state" in c and "reject" in c]
    assert len(reject_calls) >= 1
    idx = reject_calls[0].index("--mark")
    assert reject_calls[0][idx + 1] == "f-001", "finding id must be the --mark value"
    assert "--id" not in reject_calls[0], "--id flag must not appear"


def test_findings_walk_auto_post_spawned_on_quit_with_accepted(
    findings_json: Path, task_dir: Path
) -> None:
    """Closing the modal after accepting ≥1 finding spawns `adk pr-task post <url>`."""
    run_calls: list[list[str]] = []
    popen_calls: list[list[str]] = []
    pr_url = "https://github.com/acme/repo/pull/42"

    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir, pr_url=pr_url)

    async def _run() -> None:
        fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

        def _fake_run(cmd, **kwargs):
            run_calls.append(list(cmd))
            return fake_result

        fake_popen = MagicMock()

        def _fake_popen(cmd, **kwargs):
            popen_calls.append(list(cmd))
            return fake_popen

        with patch("tui.screens.findings_walk_screen.subprocess.run", _fake_run):
            with patch("tui.screens.findings_walk_screen.subprocess.Popen", _fake_popen):
                async with app.run_test() as pilot:
                    await pilot.pause()
                    # Accept finding f-001.
                    await pilot.press("a")
                    await pilot.pause()
                    # Quit — triggers finalize then auto-post.
                    await pilot.press("q")
                    await pilot.pause()

    asyncio.run(_run())

    # At least one Popen call containing pr-task post and the pr_url.
    assert len(popen_calls) >= 1, "expected subprocess.Popen to be called for auto-post"
    post_call = popen_calls[0]
    assert "pr-task" in post_call
    assert "post" in post_call
    assert pr_url in post_call


def test_findings_walk_no_auto_post_when_none_accepted(
    findings_json: Path, task_dir: Path
) -> None:
    """No post subprocess is spawned when zero findings were accepted."""
    popen_calls: list[list[str]] = []
    pr_url = "https://github.com/acme/repo/pull/42"

    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir, pr_url=pr_url)

    async def _run() -> None:
        fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

        def _fake_run(cmd, **kwargs):
            return fake_result

        fake_popen = MagicMock()

        def _fake_popen(cmd, **kwargs):
            popen_calls.append(list(cmd))
            return fake_popen

        with patch("tui.screens.findings_walk_screen.subprocess.run", _fake_run):
            with patch("tui.screens.findings_walk_screen.subprocess.Popen", _fake_popen):
                async with app.run_test() as pilot:
                    await pilot.pause()
                    # Skip without accepting anything.
                    await pilot.press("right")
                    await pilot.pause()
                    # Quit.
                    await pilot.press("q")
                    await pilot.pause()

    asyncio.run(_run())

    assert len(popen_calls) == 0, "no Popen should be spawned when no findings accepted"


def test_findings_walk_toggle_auto_post_suppresses_spawn(
    findings_json: Path, task_dir: Path
) -> None:
    """Pressing P disables auto-post; quitting after accept must not spawn Popen."""
    popen_calls: list[list[str]] = []
    pr_url = "https://github.com/acme/repo/pull/42"

    app = _WalkHarness(findings_path=findings_json, task_dir=task_dir, pr_url=pr_url)

    async def _run() -> None:
        fake_result = MagicMock(returncode=0, stdout="ok\n", stderr="")

        def _fake_run(cmd, **kwargs):
            return fake_result

        fake_popen = MagicMock()

        def _fake_popen(cmd, **kwargs):
            popen_calls.append(list(cmd))
            return fake_popen

        with patch("tui.screens.findings_walk_screen.subprocess.run", _fake_run):
            with patch("tui.screens.findings_walk_screen.subprocess.Popen", _fake_popen):
                async with app.run_test() as pilot:
                    await pilot.pause()
                    # Disable auto-post with P.
                    await pilot.press("p")
                    await pilot.pause()
                    # Accept f-001.
                    await pilot.press("a")
                    await pilot.pause()
                    # Quit — auto-post is off, so no Popen.
                    await pilot.press("q")
                    await pilot.pause()

    asyncio.run(_run())

    assert len(popen_calls) == 0, "Popen must not be called when auto-post is toggled off"


# ---------------------------------------------------------------------------
# FindingsEditScreen tests
# ---------------------------------------------------------------------------

class _EditHarness(App):
    def __init__(self, title: str, body: str) -> None:
        super().__init__()
        self._title = title
        self._body = body
        self.result: str | None = "NOT_SET"

    def compose(self) -> ComposeResult:
        yield Static("base", markup=False)

    def on_mount(self) -> None:
        self.push_screen(
            FindingsEditScreen(title=self._title, body=self._body),
            callback=self._on_result,
        )

    def _on_result(self, value: str | None) -> None:
        self.result = value


def test_findings_edit_screen_opens(tmp_path: Path) -> None:
    app = _EditHarness(title="Edit finding", body="original body text")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            from textual.widgets import TextArea
            editor = app.screen_stack[-1].query_one("#fe-editor", TextArea)
            assert "original body text" in editor.text

    asyncio.run(_run())


def test_findings_edit_cancel_returns_none(tmp_path: Path) -> None:
    app = _EditHarness(title="t", body="b")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()

    asyncio.run(_run())
    assert app.result is None


def test_findings_edit_save_returns_text(tmp_path: Path) -> None:
    app = _EditHarness(title="t", body="initial")

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("ctrl+s")
            await pilot.pause()

    asyncio.run(_run())
    # The result should be the text from the editor (at minimum non-None).
    assert app.result is not None
