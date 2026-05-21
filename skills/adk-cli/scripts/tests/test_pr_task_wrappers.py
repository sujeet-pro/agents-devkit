"""adk pr-task triage/post/report/resolve-comments — wrapper tests.

Each wrapper resolves pr_url → task_dir then shells out to the corresponding
adk-pr-review script. Verifies the URL → task_dir mapping + the forwarded
flags shape.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import pytest
import pr_task


@pytest.fixture
def fake_task(tmp_path, monkeypatch):
    """Create a fake task folder + point pr_task at it."""
    monkeypatch.setattr(pr_task, "PR_REVIEW_ROOT", tmp_path / "skill-pr-review")
    # Wire the shared _common.task_dir_for to the same fake root.
    import _common
    monkeypatch.setattr(_common, "PR_REVIEW_ROOT", tmp_path / "skill-pr-review")
    task_dir = tmp_path / "skill-pr-review" / "foo_pr-42"
    task_dir.mkdir(parents=True)
    return task_dir


def test_triage_resolves_url_and_forwards_init(fake_task, monkeypatch):
    with patch.object(pr_task, "_forward", return_value=0) as m:
        args = argparse.Namespace(
            pr_url="https://github.com/acme/foo/pull/42",
            init=True, finalize=False, default_state=None,
            mark=None, state=None, list=False, show=None, render=None,
            rewrite=None, fields_json=None, filter_state=None,
            include_content=False,
        )
        rc = pr_task.cmd_triage(args)
        assert rc == 0
        script, fwd_args = m.call_args[0]
        assert script == pr_task.TRIAGE_PY
        assert "--task-dir" in fwd_args
        assert str(fake_task) in fwd_args
        assert "--init" in fwd_args


def test_triage_forwards_finalize_and_default_state(fake_task):
    with patch.object(pr_task, "_forward", return_value=0) as m:
        args = argparse.Namespace(
            pr_url="https://github.com/acme/foo/pull/42",
            init=False, finalize=True, default_state="accept",
            mark=None, state=None, list=False, show=None, render=None,
            rewrite=None, fields_json=None, filter_state=None,
            include_content=False,
        )
        pr_task.cmd_triage(args)
        fwd_args = m.call_args[0][1]
        assert "--finalize" in fwd_args
        assert "--default-state" in fwd_args
        assert "accept" in fwd_args


def test_post_forwards_all_flags(fake_task):
    with patch.object(pr_task, "_forward", return_value=0) as m:
        args = argparse.Namespace(
            pr_url="https://github.com/acme/foo/pull/42",
            no_post=True, use_mcp=True, no_resolve_existing=True,
            no_slack_summary=True, no_approve=False,
        )
        pr_task.cmd_post(args)
        fwd_args = m.call_args[0][1]
        assert "--plan-only" in fwd_args
        assert "--use-mcp" in fwd_args
        assert "--no-resolve-existing" in fwd_args
        assert "--no-slack-summary" in fwd_args


def test_post_no_approve_sets_env(fake_task, monkeypatch):
    """--no-approve sets ADK_NO_APPROVE in the env so post_comments can read it."""
    monkeypatch.delenv("ADK_NO_APPROVE", raising=False)
    with patch.object(pr_task, "_forward", return_value=0):
        args = argparse.Namespace(
            pr_url="https://github.com/acme/foo/pull/42",
            no_post=False, use_mcp=False, no_resolve_existing=False,
            no_slack_summary=False, no_approve=True,
        )
        pr_task.cmd_post(args)
    import os
    assert os.environ.get("ADK_NO_APPROVE") == "1"


def test_report_forwards_merge_if_approved(fake_task):
    with patch.object(pr_task, "_forward", return_value=0) as m:
        args = argparse.Namespace(
            pr_url="https://github.com/acme/foo/pull/42",
            merge_if_approved=True,
        )
        pr_task.cmd_report(args)
        script, fwd_args = m.call_args[0]
        assert script == pr_task.REPORT_PY
        assert "--merge-if-approved" in fwd_args


def test_resolve_comments_just_forwards_task_dir(fake_task):
    with patch.object(pr_task, "_forward", return_value=0) as m:
        args = argparse.Namespace(pr_url="https://github.com/acme/foo/pull/42")
        pr_task.cmd_resolve_comments(args)
        script, fwd_args = m.call_args[0]
        assert script == pr_task.RESOLVER_PY
        assert "--task-dir" in fwd_args


def test_task_dir_or_die_fails_on_missing_folder(fake_task):
    # task_dir for #99 doesn't exist
    with pytest.raises(SystemExit):
        pr_task._task_dir_or_die("https://github.com/acme/foo/pull/99")


def test_task_dir_or_die_fails_on_bad_url(fake_task):
    with pytest.raises(SystemExit):
        pr_task._task_dir_or_die("not-a-pr-url")
