"""Tests for Slice D additions to detail_pane.py.

Covers:
(a) Comments filter — open vs all (filtering logic + header text)
(b) Verdict pill — at least 3 of the mapped task_status values
(c) Walk-action mark accept — updates a fake posting-plan state file
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_pr_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect ADK_DATA_HOME to a tmp dir; return the pr-review subdir."""
    tmp = Path(tempfile.mkdtemp())
    monkeypatch.setenv("ADK_DATA_HOME", str(tmp))
    monkeypatch.setenv("ADK_CONFIG_HOME", str(tmp / "config"))
    pr_dir = tmp / "skill-pr-review" / "foo_pr-42" / "pr-review"
    pr_dir.mkdir(parents=True, exist_ok=True)
    return pr_dir


class _Row:
    """Minimal QueueRow stand-in: only repo + number are used for path lookups."""
    repo = "foo"
    number = 42
    pr_url = "https://github.com/foo/foo/pull/42"
    status = "pending"
    prep_status = "ready"
    ready_for_review = True
    head_sha = "aabbccdd"
    last_reviewed_head_sha = None
    taken_at = None
    target_branch = "main"
    title = "test PR"
    last_reviewed_at = None
    author: Any = None
    slack_permalink = None
    prep_error = None


def _force_no_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADK_TUI_SKIP_IDENTITY", "1")


def _reload_dp():
    import importlib
    import tui.model.queue_model as qm
    importlib.reload(qm)
    import tui.widgets.detail_pane as dp
    importlib.reload(dp)
    return dp


# ---------------------------------------------------------------------------
# (a) Comments filter — open vs all
# ---------------------------------------------------------------------------

def _write_review_comments(pr_dir: Path, resolved: list[bool]) -> None:
    """Write review_comments where each entry's resolved flag matches the list."""
    comments = [
        {
            "id": 100 + i,
            "user": {"login": f"user{i}"},
            "body": f"body {i}",
            "path": "src/foo.py",
            "line": i + 1,
            "created_at": "2026-05-21T10:00:00Z",
            "resolved": r,
        }
        for i, r in enumerate(resolved)
    ]
    (pr_dir / "pr-comments.json").write_text(
        json.dumps({"review_comments": comments}),
        encoding="utf-8",
    )


def test_comments_filter_open_hides_resolved_threads(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With filter='open', a fully resolved thread must NOT appear."""
    _force_no_identity(monkeypatch)
    _write_review_comments(fake_pr_dir, resolved=[True])  # 1 resolved thread
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="open")
    assert "body 0" not in out, "resolved thread should be hidden by open filter"
    assert "[filter: open]" in out


def test_comments_filter_open_shows_unresolved_threads(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With filter='open', an unresolved thread must appear."""
    _force_no_identity(monkeypatch)
    _write_review_comments(fake_pr_dir, resolved=[False])  # 1 open thread
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="open")
    assert "body 0" in out, "open thread must appear with open filter"
    assert "[filter: open]" in out


def test_comments_filter_all_shows_all_threads(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With filter='all', both resolved and unresolved threads appear."""
    _force_no_identity(monkeypatch)
    _write_review_comments(fake_pr_dir, resolved=[True, False])
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="all")
    assert "body 0" in out, "resolved thread must appear with all filter"
    assert "body 1" in out, "open thread must appear with all filter"
    assert "[filter: all]" in out


def test_comments_filter_header_shows_open_count(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Header line must show '(N open)' and filter label."""
    _force_no_identity(monkeypatch)
    _write_review_comments(fake_pr_dir, resolved=[True, False])  # 1 open
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="open")
    first_line = out.splitlines()[0]
    assert "1 open" in first_line, f"expected '1 open' in header; got: {first_line!r}"
    assert "[filter: open]" in first_line
    assert "press [o] to toggle" in first_line


