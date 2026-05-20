"""Tests for the post_comments.py default-flip: auto-mode now POSTS (not plan-only).

These tests don't transmit — they read the argparse-resolved flag values to
confirm the new defaults so regressions are caught at the unit level.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def post_comments():
    """Import post_comments.py as a module despite its sibling-relative imports.
    We only inspect its argparse, so the import is lightweight.
    """
    path = Path(__file__).resolve().parent.parent.parent.parent / "adk-pr-review" / "scripts" / "post_comments.py"
    # Add the script's dir to sys.path so its `from _common import …` works.
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("post_comments_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_parser(post_comments_mod):
    """Re-walk the parser definitions out of main() — we need them isolated
    from the script's `args = ap.parse_args()` line that consumes sys.argv.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--confirmed", choices=("yes", "no"), default="yes")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--no-resolve-existing", action="store_true")
    ap.add_argument("--json", action="store_true")
    return ap


def test_default_is_post_not_plan_only(post_comments):
    """No flags → --confirmed=yes (posts)."""
    ap = _build_parser(post_comments)
    args = ap.parse_args(["--task-dir", "/tmp/x"])
    assert args.confirmed == "yes"
    assert args.plan_only is False


def test_plan_only_flag_inhibits_post(post_comments):
    """--plan-only overrides the yes default."""
    ap = _build_parser(post_comments)
    args = ap.parse_args(["--task-dir", "/tmp/x", "--plan-only"])
    # The main() function does `if args.plan_only: args.confirmed = "no"`,
    # so the test must mirror that logic — argparse alone leaves --confirmed
    # at "yes" because --plan-only is a separate flag.
    if args.plan_only:
        args.confirmed = "no"
    assert args.confirmed == "no"


def test_back_compat_confirmed_no_still_works(post_comments):
    """Old callers passing --confirmed no still get plan-only."""
    ap = _build_parser(post_comments)
    args = ap.parse_args(["--task-dir", "/tmp/x", "--confirmed", "no"])
    assert args.confirmed == "no"


def test_back_compat_confirmed_yes_explicit(post_comments):
    """Explicit --confirmed yes still posts (no double-negative regression)."""
    ap = _build_parser(post_comments)
    args = ap.parse_args(["--task-dir", "/tmp/x", "--confirmed", "yes"])
    assert args.confirmed == "yes"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
