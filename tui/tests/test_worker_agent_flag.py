"""Integration tests for `tui/worker.py --agent <name>` — κ §8.3.

Each test invokes the worker as a subprocess with a fake `--adk-bin` that
records argv. The new `--agent <name>` flag resolves via tui.agent_registry;
`--agent-bin <path>` (raw) wins over `--agent` when both are passed.

The `headless` agent is a sentinel — the worker emits one stdout line and
exits 0 without spawning a subprocess.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKER = _REPO_ROOT / "tui" / "worker.py"


def _recording_adk(tmp_path: Path, log_path: Path) -> Path:
    """Fake-adk that appends its argv to `log_path` and exits 0."""
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


def _read_log(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [ln for ln in log_path.read_text().splitlines() if ln]


def _run_worker(
    *args: str,
    timeout: float = 15.0,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(WORKER), *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=env,
    )


# --- 1. --agent + --agent-bin: raw override wins ---------------------------

def test_agent_bin_overrides_agent_name_and_heartbeat_says_custom(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """When both --agent and --agent-bin are passed, --agent-bin wins
    and the heartbeat 'agent' field is 'custom'."""
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)

    # Use a slower fake-claude so we can read the heartbeat file mid-run.
    slow = tmp_path / "slow-claude"
    slow.write_text(
        "#!/bin/sh\n"
        "echo '[claude] starting'\n"
        "sleep 1.5\n"
        "echo '[claude] done'\n"
        "exit 0\n"
    )
    slow.chmod(0o755)

    pr_url = "https://github.com/acme/foo/pull/901"

    proc = subprocess.Popen(
        [
            sys.executable, str(WORKER), pr_url,
            "--agent", "claude",
            "--agent-bin", str(slow),
            "--adk-bin", str(fake_adk),
            "--heartbeat-dir", str(worker_heartbeat_dir),
            "--heartbeat-file-interval-s", "0.1",
            "--heartbeat-bump-interval-s", "0.5",
            "--no-prepare",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    found: dict | None = None
    deadline = time.time() + 5.0
    while time.time() < deadline:
        files = list(worker_heartbeat_dir.glob("*.json"))
        if files:
            try:
                found = json.loads(files[0].read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                found = None
            if found is not None:
                break
        time.sleep(0.05)

    try:
        assert found is not None, "heartbeat file never appeared"
        assert found.get("agent") == "custom", (
            f"heartbeat 'agent' expected 'custom', got {found.get('agent')!r}"
        )
    finally:
        try:
            rc = proc.wait(timeout=10.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2.0)
            raise
    assert rc == 0, f"worker rc={rc}"


# --- 2. --agent headless: no subprocess, clean exit, release called --------

def test_agent_headless_emits_stub_line_and_exits_zero(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """`--agent headless` shouldn't spawn anything; just emit a stub line,
    exit 0, and release the row. The heartbeat agent field must be
    'headless' while it briefly exists."""
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/902"

    # Start the worker via Popen so we can race the heartbeat read against
    # the 0.5 s headless sleep before cleanup.
    proc = subprocess.Popen(
        [
            sys.executable, "-u", str(WORKER), pr_url,
            "--agent", "headless",
            "--adk-bin", str(fake_adk),
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

    found: dict | None = None
    deadline = time.time() + 3.0
    while time.time() < deadline:
        files = list(worker_heartbeat_dir.glob("*.json"))
        if files:
            try:
                found = json.loads(files[0].read_text())
            except (json.JSONDecodeError, FileNotFoundError):
                found = None
            if found is not None:
                break
        if proc.poll() is not None:
            break
        time.sleep(0.02)

    try:
        out, _ = proc.communicate(timeout=10.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate(timeout=2.0)
        pytest.fail("worker hung")

    rc = proc.returncode
    assert rc == 0, f"worker rc={rc}\nstdout:\n{out}"
    assert f"[headless] no agent spawned for {pr_url}" in out, out

    # Heartbeat field (if we caught it) must say 'headless'.
    if found is not None:
        assert found.get("agent") == "headless", (
            f"heartbeat 'agent' expected 'headless', got {found.get('agent')!r}"
        )

    # Release must have been called (proof of clean cleanup).
    log = _read_log(log_path)
    joined = "\n".join(log)
    release_lines = [ln for ln in log if "pr-queue release" in ln]
    assert release_lines, f"no release call found. log:\n{joined}"
    # Clean exit → no --status error.
    assert not any("--status error" in ln for ln in release_lines), (
        f"release should have been clean (no --status). log:\n{joined}"
    )

    # Heartbeat file removed.
    assert list(worker_heartbeat_dir.glob("*.json")) == [], (
        "heartbeat file should be removed on clean exit"
    )


# --- 3. unknown agent name -> rc=2, helpful error ---------------------------

def test_agent_unknown_name_exits_2_with_listing(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/903"

    result = _run_worker(
        pr_url,
        "--agent", "ghost",
        "--adk-bin", str(fake_adk),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--no-prepare",
    )

    assert result.returncode == 2, (
        f"expected rc=2, got {result.returncode}\nstdout:\n{result.stdout}"
    )
    assert "(error: unknown agent 'ghost';" in result.stdout, result.stdout
    # The error listing should mention the known agents.
    assert "claude" in result.stdout
    assert "headless" in result.stdout


# --- 4. --agent claude with no --agent-bin: PATH lookup --------------------

def test_agent_claude_falls_back_to_path_lookup(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """`--agent claude` (no --agent-bin) resolves to the `claude` binary.
    If claude is not on PATH on the test machine, the worker must surface
    a FileNotFoundError-style line and exit non-zero. If claude IS on PATH,
    we skip (we can't safely invoke the real CLI in a test)."""
    if shutil.which("claude") is not None:
        pytest.skip("real `claude` is on PATH; skipping to avoid invoking it")

    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/904"

    # Force PATH to a minimal value so claude can't accidentally be found
    # via a developer's PATH leaking in.
    import os
    env = os.environ.copy()
    env["PATH"] = str(tmp_path)

    result = _run_worker(
        pr_url,
        "--agent", "claude",
        "--adk-bin", str(fake_adk),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--no-prepare",
        env=env,
    )

    assert result.returncode != 0, (
        f"expected non-zero rc when claude missing; got 0\n"
        f"stdout:\n{result.stdout}"
    )
    assert "agent not found" in result.stdout, (
        f"expected 'agent not found' message; got:\n{result.stdout}"
    )


# --- 5. default (no --agent, no --agent-bin): same as --agent claude -------

def test_no_agent_flag_defaults_to_claude(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """Omitting both --agent and --agent-bin behaves like `--agent claude`."""
    if shutil.which("claude") is not None:
        pytest.skip("real `claude` is on PATH; skipping to avoid invoking it")

    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/905"

    import os
    env = os.environ.copy()
    env["PATH"] = str(tmp_path)

    result = _run_worker(
        pr_url,
        "--adk-bin", str(fake_adk),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--no-prepare",
        env=env,
    )

    assert result.returncode != 0, (
        f"expected non-zero rc when default agent (claude) missing; got 0\n"
        f"stdout:\n{result.stdout}"
    )
    assert "agent not found" in result.stdout, (
        f"expected 'agent not found' message; got:\n{result.stdout}"
    )


# --- 6. --agent codex resolves to codex bin (file-not-found smoke test) ----

def test_agent_codex_resolves_to_codex_bin(
    tmp_path: Path,
    worker_heartbeat_dir: Path,
) -> None:
    """`--agent codex` should attempt to invoke the `codex` binary. With an
    empty PATH that's a clean FileNotFoundError that the worker handles."""
    if shutil.which("codex") is not None:
        pytest.skip("real `codex` is on PATH; skipping to avoid invoking it")

    log_path = tmp_path / "adk.log"
    fake_adk = _recording_adk(tmp_path, log_path)
    pr_url = "https://github.com/acme/foo/pull/906"

    import os
    env = os.environ.copy()
    env["PATH"] = str(tmp_path)

    result = _run_worker(
        pr_url,
        "--agent", "codex",
        "--adk-bin", str(fake_adk),
        "--heartbeat-dir", str(worker_heartbeat_dir),
        "--no-prepare",
        env=env,
    )

    assert result.returncode != 0
    # Whatever error path fires, the message should reference the missing
    # binary (codex), not claude.
    assert "codex" in result.stdout, (
        f"expected 'codex' in error output; got:\n{result.stdout}"
    )