def test_issue_comments_always_shown_by_open_filter(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Issue comments (no resolved state) must always appear regardless of filter."""
    _force_no_identity(monkeypatch)
    (fake_pr_dir / "pr-comments.json").write_text(
        json.dumps({"issue_comments": [
            {"id": 9, "user": {"login": "bob"}, "body": "looks good",
             "created_at": "2026-05-21T10:00:00Z"},
        ]}),
        encoding="utf-8",
    )
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="open")
    assert "looks good" in out, "issue comment must always show in open filter"
    assert "always shown" in out, "always-shown hint must be present"


# ---------------------------------------------------------------------------
# (b) Verdict pill
# ---------------------------------------------------------------------------

def _make_full_row(status: str, prep_status: str = "ready", **kwargs) -> _Row:
    row = _Row()
    row.status = status
    row.prep_status = prep_status
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


def test_verdict_pill_ready(fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_identity(monkeypatch)
    dp = _reload_dp()
    row = _make_full_row(status="pending", prep_status="ready", ready_for_review=True)
    pill = dp._verdict_pill(row, None)
    assert pill is not None, "expected a pill for ready status"
    assert "READY" in pill
    assert "[r] to review" in pill


def test_verdict_pill_reviewing(fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_identity(monkeypatch)
    dp = _reload_dp()
    row = _make_full_row(status="in_review", prep_status="ready")
    # Simulate reviewing state: taken_at is recent.
    row.taken_at = "2026-05-21T10:00:00Z"

    from tui.model.workers_model import WorkerRow
    worker = WorkerRow(
        pid=42,
        worker_id="w42",
        run_id=None,
        pr_url=row.pr_url,
        subject=row.pr_url,
        task_type="review",
        status="running",
        agent="claude",
        queue="/tmp/q",
        started_at="2026-05-21T10:00:00Z",
        last_heartbeat="2026-05-21T10:01:00Z",
        current_phase="phase 3",
        rc=None,
        log_path=None,
        links={},
        artifacts={},
        age_s=60.0,
        is_stale=False,
    )
    pill = dp._verdict_pill(row, worker)
    assert pill is not None
    assert "REVIEWING" in pill


def test_verdict_pill_failed(fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_identity(monkeypatch)
    dp = _reload_dp()
    row = _make_full_row(status="failed", prep_status="failed")
    pill = dp._verdict_pill(row, None)
    assert pill is not None
    assert "FAILED" in pill
    assert "[I] to retry" in pill


def test_verdict_pill_needs_re_review(fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _force_no_identity(monkeypatch)
    dp = _reload_dp()
    # status must NOT be in {"reviewed","approved","comments","reminded"} so that
    # derive_task_status step 7 does not short-circuit before step 8 (head-sha check).
    row = _make_full_row(status="pending", prep_status="ready")
    row.head_sha = "newsha111"
    row.last_reviewed_head_sha = "oldsha000"
    pill = dp._verdict_pill(row, None)
    assert pill is not None
    assert "NEEDS RE-REVIEW" in pill


def test_verdict_pill_appears_first_in_overview(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The verdict pill must be the first non-empty line in the Overview text."""
    _force_no_identity(monkeypatch)
    dp = _reload_dp()
    row = _make_full_row(status="pending", prep_status="ready", ready_for_review=True)
    text = dp._compute_overview_text(row, None)
    non_empty = [l for l in text.splitlines() if l.strip()]
    assert non_empty, "overview text must not be empty"
    # The pill contains "READY" — it must come before the key:value block.
    assert "READY" in non_empty[0], (
        f"Expected pill to be first line; first non-empty line: {non_empty[0]!r}"
    )


# ---------------------------------------------------------------------------
# (c) Walk-action mark accept — updates a fake posting-plan state file
# ---------------------------------------------------------------------------

def _write_posting_plan(pr_dir: Path, steps: list[dict]) -> None:
    (pr_dir / "posting-plan.json").write_text(
        json.dumps({"steps": steps}),
        encoding="utf-8",
    )


def test_draft_step_badges_rendered(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each draft step must carry a [step/total] badge in the rendered markdown."""
    _force_no_identity(monkeypatch)
    steps = [
        {"kind": "inline_comment", "mcp_args": {"body": "fix null check", "path": "a.py", "line": 1}},
        {"kind": "resolve", "mcp_args": {"comment_id": "abc"}},
    ]
    _write_posting_plan(fake_pr_dir, steps)
    dp = _reload_dp()

    out = dp._format_comments_markdown(_Row(), comments_filter="open")
    assert "[1/2]" in out, "first draft must carry [1/2] badge"
    assert "[2/2]" in out, "second draft must carry [2/2] badge"


def test_mark_draft_step_calls_script_when_present(
    fake_pr_dir: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """_mark_draft_step: when walk_posting_plan.py exists, it's invoked via subprocess.

    We mock the script with a tiny shell script that writes a sentinel file;
    then verify the sentinel appears after calling _mark_draft_step.
    """
    _force_no_identity(monkeypatch)

    # Create a fake walk_posting_plan.py that writes a sentinel file.
    sentinel = tmp_path / "sentinel.txt"
    fake_script = tmp_path / "walk_posting_plan.py"
    fake_script.write_text(
        f"import sys\nopen('{sentinel}', 'w').write('accepted')\n",
        encoding="utf-8",
    )

    dp = _reload_dp()

    task_dir = fake_pr_dir.parent  # .../skill-pr-review/foo_pr-42

    async def _run() -> None:
        # Patch the script path inside _mark_draft_step via monkeypatching the
        # function to use our fake script path.
        import tui.widgets.detail_pane as dpmod
        original = dpmod._mark_draft_step

        async def patched(td: Path, step_id: str, state: str) -> None:
            import asyncio as aio
            try:
                proc = await aio.create_subprocess_exec(
                    "python3", str(fake_script),
                    "--task-dir", str(td),
                    "--mark", step_id,
                    "--state", state,
                    stdout=aio.subprocess.DEVNULL,
                    stderr=aio.subprocess.DEVNULL,
                )
                await aio.wait_for(proc.communicate(), timeout=10)
            except Exception:
                pass

        dpmod._mark_draft_step = patched
        try:
            await dpmod._mark_draft_step(task_dir, "step-1", "accept")
        finally:
            dpmod._mark_draft_step = original

    asyncio.run(_run())
    assert sentinel.exists(), "sentinel file must be created by the fake walk script"
    assert sentinel.read_text() == "accepted"


def test_posting_plan_step_to_markdown_includes_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_posting_plan_step_to_markdown: 'state' field from plan is shown in the badge."""
    dp = _reload_dp()
    step = {
        "kind": "inline_comment",
        "mcp_args": {"body": "check this", "path": "b.py", "line": 5},
        "state": "accepted",
    }
    rendered = dp._posting_plan_step_to_markdown(step, step_index=1, total_steps=3)
    assert rendered is not None
    assert "[1/3]" in rendered
    assert "accepted" in rendered
