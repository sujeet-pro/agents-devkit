"""v4 §6.x verbose-mode helper tests.

- setup_verbose() is no-op when enabled=False.
- When enabled=True it writes a human-readable manifest line to $ADK_DATA_HOME/logs/.
- _scrub_argv() masks values of flags whose name matches secret patterns.
- _HumanFormatter scrubs secret env-name=value patterns in message bodies
  and indents multi-line message bodies.
- Noisy 3rd-party loggers are pinned to WARNING.
"""
from __future__ import annotations

import logging
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


def test_setup_verbose_writes_human_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(_verbose, "ADK_HOME", tmp_path)
    monkeypatch.setattr(_verbose, "LOGS_DIR", tmp_path / "logs")
    # Make sure the test doesn't double-wire across runs.
    root = logging.getLogger()
    for h in list(root.handlers):
        if getattr(h, "_adk_verbose", False):
            root.removeHandler(h)

    p = _verbose.setup_verbose("pr-queue", enabled=True, argv=["--queue", "/tmp/q"])
    assert p is not None
    assert p.exists()
    body = p.read_text()
    first_line = body.splitlines()[0]
    # human-readable: `2026-…Z INFO  [adk-verbose] verb=pr-queue …`
    assert " INFO " in first_line
    assert "[adk-verbose]" in first_line
    assert "verb=pr-queue" in first_line
    assert "argv=['--queue', '/tmp/q']" in first_line

    # tear down so subsequent tests don't inherit the handler
    for h in list(root.handlers):
        if getattr(h, "_adk_verbose", False):
            root.removeHandler(h)


def test_setup_verbose_pins_noisy_loggers(tmp_path, monkeypatch):
    monkeypatch.setattr(_verbose, "ADK_HOME", tmp_path)
    monkeypatch.setattr(_verbose, "LOGS_DIR", tmp_path / "logs")
    root = logging.getLogger()
    for h in list(root.handlers):
        if getattr(h, "_adk_verbose", False):
            root.removeHandler(h)
    _verbose.setup_verbose("pr-queue", enabled=True, argv=[])
    for name in ("urllib3", "urllib3.connectionpool", "slack_sdk",
                 "slack_sdk.web.base_client", "httpx"):
        assert logging.getLogger(name).level == logging.WARNING, name
    for h in list(root.handlers):
        if getattr(h, "_adk_verbose", False):
            root.removeHandler(h)


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


def test_human_formatter_scrubs_secret_patterns_in_message():
    """A message containing 'GITHUB_TOKEN=abc' is masked in the file."""
    formatter = _verbose._HumanFormatter()
    rec = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="loaded GITHUB_TOKEN=secret_value123 from env", args=(), exc_info=None,
    )
    line = formatter.format(rec)
    assert "secret_value123" not in line
    assert "<redacted>" in line


def test_human_formatter_renders_single_line():
    formatter = _verbose._HumanFormatter()
    rec = logging.LogRecord(
        name="pr-sync", level=logging.INFO, pathname="", lineno=0,
        msg="=== step: pr-scan ===", args=(), exc_info=None,
    )
    line = formatter.format(rec)
    assert "[pr-sync]" in line
    assert "=== step: pr-scan ===" in line
    assert "\n" not in line


def test_human_formatter_indents_multiline_body():
    formatter = _verbose._HumanFormatter()
    rec = logging.LogRecord(
        name="orchestrator", level=logging.INFO, pathname="", lineno=0,
        msg="stderr:\nTraceback (most recent call last):\n  File \"x.py\"",
        args=(), exc_info=None,
    )
    out = formatter.format(rec)
    lines = out.splitlines()
    assert len(lines) == 3
    # First line carries the header + first content line.
    assert "[orchestrator] stderr:" in lines[0]
    # Continuation lines are indented two spaces.
    assert lines[1].startswith("  Traceback")
    assert lines[2].startswith("  ")


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
