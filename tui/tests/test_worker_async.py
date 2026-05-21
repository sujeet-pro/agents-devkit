"""Tests for the S-1/M-3 async-streaming refactor of tui/worker.py — θ.

These tests exercise the runtime behavior:
- M-3: prepare stdout is streamed line-by-line (NOT buffered).
- S-1: SIGTERM mid-prepare triggers a release with --status error.
- Invariant: SIGTERM before claim completes does NOT call release.
"""
from __future__ import annotations

import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER = _REPO_ROOT / "tui" / "worker.py"


def _recording_adk(
    tmp_path: Path,
    log_path: Path,
    *,
    delay_on: dict[str, float] | None = None,
    rc: int = 0,
    fail_on: list[str] | None = None,
) -> Path:
    """Build a fake-adk shell script that appends its argv to `log_path` and
    optionally sleeps mid-execution between echoes when its argv matches a key
    in `delay_on`. Emits one line BEFORE the sleep, one after — so streaming
    can be observed.

    delay_on: { 'prepare': 2.0 } → sleep 2s during `pr-task prepare`.
    """
    delay_on = delay_on or {}
    fail_pattern = "|".join(fail_on) if fail_on else "__NEVER__"

    delay_block = ""
    for key, secs in delay_on.items():
        delay_block += (
            f'case "$*" in *{key}*)\n'
            f'  echo "[adk] {key} starting"\n'
            f"  sleep {secs}\n"
            f'  echo "[adk] {key} step 2"\n'
            f"  sleep {secs}\n"
            f'  echo "[adk] {key} step 3"\n'
            f"  ;; \n"
            f"esac\n"
        )

    script = tmp_path / "rec-adk"
    script.write_text(
        "#!/bin/sh\n"
        f'echo "$@" >> "{log_path}"\n'
        f"{delay_block}"
        f"case \"$*\" in *{fail_pattern}*) exit {rc};; esac\n"
        'echo "ok"\n'
        "exit 0\n"
    )
    script.chmod(0o755)
    return script


def _read_log(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [ln for ln in log_path.read_text().splitlines() if ln]


def test_streamed_prepare_output_arrives_line_by_line(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """M-3 fix: prepare stdout must stream, not buffer until exit.

    The fake adk emits 3 lines with 0.4 s sleeps between them during prepare.
    We readline() the worker's stdout and timestamp each line. The 3 prepare
    lines must arrive with > 0.2 s gaps — proving streaming.
    """
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path, delay_on={"prepare": 0.4})
    pr_url = "https://github.com/acme/foo/pull/200"

    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(fake_claude_script),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        lines: list[tuple[float, str]] = []
        deadline = time.time() + 15.0
        start = time.time()
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            lines.append((time.time() - start, line.rstrip("\n")))
            if "(review exited" in line:
                break
        rc = proc.wait(timeout=5.0)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=2.0)

    assert rc == 0, "\n".join(ln for _, ln in lines)

    # Filter to just the "[adk] prepare" lines (these are the ones we control
    # the spacing of). Confirm we saw all 3 with monotonically increasing ts.
    prepare_lines = [(t, ln) for t, ln in lines if "[adk] prepare" in ln]
    assert len(prepare_lines) == 3, (
        f"expected 3 prepare lines, got {len(prepare_lines)}.\n"
        f"all lines:\n" + "\n".join(f"{t:.3f}: {ln}" for t, ln in lines)
    )

    # Each pair of adjacent prepare lines should be separated by > 0.2 s in
    # arrival time. If output were buffered until prepare exits, all three
    # would arrive within a few ms of each other.
    for (t1, _), (t2, _) in zip(prepare_lines, prepare_lines[1:]):
        gap = t2 - t1
        assert gap > 0.2, (
            f"prepare lines arrived too fast (gap={gap:.3f}s) — looks buffered.\n"
            "all lines:\n" + "\n".join(f"{t:.3f}: {ln}" for t, ln in lines)
        )


