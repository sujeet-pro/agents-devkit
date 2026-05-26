"""Tests for pr_review_dir() and pr_review_file() helpers.

PR-review-specific files live in `<task_dir>/pr-review/`.
"""
from __future__ import annotations

from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent.parent.parent / "adk-pr-review" / "scripts"))

from _common import pr_review_dir, pr_review_file, PR_REVIEW_FILES


def test_pr_review_dir_creates_subfolder(tmp_path):
    """pr_review_dir(task_dir) returns task_dir/pr-review and creates it."""
    task_dir = tmp_path / "fake_pr-1"
    task_dir.mkdir()
    out = pr_review_dir(task_dir)
    assert out == task_dir / "pr-review"
    assert out.exists() and out.is_dir()


def test_pr_review_file_prefers_v4_location(tmp_path):
    """When the v4 location exists, pr_review_file returns it."""
    task_dir = tmp_path / "fake_pr-2"
    (task_dir / "pr-review").mkdir(parents=True)
    (task_dir / "pr-review" / "pr.json").write_text('{"id": 1}', encoding="utf-8")
    p = pr_review_file(task_dir, "pr.json")
    assert p == task_dir / "pr-review" / "pr.json"
    assert p.exists()


def test_pr_review_file_returns_v4_path_for_brand_new_file(tmp_path):
    """When the file doesn't yet exist, pr_review_file returns the v4 path
    (and mkdir's its parent on demand)."""
    task_dir = tmp_path / "fake_pr-4"
    task_dir.mkdir()
    p = pr_review_file(task_dir, "findings.json")
    assert p == task_dir / "pr-review" / "findings.json"
    assert not p.exists()
    assert p.parent.exists()


def test_pr_review_files_set_covers_known_files():
    """The PR_REVIEW_FILES set lists every PR-review artifact that lives in
    the ``pr-review/`` subfolder. ``state.json`` and ``review.log`` are
    intentionally NOT in this set — they live at the task root alongside
    ``code/`` and ``code-index/``, mirroring the v4 layout."""
    expected = {
        "pr.json", "pr-comments.json", "diff.patch", "precis.md",
        "findings.json", "validated-findings.json", "initial-findings.json",
        "findings-final.json", "validation-report.json",
        "triage.json", "triage-state.json",
        "posting-plan.json", "post-result.json", "comment-actions.json",
        "findings.md", "report.md", "queue-context.json",
    }
    assert expected <= PR_REVIEW_FILES


def test_brand_new_task_uses_v4_layout(tmp_path):
    """A task folder with no existing PR files uses the v4 layout."""
    task = tmp_path / "fresh_pr-7"
    task.mkdir()
    p = pr_review_file(task, "pr.json")
    assert p == task / "pr-review" / "pr.json"
    # Parent directory created on demand.
    assert (task / "pr-review").exists()
