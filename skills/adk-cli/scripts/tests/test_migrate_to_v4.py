"""P7: migrate_to_v4.py end-to-end test.

Covers:
  * Area dir rename (pr-reviews → skill-pr-review, etc.).
  * Task folder restructure (well-known files move into pr-review/).
  * Empty memory/ removal.
  * Idempotent re-run.
  * Conflict handling (both legacy + v4 present).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
MIGRATOR = REPO_ROOT / "scripts" / "migrate_to_v4.py"


def _run(home: Path, *args: str) -> dict:
    env = {**os.environ, "ADK_HOME": str(home)}
    cp = subprocess.run(
        [sys.executable, str(MIGRATOR), *args],
        env=env, capture_output=True, text=True, check=False,
    )
    assert cp.returncode in (0, 1), f"unexpected rc={cp.returncode}: {cp.stderr}"
    return json.loads(cp.stdout)


def test_dry_run_no_side_effects(tmp_path):
    """--dry-run reports what would happen but doesn't touch disk."""
    (tmp_path / "pr-reviews" / "foo_pr-1").mkdir(parents=True)
    (tmp_path / "pr-reviews" / "foo_pr-1" / "pr.json").write_text("{}")
    (tmp_path / "memory").mkdir()
    summary = _run(tmp_path, "--dry-run")
    assert summary["dry_run"] is True
    assert summary["done"] == 0
    assert summary["would_do"] >= 1
    # Disk unchanged.
    assert (tmp_path / "pr-reviews" / "foo_pr-1" / "pr.json").exists()
    assert not (tmp_path / "skill-pr-review").exists()


def test_live_migration_renames_areas_and_moves_files(tmp_path):
    (tmp_path / "pr-reviews" / "foo_pr-1").mkdir(parents=True)
    (tmp_path / "pr-reviews" / "foo_pr-1" / "pr.json").write_text("{}")
    (tmp_path / "pr-reviews" / "foo_pr-1" / "diff.patch").write_text("")
    (tmp_path / "pr-reviews" / "foo_pr-1" / "code-index").mkdir()
    (tmp_path / "memory").mkdir()
    (tmp_path / "investigations").mkdir()

    summary = _run(tmp_path, "--yes")

    # Area dirs renamed.
    assert (tmp_path / "skill-pr-review" / "foo_pr-1").exists()
    assert (tmp_path / "skill-investigate").exists()
    assert not (tmp_path / "pr-reviews").exists()
    assert not (tmp_path / "investigations").exists()
    # Files moved into pr-review/ subfolder.
    assert (tmp_path / "skill-pr-review" / "foo_pr-1" / "pr-review" / "pr.json").exists()
    assert (tmp_path / "skill-pr-review" / "foo_pr-1" / "pr-review" / "diff.patch").exists()
    # code-index/ stays at the top (NOT in PR_REVIEW_FILES).
    assert (tmp_path / "skill-pr-review" / "foo_pr-1" / "code-index").exists()
    # Empty memory/ removed.
    assert not (tmp_path / "memory").exists()
    # Summary shape.
    assert summary["errors"] == 0
    assert summary["done"] > 0


def test_idempotent_second_run_is_no_op(tmp_path):
    (tmp_path / "pr-reviews" / "foo_pr-1").mkdir(parents=True)
    (tmp_path / "pr-reviews" / "foo_pr-1" / "pr.json").write_text("{}")
    s1 = _run(tmp_path, "--yes")
    s2 = _run(tmp_path, "--yes")
    assert s1["done"] >= 2
    assert s2["done"] == 0
    assert s2["would_do"] == 0
    assert s2["errors"] == 0


def test_non_empty_memory_preserved(tmp_path):
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "MEMORY.md").write_text("# user notes\n")
    summary = _run(tmp_path, "--yes")
    assert (tmp_path / "memory" / "MEMORY.md").exists()
    assert any(r["action"] == "skip_non_empty" for r in summary["details"])


def test_refuses_without_yes_flag(tmp_path):
    """Refuse to run live without --yes (or --dry-run)."""
    env = {**os.environ, "ADK_HOME": str(tmp_path)}
    cp = subprocess.run(
        [sys.executable, str(MIGRATOR)],
        env=env, capture_output=True, text=True, check=False,
    )
    assert cp.returncode == 2


def test_conflict_when_both_legacy_and_v4_present(tmp_path):
    (tmp_path / "pr-reviews").mkdir()
    (tmp_path / "skill-pr-review").mkdir()
    summary = _run(tmp_path, "--yes")
    assert any(r["action"] == "skip_conflict" for r in summary["details"])
    # Neither dir touched.
    assert (tmp_path / "pr-reviews").exists()
    assert (tmp_path / "skill-pr-review").exists()
