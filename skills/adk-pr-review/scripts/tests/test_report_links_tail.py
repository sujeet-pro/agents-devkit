"""report.py prints a Links block at the end of every review.

User request: when the review is done, print clickable URLs for the PR +
Slack so the user can click and visit directly. file:// URLs for local
artifacts so terminals auto-linkify them.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import report


def test_links_tail_with_slack_permalink(tmp_path, capsys):
    task_dir = tmp_path / "fake_pr-1"
    task_dir.mkdir()
    (task_dir / "findings.md").write_text("# findings\n")
    (task_dir / "report.md").write_text("# report\n")
    (task_dir / "queue-context.json").write_text(json.dumps({
        "slack": {
            "permalink": "https://example.slack.com/archives/C123/p1779267308866179",
            "channel_id": "C123",
        }
    }))
    pr = {"url": "https://github.com/acme/foo/pull/42"}

    report._print_links_tail(task_dir, pr)
    out = capsys.readouterr().out
    assert "Links" in out
    assert "https://github.com/acme/foo/pull/42" in out
    assert "https://example.slack.com/archives/C123/p1779267308866179" in out
    assert f"file://{task_dir.resolve()}" in out
    assert f"file://{(task_dir / 'findings.md').resolve()}" in out
    assert f"file://{(task_dir / 'report.md').resolve()}" in out


def test_links_tail_no_slack_when_unavailable(tmp_path, capsys):
    """When queue-context.json is missing, the Slack line is omitted."""
    task_dir = tmp_path / "fake_pr-2"
    task_dir.mkdir()
    (task_dir / "findings.md").write_text("# findings\n")
    pr = {"url": "https://bitbucket.org/ws/repo/pull-requests/100"}

    report._print_links_tail(task_dir, pr)
    out = capsys.readouterr().out
    assert "https://bitbucket.org/ws/repo/pull-requests/100" in out
    assert "Slack:" not in out


def test_links_tail_no_artifacts(tmp_path, capsys):
    """Missing artifact files are omitted (not a hard error)."""
    task_dir = tmp_path / "fake_pr-3"
    task_dir.mkdir()
    pr = {"url": "https://github.com/acme/foo/pull/1"}

    report._print_links_tail(task_dir, pr)
    out = capsys.readouterr().out
    assert "Findings:" not in out  # no findings.md → no line
    assert "Report:" not in out    # no report.md → no line
    assert "Task dir:" in out      # task dir always shown
    assert "PR:" in out             # PR URL always shown


def test_links_tail_pr_url_on_own_line(tmp_path, capsys):
    """The PR URL is on its own line so terminals auto-linkify it."""
    task_dir = tmp_path / "fake_pr-4"
    task_dir.mkdir()
    pr = {"url": "https://github.com/acme/foo/pull/42"}
    report._print_links_tail(task_dir, pr)
    out = capsys.readouterr().out
    pr_line = [ln for ln in out.splitlines() if "github.com/acme/foo/pull/42" in ln]
    assert len(pr_line) == 1
    # The URL is at the end of the line — terminals linkify URL prefixes.
    assert pr_line[0].strip().endswith("https://github.com/acme/foo/pull/42")