def test_sigterm_mid_prepare_releases_lock(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """S-1 fix: when SIGTERM arrives during prepare, the worker must release
    the lock (with --status error) and exit 130. Validates the signal handler
    is installed BEFORE prepare runs.
    """
    log_path = tmp_path / "adk.log"
    # Prepare emits an initial line, sleeps 3 s, emits another line.
    fake_adk = _recording_adk(tmp_path, log_path, delay_on={"prepare": 3.0})
    pr_url = "https://github.com/acme/foo/pull/201"

    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(fake_claude_script),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    saw_prepare_line = False
    captured: list[str] = []
    try:
        # Wait until we see the first [adk] prepare line (so we know we're
        # actually inside the prepare call when we SIGTERM).
        deadline = time.time() + 5.0
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            captured.append(line.rstrip("\n"))
            if "[adk] prepare starting" in line:
                saw_prepare_line = True
                break

        if not saw_prepare_line:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
            pytest.fail(
                "never saw '[adk] prepare starting' before SIGTERM.\n"
                "captured:\n" + "\n".join(captured)
            )

        proc.send_signal(signal.SIGTERM)

        # Drain remaining stdout while waiting for exit.
        try:
            tail, _ = proc.communicate(timeout=8.0)
            if tail:
                captured.append(tail.rstrip("\n"))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2.0)
            pytest.fail(
                "worker did not exit within 8 s of SIGTERM mid-prepare.\n"
                "captured:\n" + "\n".join(captured)
            )

        rc = proc.returncode
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=2.0)

    assert rc == 130, (
        f"expected rc=130 on SIGTERM mid-prepare; got {rc}\n"
        "captured:\n" + "\n".join(captured)
    )

    log = _read_log(log_path)
    joined = "\n".join(log)
    release_lines = [ln for ln in log if "pr-queue release" in ln]
    assert release_lines, (
        "no release call recorded after SIGTERM mid-prepare.\n"
        f"adk log:\n{joined}\n"
        "captured:\n" + "\n".join(captured)
    )
    assert any("--status error" in ln for ln in release_lines), (
        f"release was not called with --status error.\n{joined}"
    )


def test_sigterm_before_claim_releases_nothing(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """Invariant: if the worker is killed before the claim completes, NO
    release call should appear in the adk log (nothing was acquired).

    Real-world shape: the TUI sends SIGTERM, waits a grace period, then SIGKILL
    if the worker hasn't exited. Here we emulate that — the in-flight claim
    subprocess is not signalled by Popen.send_signal (it stays orphaned),
    so after a grace period we SIGKILL the worker. Whatever the exit code, the
    invariant under test is: no release was logged.
    """
    log_path = tmp_path / "adk.log"
    # Claim hangs for 20 s — long enough that it can't possibly complete
    # before we kill the worker.
    fake_adk = _recording_adk(tmp_path, log_path, delay_on={"claim": 20.0})
    pr_url = "https://github.com/acme/foo/pull/202"

    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(fake_claude_script),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
            "--no-prepare",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    captured: list[str] = []
    try:
        # Wait for the [adk] claim line so we know claim is in flight.
        deadline = time.time() + 5.0
        saw_claim_line = False
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            captured.append(line.rstrip("\n"))
            if "[adk] claim starting" in line:
                saw_claim_line = True
                break

        if not saw_claim_line:
            proc.kill()
            proc.wait(timeout=2.0)
            pytest.fail(
                "never saw '[adk] claim starting' before signalling.\n"
                "captured:\n" + "\n".join(captured)
            )

        # Send SIGTERM. Worker's signal handler sets sig_received but cannot
        # cancel the in-flight claim subprocess (it has no handle to it). The
        # claim child stays orphaned. After a 2 s grace period, SIGKILL the
        # worker — mimicking how the TUI will escalate.
        proc.send_signal(signal.SIGTERM)
        try:
            rc = proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                rc = proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                pytest.fail(
                    "worker did not exit within 4 s of SIGTERM+SIGKILL.\n"
                    "captured:\n" + "\n".join(captured)
                )
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=2.0)

    # Drain whatever's left in stdout (best-effort; worker may have been killed
    # before flushing).
    try:
        tail = proc.stdout.read()
        if tail:
            captured.append(tail.rstrip("\n"))
    except Exception:
        pass

    # The contract under test: NO release call appears in the adk log.
    log = _read_log(log_path)
    joined = "\n".join(log)
    release_lines = [ln for ln in log if "pr-queue release" in ln]
    assert not release_lines, (
        f"release call should NOT happen when claim never completed.\n"
        f"adk log:\n{joined}\n"
        "captured:\n" + "\n".join(captured)
    )
    # Worker exited (one way or another) — definitely not rc=0.
    assert rc != 0, (
        f"expected non-zero exit; got {rc}\n"
        "captured:\n" + "\n".join(captured)
    )
