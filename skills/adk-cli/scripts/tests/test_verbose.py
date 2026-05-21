"""v4 §6.x verbose-mode helper tests.

- setup_verbose() is no-op when enabled=False.
- When enabled=True it writes a JSON-lines manifest to ~/.agents-devkit/logs/.
- _scrub_argv() masks values of flags whose name matches secret patterns.
- _JsonLinesFormatter scrubs secret env-name=value patterns in message bodies.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import _verbose


def test_setup_verbose_disabled_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("ADK_HOME", str(tmp_path))
    monkeypatch.setattr(_verbose, "ADK_HOME", tmp_path)
    monkeypatch.setattr(_verbose, "LOGS_DIR", tmp_path / "logs")
    out = _verbose.setup_verbose("pr-queue", enabled=False)
    assert out is None
    assert not (tmp_path / "logs").exists()


def test_setup_verbose_writes_jsonl_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(_verbose, "ADK_HOME", tmp_path)
    monkeypatch.setattr(_verbose, "LOGS_DIR", tmp_path / "logs")
    p = _verbose.setup_verbose("pr-queue", enabled=True, argv=["--queue", "/tmp/q"])
    assert p is not None
    assert p.exists()
    body = p.read_text()
    first_line = body.splitlines()[0]
    record = json.loads(first_line)
    assert record["level"] == "INFO"
    assert record["name"] == "adk-verbose"
    assert "verb=pr-queue" in record["msg"]
    assert "argv=['--queue', '/tmp/q']" in record["msg"]


def test_scrub_argv_masks_separated_value():
    argv = ["--queue", "/tmp/q", "--api-token", "secret123"]
    out = _verbose._scrub_argv(argv)
    assert out[3] == "<redacted>"
    assert "secret123" not in out


def test_scrub_argv_masks_inline_value():
    argv = ["--queue=/tmp/q", "--api-token=secret123"]
    out = _verbose._scrub_argv(argv)
    assert out[1] == "--api-token=<redacted>"
    assert "secret123" not in str(out)


def test_scrub_argv_leaves_non_secret_flags_alone():
    argv = ["--queue", "/tmp/q", "--max-reviews", "5"]
    out = _verbose._scrub_argv(argv)
    assert out == argv


def test_jsonl_formatter_scrubs_secret_patterns_in_message():
    """A message containing 'GITHUB_TOKEN=abc' is masked in the file."""
    formatter = _verbose._JsonLinesFormatter()
    rec = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="loaded GITHUB_TOKEN=secret_value123 from env", args=(), exc_info=None,
    )
    line = formatter.format(rec)
    data = json.loads(line)
    assert "secret_value123" not in data["msg"]
    assert "<redacted>" in data["msg"]


def test_is_secret_name_recognises_suffixes():
    assert _verbose._is_secret_name("GITHUB_TOKEN")
    assert _verbose._is_secret_name("STATSIG_API_KEY")
    assert _verbose._is_secret_name("MY_PASSWORD")
    assert _verbose._is_secret_name("FOO_CRED")
    assert _verbose._is_secret_name("BAR_PAT")
    assert _verbose._is_secret_name("BAZ_SECRET")
    assert not _verbose._is_secret_name("PATH")
    assert not _verbose._is_secret_name("HOME")
    assert not _verbose._is_secret_name("PR_URL")
