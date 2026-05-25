"""Tests for ReviewRunner protocol and SubprocessRunner adapter.

Covers:
  - ReviewRunner protocol conformance (isinstance check)
  - ReviewEvent field defaults
  - SubprocessRunner event sequence: started → phase* → completed
  - SubprocessRunner emits failed on non-zero exit code
  - SubprocessRunner emits failed on FileNotFoundError (missing binary)
  - Phase markers in subprocess stdout produce ReviewEvent(kind="phase")
  - Duplicate phase labels are de-duplicated (only emitted on change)
  - PR URL is present in links on every event
  - log_path option writes subprocess output to a file
  - Invalid runner build (custom with no --agent) produces a single failed
    event with no started event
  - Existing subprocess/CLI flow (auto_run._spawn_review) still works
    independently — importing subprocess_runner does not break it
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import review_runner as rr
import subprocess_runner as sr


# ---------------------------------------------------------------------------
# Helpers — fake Popen that works without a real file descriptor
# ---------------------------------------------------------------------------

class _FakePopen:
    """Minimal Popen stand-in for unit tests.

    ``poll()`` returns ``returncode`` immediately so the
    ``while proc.poll() is None`` loop in SubprocessRunner is skipped, and
    output is consumed via the trailing drain loop (``for line in proc.stdout``).

    ``stdout`` is set to ``self`` so it is non-None and iterable, but is not a
    real file-descriptor; the selector registration inside SubprocessRunner is
    wrapped in a try/except so the failure is silently ignored and the drain
    loop handles all output.
    """

    def __init__(self, lines: list[str], returncode: int = 0) -> None:
        self.returncode = returncode
        self._lines = list(lines)
        self.stdout = self  # iterable, but not selectable

    def poll(self) -> int:
        return self.returncode

    def readline(self) -> str:
        return ""

    def __iter__(self):
        return iter(self._lines)


def _popen_ok(lines: list[str]) -> _FakePopen:
    return _FakePopen(lines, returncode=0)


def _popen_fail(lines: list[str]) -> _FakePopen:
    return _FakePopen(lines, returncode=1)


def _collect(runner_obj, pr_url: str, **opts) -> list[rr.ReviewEvent]:
    return list(runner_obj.start(pr_url, **opts))


# ---------------------------------------------------------------------------
# ReviewEvent dataclass
# ---------------------------------------------------------------------------

def test_review_event_required_fields():
    e = rr.ReviewEvent(kind="started", label="test")
    assert e.kind == "started"
    assert e.label == "test"


def test_review_event_defaults():
    e = rr.ReviewEvent(kind="completed", label="done")
    assert e.detail is None
    assert e.pct is None
    assert e.elapsed_ms is None
    assert e.links == {}


def test_review_event_links_default_is_independent():
    e1 = rr.ReviewEvent(kind="started", label="a")
    e2 = rr.ReviewEvent(kind="started", label="b")
    e1.links["pr"] = "url1"
    assert e2.links == {}, "default_factory must produce a fresh dict per instance"


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_subprocess_runner_satisfies_protocol():
    runner = sr.SubprocessRunner(runner="claude")
    assert isinstance(runner, rr.ReviewRunner)


def test_any_class_with_start_method_satisfies_protocol():
    class _MinimalRunner:
        def start(self, pr_url: str, **opts) -> list:
            return []

    assert isinstance(_MinimalRunner(), rr.ReviewRunner)


# ---------------------------------------------------------------------------
# Normal run: started → phase → completed
# ---------------------------------------------------------------------------

def test_emits_started_as_first_event(monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok([]))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    assert events[0].kind == "started"


def test_emits_completed_as_last_event_on_zero_rc(monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok([]))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    assert events[-1].kind == "completed"
    assert "rc=0" in (events[-1].detail or "")


def test_emits_failed_as_last_event_on_nonzero_rc(monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_fail([]))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    assert events[-1].kind == "failed"
    assert "rc=1" in (events[-1].detail or "")


def test_event_sequence_contains_phase_after_started(monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok([]))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    kinds = [e.kind for e in events]
    # started must appear, then at least one phase, then completed
    assert kinds[0] == "started"
    assert "phase" in kinds
    assert kinds[-1] == "completed"


# ---------------------------------------------------------------------------
# Phase marker parsing
# ---------------------------------------------------------------------------

def test_phase_markers_produce_phase_events(monkeypatch):
    output = [
        "some prefix output\n",
        "Phase 1: clone worktree\n",
        "more output\n",
        "Phase 3: build embeddings\n",
        "done\n",
    ]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    phase_labels = [e.label for e in events if e.kind == "phase"]
    assert any("phase 1" in lbl for lbl in phase_labels)
    assert any("phase 3" in lbl for lbl in phase_labels)


def test_phase_markers_with_description_include_desc(monkeypatch):
    output = ["Phase 2a: fetch PR meta\n"]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    phase_labels = [e.label for e in events if e.kind == "phase"]
    assert any("fetch PR meta" in lbl for lbl in phase_labels)


def test_duplicate_phase_labels_not_emitted_twice(monkeypatch):
    """The same phase label emitted twice in stdout produces only one event."""
    output = [
        "Phase 1: clone\n",
        "Phase 1: clone\n",  # duplicate
    ]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    phase_1_events = [e for e in events if e.kind == "phase" and "phase 1" in e.label]
    assert len(phase_1_events) == 1, "duplicate labels must not produce duplicate events"


def test_non_phase_lines_do_not_produce_phase_events(monkeypatch):
    output = ["regular output line\n", "another line without phase marker\n"]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    # Only the initial "review agent running" phase event from runner setup
    user_phases = [
        e for e in events
        if e.kind == "phase" and e.label != "review agent running"
    ]
    assert user_phases == []


# ---------------------------------------------------------------------------
# Parse-phase helper directly
# ---------------------------------------------------------------------------

def test_parse_phase_label_basic():
    assert sr._parse_phase_label("Phase 1: clone worktree\n") == "phase 1: clone worktree"


def test_parse_phase_label_with_bracket_prefix():
    assert sr._parse_phase_label("[adk-pr-review] Phase 3: build embeddings") == "phase 3: build embeddings"


def test_parse_phase_label_case_insensitive():
    assert sr._parse_phase_label("phase 2a: fetch meta") == "phase 2a: fetch meta"


def test_parse_phase_label_no_match_returns_none():
    assert sr._parse_phase_label("just a log line") is None
    assert sr._parse_phase_label("") is None


def test_parse_phase_label_strips_trailing_dashes():
    result = sr._parse_phase_label("Phase 4: validate ----")
    assert result is not None
    assert not result.endswith("-")


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------

def test_emits_failed_on_missing_binary(monkeypatch):
    def _raise(*a, **k):
        raise FileNotFoundError("claude: command not found")
    monkeypatch.setattr(sr.subprocess, "Popen", _raise)
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    assert events[-1].kind == "failed"
    assert "not on PATH" in (events[-1].detail or "")


def test_build_failure_emits_single_failed_event_no_started():
    """--runner custom without --agent raises before spawning anything."""
    runner = sr.SubprocessRunner(runner="custom", agent=None)
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    assert len(events) == 1
    assert events[0].kind == "failed"
    assert "build command failed" in events[0].label


# ---------------------------------------------------------------------------
# PR URL in links
# ---------------------------------------------------------------------------

def test_all_events_carry_pr_url_in_links(monkeypatch):
    output = ["Phase 1: clone\n"]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    pr = "https://github.com/org/repo/pull/99"
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, pr)
    for e in events:
        assert e.links.get("pr") == pr, f"event {e.kind!r} missing pr link"


# ---------------------------------------------------------------------------
# log_path option
# ---------------------------------------------------------------------------

def test_log_path_option_writes_output(tmp_path, monkeypatch):
    output = ["Phase 2: fetch meta\n", "regular line\n"]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok(output))
    log_p = tmp_path / "review.log"
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1", log_path=log_p)
    assert log_p.exists(), "log file must be created when log_path is provided"
    content = log_p.read_text()
    assert "Phase 2" in content


def test_log_path_not_provided_does_not_create_file(tmp_path, monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok([]))
    runner = sr.SubprocessRunner(runner="claude")
    _collect(runner, "https://github.com/org/repo/pull/1")
    # No log files should appear in tmp_path since we did not pass log_path
    assert list(tmp_path.iterdir()) == []


def test_log_path_created_even_on_failure(tmp_path, monkeypatch):
    output = ["Phase 1: clone\n"]
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_fail(output))
    log_p = tmp_path / "fail.log"
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1", log_path=log_p)
    assert log_p.exists()
    assert events[-1].kind == "failed"


# ---------------------------------------------------------------------------
# elapsed_ms
# ---------------------------------------------------------------------------

def test_completed_event_has_elapsed_ms(monkeypatch):
    monkeypatch.setattr(sr.subprocess, "Popen", lambda *a, **k: _popen_ok([]))
    runner = sr.SubprocessRunner(runner="claude")
    events = _collect(runner, "https://github.com/org/repo/pull/1")
    completed = next(e for e in events if e.kind == "completed")
    assert completed.elapsed_ms is not None
    assert completed.elapsed_ms >= 0


# ---------------------------------------------------------------------------
# Isolation: importing subprocess_runner does not break auto_run
# ---------------------------------------------------------------------------

def test_auto_run_import_unaffected_by_subprocess_runner():
    """Importing subprocess_runner must not break auto_run.

    This guards against inadvertent import side-effects that might break the
    existing _spawn_review path.
    """
    import auto_run  # noqa: PLC0415
    assert hasattr(auto_run, "_spawn_review"), "_spawn_review must still exist"
    assert hasattr(auto_run, "_parse_phase_marker"), "_parse_phase_marker must still exist"


def test_phase_regex_stays_in_sync_with_auto_run():
    """The local _PHASE_RE and auto_run._PHASE_RE should parse identically.

    This test fails if the two implementations drift, reminding maintainers to
    update subprocess_runner._PHASE_RE as well.
    """
    import auto_run  # noqa: PLC0415
    cases = [
        ("Phase 1: clone worktree\n", True),
        ("phase 3: build embeddings", True),
        ("[adk] Phase 2a — fetch meta", True),
        ("just output", False),
        ("", False),
    ]
    for line, should_match in cases:
        local_result = sr._parse_phase_label(line)
        auto_result = auto_run._parse_phase_marker(line)
        both_match = (local_result is not None) == (auto_result is not None)
        assert both_match, (
            f"regex mismatch for {line!r}: "
            f"local={local_result!r} auto_run={auto_result!r}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
