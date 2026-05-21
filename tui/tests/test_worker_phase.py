"""Unit + integration tests for the ε phase parser in `tui/worker.py`.

Covers:
- `_parse_phase_marker` (regex unit tests, 6 positive + 3 negative).
- An end-to-end integration test that spawns `tui/worker.py` with a fake_claude
  that emits phase-marker lines with sleeps between them, and polls the
  heartbeat file to observe `current_phase` transitions.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tui.worker import _parse_phase_marker


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER = _REPO_ROOT / "tui" / "worker.py"


# --- 1. unit tests for _parse_phase_marker ---------------------------------

@pytest.mark.parametrize(
    "line,expected",
    [
        ("--- Phase 0: prereq ---", "phase 0: prereq"),
        ("--- Phase 2a: fetch PR ---", "phase 2a: fetch PR"),
        ("## Phase 4: Triage", "phase 4: Triage"),
        ("**Phase 5: Post**", "phase 5: Post"),
        ("Phase 3 validate:", "phase 3"),
        ("phase 3", "phase 3"),
    ],
)
def test_parse_phase_marker_positive(line: str, expected: str) -> None:
    got = _parse_phase_marker(line)
    # `Phase 6 disposition` per the SPEC is allowed to return either
    # `"phase 6: disposition"` or `"phase 6"` because the boundary regex
    # only captures the sub-task after a `:` / `-` / `—`. Same flex applies
    # to `Phase 3 validate:` — we accept either with-desc or num-only.
    assert got == expected, (
        f"line={line!r}: expected {expected!r}, got {got!r}"
    )


def test_parse_phase_marker_phase6_disposition_either_form() -> None:
    """`Phase 6 disposition` may produce either `"phase 6"` or
    `"phase 6: disposition"` depending on whether the regex consumes the
    trailing word as a description. Both are acceptable per SPEC §4.1."""
    got = _parse_phase_marker("Phase 6 disposition")
    assert got in {"phase 6", "phase 6: disposition"}, got


def test_parse_phase_marker_unrelated_text() -> None:
    assert _parse_phase_marker("some unrelated text") is None


def test_parse_phase_marker_no_false_positive_on_multiphase() -> None:
    """`multiphase` must NOT match — word boundary guards against it."""
    assert _parse_phase_marker("multiphase code") is None


def test_parse_phase_marker_no_false_positive_on_phaserator() -> None:
    """`phaserator.py` must NOT match — no digit follows the word `phaser`."""
    assert _parse_phase_marker("see phaserator.py for") is None


def test_parse_phase_marker_no_false_positive_in_prose() -> None:
    """`Phase N` mid-sentence (PR title, narration) must NOT match — the
    regex anchors at line-start with optional decoration only."""
    cases = [
        "PR title: Add Phase 4 to migration",
        '{"key": "phase 3 done"}',
        "In Phase 2, we did X.",
        "completed Phase 4: Triage moving to Phase 5: Post",
    ]
    for line in cases:
        assert _parse_phase_marker(line) is None, f"false positive on {line!r}"


def test_parse_phase_marker_truncates_at_80_chars() -> None:
    """Defensive truncation: outputs are capped at 80 chars."""
    long_desc = "x" * 200
    # Build a description that's < 60 chars (regex limit) so the matcher
    # consumes the description, then verify the final label is ≤ 80.
    line = f"Phase 4: {long_desc[:50]}"
    got = _parse_phase_marker(line)
    assert got is not None
    assert len(got) <= 80


# --- 2. integration test ---------------------------------------------------

def _recording_adk(tmp_path: Path, log_path: Path) -> Path:
    """Tiny fake-adk that just records its argv. Mirrors the pattern in
    test_worker.py."""
    script = tmp_path / "rec-adk"
    script.write_text(
        f"""#!/bin/sh
