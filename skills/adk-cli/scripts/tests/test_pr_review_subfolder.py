"""P4 exit-criterion tests: pr_review_dir() and pr_review_file() helpers.

v4 §3: PR-review-specific files live in `<task_dir>/pr-review/`.
P7's data migration moves existing files in; until then, pr_review_file()
falls back to the legacy top-level path for reads.
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


def test_pr_review_file_falls_back_to_legacy_when_v4_absent(tmp_path):
    """When only the legacy top-level file exists, pr_review_file returns the
    legacy path. This is the read-shim that preserves the user's in-flight
    task folders until P7's migration moves them."""
    task_dir = tmp_path / "fake_pr-3"
    task_dir.mkdir()
    (task_dir / "pr.json").write_text('{"id": 2}', encoding="utf-8")
    p = pr_review_file(task_dir, "pr.json")
    assert p == task_dir / "pr.json"
    assert p.exists()


def test_pr_review_file_defaults_to_v4_when_neither_exists(tmp_path):
    """When the file doesn't exist anywhere, pr_review_file returns the v4
    location (where a new write would land)."""
    task_dir = tmp_path / "fake_pr-4"
    task_dir.mkdir()
    p = pr_review_file(task_dir, "findings.json")
    assert p == task_dir / "pr-review" / "findings.json"
    assert not p.exists()


def test_pr_review_files_set_covers_known_files():
    """The PR_REVIEW_FILES set lists every file the skill writes."""
    expected = {
        "pr.json", "pr-comments.json", "diff.patch", "precis.md",
        "findings.json", "validated-findings.json", "initial-findings.json",
        "findings-final.json", "validation-report.json",
        "triage.json", "triage-state.json",
        "posting-plan.json", "post-result.json", "comment-actions.json",
        "findings.md", "report.md", "state.json", "queue-context.json",
        "review.log",
    }
    assert expected <= PR_REVIEW_FILES
