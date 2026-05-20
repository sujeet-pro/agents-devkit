"""Tests for the importable append_decision() helper added to
scripts/decision_logger.py (improvement #4 — decision-log gap)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def dl_mod():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts"))
    import decision_logger
    return decision_logger


def test_append_decision_writes_one_line(tmp_path, monkeypatch, dl_mod):
    log_dir = tmp_path / "improve" / "learning"
    monkeypatch.setattr(dl_mod, "LOG_DIR", log_dir)
    monkeypatch.setattr(dl_mod, "LOG_FILE", log_dir / "decisions.jsonl")
    dl_mod.append_decision(
        skill="adk-pr-review", fork_id="embed_model", fork_type="inferred",
        default_offered="nomic-embed-text",
        evidence="--detailed=False",
        repo="ecomm-ssr", task_slug="ecomm-ssr_pr-42",
    )
    content = (log_dir / "decisions.jsonl").read_text(encoding="utf-8")
    lines = [ln for ln in content.splitlines() if ln.strip()]
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["skill"] == "adk-pr-review"
    assert rec["fork_id"] == "embed_model"
    assert rec["fork_type"] == "inferred"
    assert rec["repo"] == "ecomm-ssr"
    assert rec["default_offered"] == "nomic-embed-text"
    assert "ts" in rec


def test_append_decision_appends_not_overwrites(tmp_path, monkeypatch, dl_mod):
    log_dir = tmp_path / "improve" / "learning"
    monkeypatch.setattr(dl_mod, "LOG_DIR", log_dir)
    monkeypatch.setattr(dl_mod, "LOG_FILE", log_dir / "decisions.jsonl")
    for fid in ("a", "b", "c"):
        dl_mod.append_decision(skill="x", fork_id=fid, fork_type="auto-defaulted")
    content = (log_dir / "decisions.jsonl").read_text(encoding="utf-8")
    assert len([ln for ln in content.splitlines() if ln.strip()]) == 3


def test_append_decision_invalid_fork_type_drops_silently(tmp_path, monkeypatch, dl_mod, capsys):
    log_dir = tmp_path / "improve" / "learning"
    monkeypatch.setattr(dl_mod, "LOG_DIR", log_dir)
    monkeypatch.setattr(dl_mod, "LOG_FILE", log_dir / "decisions.jsonl")
    dl_mod.append_decision(skill="x", fork_id="y", fork_type="totally-bogus")
    captured = capsys.readouterr()
    assert "bad fork_type" in captured.err
    # File must not have been touched.
    assert not (log_dir / "decisions.jsonl").exists()


def test_append_decision_fail_open_on_io_error(monkeypatch, dl_mod, capsys):
    """When the log dir is unwritable, the helper must NOT raise.

    Otherwise a borked filesystem blocks every PR review.
    """
    monkeypatch.setattr(dl_mod, "LOG_DIR", Path("/proc/this-cannot-exist-12345"))
    monkeypatch.setattr(dl_mod, "LOG_FILE", Path("/proc/this-cannot-exist-12345/decisions.jsonl"))
    # Should not raise.
    dl_mod.append_decision(skill="x", fork_id="y", fork_type="inferred")


def test_append_decision_extras_passthrough(tmp_path, monkeypatch, dl_mod):
    """Arbitrary kwargs land in the record without schema validation."""
    log_dir = tmp_path / "improve" / "learning"
    monkeypatch.setattr(dl_mod, "LOG_DIR", log_dir)
    monkeypatch.setattr(dl_mod, "LOG_FILE", log_dir / "decisions.jsonl")
    dl_mod.append_decision(
        skill="x", fork_id="y", fork_type="inferred",
        prior_decisions_count=7,
    )
    rec = json.loads((log_dir / "decisions.jsonl").read_text(encoding="utf-8").strip())
    assert rec["prior_decisions_count"] == 7


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