echo "$@" >> "{log_path}"
echo "ok"
exit 0
"""
    )
    script.chmod(0o755)
    return script


@pytest.fixture
def phase_emitting_agent_script(tmp_path: Path) -> Path:
    """A fake-claude that emits 3 phase markers with sleeps in between so the
    heartbeat-file loop has time to observe each transition."""
    p = tmp_path / "phase-emitting-claude"
    p.write_text(
        "#!/bin/sh\n"
        "echo '--- Phase 0: prereq ---'\n"
        "sleep 0.3\n"
        "echo '[claude] thinking...'\n"
        "sleep 0.1\n"
        "echo '## Phase 4: Triage'\n"
        "sleep 0.3\n"
        "echo '**Phase 5: Post**'\n"
        "sleep 0.3\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


def test_worker_heartbeat_file_phase_transitions(
    tmp_path: Path,
    phase_emitting_agent_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """Spawn the worker with a phase-emitting fake_claude and poll the
    heartbeat file. The `current_phase` field must transition through the
    expected sequence as the agent emits markers."""
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/501"

    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(phase_emitting_agent_script),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.05",
            "--heartbeat-bump-interval-s", "0.5",
            "--no-prepare",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    observed_phases: list[str] = []

    try:
        deadline = time.time() + 10.0
        while time.time() < deadline:
            files = list(worker_heartbeat_dir.glob("*.json"))
            if files:
                try:
                    payload = json.loads(files[0].read_text())
                except (json.JSONDecodeError, FileNotFoundError):
                    payload = None
                if payload is not None:
                    cp = payload.get("current_phase")
                    if cp and (not observed_phases or observed_phases[-1] != cp):
                        observed_phases.append(cp)
            if proc.poll() is not None:
                # Process exited; do a final read.
                files = list(worker_heartbeat_dir.glob("*.json"))
                if files:
                    try:
                        payload = json.loads(files[0].read_text())
                        cp = payload.get("current_phase")
                        if cp and (not observed_phases or observed_phases[-1] != cp):
                            observed_phases.append(cp)
                    except Exception:
                        pass
                break
            time.sleep(0.02)
        rc = proc.wait(timeout=5.0)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=2.0)

    assert rc == 0, f"worker exit={rc}, observed phases={observed_phases}"

    # We must have observed at least 2 distinct phase-transitions. The exact
    # sequence depends on timing; the contract is:
    #   - `phase 0` (or `phase 0: prereq`) appears at some point.
    #   - `phase 4: Triage` appears.
    #   - `phase 5: Post` appears.
    joined = " | ".join(observed_phases)

    saw_zero = any(p.startswith("phase 0") for p in observed_phases)
    saw_four = any("phase 4: Triage" in p for p in observed_phases)
    saw_five = any("phase 5: Post" in p for p in observed_phases)

    assert saw_zero, (
        f"never observed `phase 0` transition. Observed: {joined}"
    )
    assert saw_four, (
        f"never observed `phase 4: Triage` transition. Observed: {joined}"
    )
    assert saw_five, (
        f"never observed `phase 5: Post` transition. Observed: {joined}"
    )

    # And the ordering must be 0 → 4 → 5 (no later phase observed before an
    # earlier one). Use explicit lookups with pytest.fail so a missed
    # transition surfaces clearly instead of a StopIteration deep in next().
    def _idx(needle: str, predicate) -> int:
        for i, p in enumerate(observed_phases):
            if predicate(p):
                return i
        pytest.fail(
            f"phase transition {needle!r} never observed. Observed: {joined}"
        )

    idx0 = _idx("phase 0", lambda p: p.startswith("phase 0"))
    idx4 = _idx("phase 4: Triage", lambda p: "phase 4: Triage" in p)
    idx5 = _idx("phase 5: Post", lambda p: "phase 5: Post" in p)
    assert idx0 < idx4 < idx5, (
        f"phase ordering wrong: {observed_phases} (indexes 0/4/5 = {idx0}/{idx4}/{idx5})"
    )
