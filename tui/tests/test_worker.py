"""Unit + integration tests for `tui/worker.py` — δ.

Each test invokes the worker as a real subprocess (`python3 tui/worker.py …`)
with fake `--adk-bin` + `--agent-bin` scripts so no real `claude -p` / `adk`
calls happen. The fake_adk used here records its argv to a logfile so the
release/heartbeat/claim verbs can be asserted on.
"""
from __future__ import annotations

import json
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
    rc: int = 0,
    fail_on: list[str] | None = None,
) -> Path:
    """Build a fake-adk shell script that appends its argv to `log_path` and
    exits 0 unless one of the `fail_on` substrings appears in its argv (in
    which case it exits `rc`).
    """
    fail_pattern = "|".join(fail_on) if fail_on else "__NEVER__"
    script = tmp_path / "rec-adk"
    script.write_text(
        f"""#!/bin/sh
echo "$@" >> "{log_path}"
case "$*" in *{fail_pattern}*) exit {rc};; esac
echo "ok"
exit 0
"""
    )
    script.chmod(0o755)
    return script


def _read_log(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [ln for ln in log_path.read_text().splitlines() if ln]


def _run_worker(
    *args: str,
    timeout: float = 15.0,
) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(WORKER), *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# --- 1. happy path ---------------------------------------------------------

def test_happy_path_runs_claim_review_release(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/42"

    result = _run_worker(
        pr_url,
        "--adk-bin", str(fake_adk),
        "--agent-bin", str(fake_claude_script),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--heartbeat-file-interval-s", "0.1",
        "--heartbeat-bump-interval-s", "0.5",
        "--no-prepare",
    )

    assert result.returncode == 0, (
        f"worker exit={result.returncode}\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    out = result.stdout
    assert f"(claimed: {pr_url})" in out, out
    assert f"$ " in out and str(fake_claude_script) in out, out
    assert "[claude] phase 2: querying" in out, out
    assert "[claude] phase 5: posting comments" in out, out
    assert "[claude] phase 6: report" in out, out
    assert "(review exited rc=0)" in out, out
    assert f"(released: {pr_url})" in out, out

    log = _read_log(log_path)
    joined = "\n".join(log)
    assert "pr-queue claim" in joined, joined
    assert "pr-queue release" in joined, joined

    # Heartbeat file removed on clean exit.
    assert list(worker_heartbeat_dir.glob("*.json")) == []


# --- 2. heartbeat file ------------------------------------------------------

def test_heartbeat_file_written_mid_run_and_cleaned_on_exit(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)

    # An agent that sleeps long enough that we can peek at the heartbeat dir
    # mid-run, but short enough to keep the test fast.
    slow = tmp_path / "slow-claude"
    slow.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "sleep 1.5\n"
        "echo '[claude] done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    pr_url = "https://github.com/acme/foo/pull/77"

    proc = subprocess.Popen(
        [
            sys.executable, str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(slow),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
            "--no-prepare",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Poll for a heartbeat file while the agent sleeps.
    found: dict | None = None
    deadline = time.time() + 3.0
    while time.time() < deadline:
        files = list(worker_heartbeat_dir.glob("*.json"))
        if files:
            try:
                found = json.loads(files[0].read_text())
            except json.JSONDecodeError:
                found = None
            if found is not None:
                break
        time.sleep(0.05)
    try:
        assert found is not None, "heartbeat file never appeared mid-run"
        assert found.get("pid"), found
        assert found.get("pr_url") == pr_url, found
        assert found.get("task_type") == "review", found
        # current_phase is "review" or another stage but must be present.
        assert "current_phase" in found, found
    finally:
        # Always reap.
        try:
            rc = proc.wait(timeout=10.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2.0)
            raise

    assert rc == 0
    # File removed after clean exit.
    assert list(worker_heartbeat_dir.glob("*.json")) == [], (
        "heartbeat file should be cleaned up on clean exit"
    )


# --- 3. claim failure -------------------------------------------------------

def test_claim_failure_exits_2(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    # rec-adk fails (exit 2) when argv contains "claim".
    fake_adk = _recording_adk(tmp_path, log_path, rc=2, fail_on=["claim"])
    pr_url = "https://github.com/acme/foo/pull/43"

    result = _run_worker(
        pr_url,
        "--adk-bin", str(fake_adk),
        "--agent-bin", str(fake_claude_script),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--heartbeat-file-interval-s", "0.1",
        "--heartbeat-bump-interval-s", "0.5",
        "--no-prepare",
    )
    assert result.returncode == 2, (
        f"expected rc=2 on claim failure; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "(error: claim failed" in result.stdout, result.stdout
    # Agent should never have been invoked.
    assert "[claude]" not in result.stdout


# --- 4. agent failure -------------------------------------------------------

def test_agent_failure_releases_with_status_error(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)

    failing_claude = tmp_path / "bad-claude"
    failing_claude.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "echo '[claude] something exploded'\n"
        "exit 1\n"
    )
    failing_claude.chmod(0o755)
    pr_url = "https://github.com/acme/foo/pull/44"

    result = _run_worker(
        pr_url,
        "--adk-bin", str(fake_adk),
        "--agent-bin", str(failing_claude),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--heartbeat-file-interval-s", "0.1",
        "--heartbeat-bump-interval-s", "0.5",
        "--no-prepare",
    )
    assert result.returncode == 1, (
        f"expected rc=1 on agent failure; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "(review exited rc=1)" in result.stdout, result.stdout

    log = _read_log(log_path)
    joined = "\n".join(log)
    # Release must have happened with --status error.
    release_lines = [ln for ln in log if "pr-queue release" in ln]
    assert release_lines, f"no release call found. log:\n{joined}"
    assert any("--status error" in ln for ln in release_lines), (
        f"release was not called with --status error. log:\n{joined}"
    )


# --- 5. invalid url ---------------------------------------------------------

def test_invalid_pr_url_exits_2(
    tmp_path: Path,
    fake_claude_script: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)

    result = _run_worker(
        "not-a-url",
        "--adk-bin", str(fake_adk),
        "--agent-bin", str(fake_claude_script),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--no-prepare",
    )
    assert result.returncode == 2, (
        f"expected rc=2 on invalid url; got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "(error: invalid pr_url" in result.stdout, result.stdout
    # fake_adk should never have been called.
    assert _read_log(log_path) == []


# --- 6. SIGTERM -------------------------------------------------------------

def test_sigterm_releases_and_cleans_heartbeat(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)

    # An agent that sleeps long so SIGTERM hits while it's mid-review.
    long_claude = tmp_path / "long-claude"
    long_claude.write_text(
        "#!/bin/sh\n"
        "echo '[claude] long-running'\n"
        "sleep 30\n"
        "exit 0\n"
    )
    long_claude.chmod(0o755)
    pr_url = "https://github.com/acme/foo/pull/45"

    proc = subprocess.Popen(
        [
            sys.executable, str(WORKER), pr_url,
            "--adk-bin", str(fake_adk),
            "--agent-bin", str(long_claude),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
            "--no-prepare",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait for the heartbeat file to appear so we know the worker is mid-run.
    deadline = time.time() + 3.0
    while time.time() < deadline:
        if list(worker_heartbeat_dir.glob("*.json")):
            break
        time.sleep(0.05)
    else:
        # Heartbeat file never appeared — fail loudly instead of letting the
        # downstream SIGTERM-then-assert produce a confusing failure.
        proc.terminate()
        try:
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2.0)
        pytest.fail("heartbeat file never appeared within 3 s")

    proc.send_signal(signal.SIGTERM)
    try:
        rc = proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2.0)
        pytest.fail("worker did not exit within 5s of SIGTERM")

    assert rc == 130, f"expected rc=130 on SIGTERM; got {rc}"

    # Heartbeat file removed within a few heartbeat intervals.
    deadline = time.time() + 2.0
    while time.time() < deadline:
        if not list(worker_heartbeat_dir.glob("*.json")):
            break
        time.sleep(0.05)
    assert list(worker_heartbeat_dir.glob("*.json")) == [], (
        "heartbeat file should be cleaned up after SIGTERM"
    )

    # Release should have been called (with --status error since mid-review).
    log = _read_log(log_path)
    joined = "\n".join(log)
    release_lines = [ln for ln in log if "pr-queue release" in ln]
    assert release_lines, f"no release call after SIGTERM. log:\n{joined}"
    assert any("--status error" in ln for ln in release_lines), (
        f"release was not called with --status error. log:\n{joined}"
    )
