"""Tests for `_read_manifest_model` in prepare_task.py — the helper that lets a
re-run of `adk pr-task prepare URL` (no flags) inherit the embed model the
index was built with, instead of erroring out with a model-mismatch.

Why this matters: the user's contract is "operations should be incremental".
If the first prepare run was `--detailed` (bge-m3) and the second is plain
prepare, today's code would default to nomic-embed-text and the embedder
would refuse the incremental add. The manifest peek closes that gap.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import prepare_task


def _seed_manifest(tmp_path: Path, *, model: str, repo: str, pr_number: int,
                   monkeypatch) -> None:
    """Write a fake index manifest at the path prepare_task will look up."""
    task_dir = tmp_path / f"{repo}_pr-{pr_number}"
    (task_dir / "code-index").mkdir(parents=True)
    (task_dir / "code-index" / "meta.json").write_text(
        json.dumps({"model": model, "dim": 768, "rows": 1}), encoding="utf-8")
    # Redirect task_dir_for to point inside tmp_path.
    monkeypatch.setattr(prepare_task, "task_dir_for",
                        lambda r, n: tmp_path / f"{r}_pr-{n}")


def test_returns_none_when_no_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(prepare_task, "task_dir_for",
                        lambda r, n: tmp_path / "does-not-exist")
    assert prepare_task._read_manifest_model("https://github.com/acme/foo/pull/1") is None


def test_returns_model_from_manifest(tmp_path, monkeypatch):
    _seed_manifest(tmp_path, model="bge-m3", repo="foo", pr_number=42,
                   monkeypatch=monkeypatch)
    assert prepare_task._read_manifest_model("https://github.com/acme/foo/pull/42") == "bge-m3"


def test_returns_none_for_unparseable_url(monkeypatch):
    # An obviously-bad URL → parse_pr_url raises → helper swallows + returns None.
    assert prepare_task._read_manifest_model("not a url at all") is None


def test_returns_none_for_no_url(monkeypatch):
    assert prepare_task._read_manifest_model(None) is None


def test_returns_none_when_manifest_corrupt(tmp_path, monkeypatch):
    """A malformed meta.json shouldn't crash the helper — model resolution
    falls back to the config default, just as if no manifest existed."""
    task_dir = tmp_path / "foo_pr-1"
    (task_dir / "code-index").mkdir(parents=True)
    (task_dir / "code-index" / "meta.json").write_text("{ this is not json",
                                                       encoding="utf-8")
    monkeypatch.setattr(prepare_task, "task_dir_for",
                        lambda r, n: tmp_path / f"{r}_pr-{n}")
    assert prepare_task._read_manifest_model("https://github.com/acme/foo/pull/1") is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
