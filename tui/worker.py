"""worker.py — drives one PR through claim → prepare → claude -p → release.

Spawned by the TUI when the user presses `r` on an eligible row. Standalone:
runnable as `python3 tui/worker.py <pr_url>`. POSIX only (uses
`loop.add_signal_handler` for SIGTERM); Windows unsupported per constitution VI.2.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import signal
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Anchored at start-of-line with optional decoration (---, ##, **, >, whitespace).
# This is deliberately strict so we DON'T match "Phase N" mid-prose (e.g. PR
# titles, JSON-embedded strings, narration like "completed Phase 4 ..."). The
# description char-class excludes ':' so a multi-marker line ("Phase 1: foo
# Phase 2: bar") doesn't capture across markers.
_PHASE_RE = re.compile(
    r"^[\s\-#*>]*"
    r"[Pp]hase\s+"
    r"([0-9]+[a-zA-Z]?)"
    r"(?:\s*[:—\-]\s*([^.\n*:]{1,60}))?"
)


def _parse_phase_marker(text: str) -> str | None:
    m = _PHASE_RE.match(text)
    if m is None:
        return None
    num = m.group(1)
    desc = (m.group(2) or "").strip().rstrip("- ").rstrip()
    label = f"phase {num}: {desc}" if desc else f"phase {num}"
    return label[:80]

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skills" / "adk-pr-review" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "adk-cli" / "scripts"))
_LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from config import adk_data_home, adk_config_home  # noqa: E402

from _common import parse_pr_url, task_dir_for  # noqa: E402

from tui.agent_registry import default_agent, get_agent, list_agents  # noqa: E402
from run_state import worker_id as make_worker_id  # noqa: E402

try:
    from queue_io import DEFAULT_QUEUE_PATH  # noqa: E402
except Exception:  # pragma: no cover
    DEFAULT_QUEUE_PATH = adk_config_home() / "pr-queue.json5"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_adk_bin() -> Path:
    candidate = REPO_ROOT / "bin" / "adk"
    return candidate if candidate.exists() else Path("adk")


def _write_heartbeat(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _emit(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


async def _run_streamed(cmd: list[str]) -> int:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        sys.stdout.write(line.decode(errors="replace"))
        sys.stdout.flush()
    return await proc.wait()


async def _bump_loop(adk_bin: str, pr_url: str, queue: str, interval: float) -> None:
    while True:
        await asyncio.sleep(interval)
        p = await asyncio.create_subprocess_exec(
            adk_bin, "pr-queue", "heartbeat", pr_url, "--queue", queue,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        await p.wait()


async def _file_loop(hb_path: Path, payload: dict, interval: float) -> None:
    while True:
        await asyncio.sleep(interval)
        payload["last_heartbeat"] = _now_iso()
        try:
            _write_heartbeat(hb_path, payload)
        except Exception:
            pass


async def _stream_proc(proc: asyncio.subprocess.Process, payload: dict) -> None:
    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        decoded = line.decode(errors="replace")
        sys.stdout.write(decoded)
        sys.stdout.flush()
        new_phase = _parse_phase_marker(decoded)
        if new_phase is not None:
            payload["current_phase"] = new_phase


async def _release(adk_bin: str, pr_url: str, queue: str, *, status: str | None = None) -> None:
    cmd = [adk_bin, "pr-queue", "release", pr_url, "--queue", queue]
    if status:
        cmd += ["--status", status]
    rc = await _run_streamed(cmd)
    if rc == 0:
        _emit(f"(released: {pr_url})")
    else:
        _emit(f"(error: release rc={rc} — lock may be stuck)")


async def _drive(args: argparse.Namespace) -> int:
    try:
        parse_pr_url(args.pr_url)
    except Exception as exc:
        _emit(f"(error: invalid pr_url: {exc})")
        return 2

    adk_bin = str(args.adk_bin) if args.adk_bin else str(_resolve_adk_bin())
    if args.agent_bin:
        agent_bin = str(args.agent_bin)
        agent_name = "custom"
    elif args.agent:
        spec = get_agent(args.agent)
        if spec is None:
            _emit(
                f"(error: unknown agent {args.agent!r}; available: "
                f"{', '.join(s.name for s in list_agents())})"
            )
            return 2
        agent_bin = spec.bin
        agent_name = spec.name
    else:
        spec = default_agent()
        agent_bin = spec.bin
        agent_name = spec.name
    queue = str(args.queue) if args.queue else str(DEFAULT_QUEUE_PATH)

    agent_proc: asyncio.subprocess.Process | None = None
    sig_received = False

    def _on_sigterm() -> None:
        nonlocal sig_received
        sig_received = True
        if agent_proc is not None and agent_proc.returncode is None:
            try:
                agent_proc.terminate()
            except ProcessLookupError:
                pass

    try:
        asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, _on_sigterm)
    except NotImplementedError:  # pragma: no cover
        pass

    claim_cmd = [adk_bin, "pr-queue", "claim", args.pr_url, "--queue", queue]
    if args.force:
        claim_cmd.append("--force")
    if await _run_streamed(claim_cmd) != 0:
        _emit("(error: claim failed — row may be locked by another reviewer)")
        return 2
    _emit(f"(claimed: {args.pr_url})")
    if sig_received:
        await _release(adk_bin, args.pr_url, queue, status="error")
        return 130

    if not args.no_prepare:
        prep_cmd = [adk_bin, "pr-task", "prepare", args.pr_url, "--queue", queue]
        _emit("$ " + " ".join(prep_cmd))
        rc = await _run_streamed(prep_cmd)
        if rc != 0:
            _emit(f"(error: prepare failed rc={rc})")
            await _release(adk_bin, args.pr_url, queue, status="error")
            return 1
        if sig_received:
            await _release(adk_bin, args.pr_url, queue, status="error")
            return 130

    hb_path = Path(args.heartbeat_dir).expanduser() / f"{os.getpid()}.json"
    started = _now_iso()
    worker_state_id = args.worker_id or make_worker_id(args.run_id or f"tui-{os.getpid()}", args.pr_url)
    try:
        _pr_parsed = parse_pr_url(args.pr_url)
        _review_log_path = str(task_dir_for(_pr_parsed["repo"], _pr_parsed["pr_number"]) / "review.log")
    except Exception:
        _review_log_path = None
    payload = {
        "version": 1,
        "worker_id": worker_state_id,
        "run_id": args.run_id,
        "pid": os.getpid(), "pr_url": args.pr_url, "subject": args.pr_url,
        "task_type": "review",
        "status": "running",
        "agent": agent_name, "queue": queue,
        "started_at": started, "last_heartbeat": started,
        "current_phase": "phase 0", "rc": None,
        "log_path": _review_log_path,
        "links": {"pr": args.pr_url},
    }
    _write_heartbeat(hb_path, payload)

    bump_task = asyncio.create_task(_bump_loop(adk_bin, args.pr_url, queue, args.heartbeat_bump_interval_s))
    file_task = asyncio.create_task(_file_loop(hb_path, payload, args.heartbeat_file_interval_s))

    agent_cmd = [agent_bin, "-p", f"/adk-pr-review {args.pr_url}"]
    _emit("$ " + " ".join(agent_cmd))

    agent_rc = 1

    try:
        if agent_bin == "__headless__":
            _emit(f"[headless] no agent spawned for {args.pr_url}")
            await asyncio.sleep(0.5)
            agent_rc = 0
        else:
            try:
                agent_proc = await asyncio.create_subprocess_exec(
                    *agent_cmd,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
                    env=os.environ.copy(),
                )
                await _stream_proc(agent_proc, payload)
                agent_rc = await agent_proc.wait()
            except FileNotFoundError as exc:
                _emit(f"(error: agent not found: {exc})")
                agent_rc = 1
    finally:
        if sig_received and agent_proc is not None:
            try:
                if agent_proc.returncode is None:
                    agent_proc.terminate()
                    try:
                        await asyncio.wait_for(agent_proc.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        agent_proc.kill()
                        await agent_proc.wait()
            except ProcessLookupError:
                pass
            agent_rc = agent_proc.returncode if agent_proc.returncode is not None else 130

        bump_task.cancel()
        file_task.cancel()
        for t in (bump_task, file_task):
            try:
                await t
            except BaseException:
                pass

        try:
            if hb_path.exists():
                hb_path.unlink()
        except OSError:
            pass

        _emit(f"(review exited rc={agent_rc})")

        status = "error" if (sig_received or agent_rc != 0) else None
        await _release(adk_bin, args.pr_url, queue, status=status)

    if sig_received:
        return 130
    return agent_rc if agent_rc == 0 else 1


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="tui/worker.py")
    ap.add_argument("pr_url")
    ap.add_argument("--queue", default=None)
    ap.add_argument("--agent-bin", default=None)
    ap.add_argument(
        "--agent",
        default=None,
        help="agent name in the registry (e.g. 'claude'); "
             "ignored if --agent-bin is also set",
    )
    ap.add_argument("--adk-bin", default=None)
    ap.add_argument("--no-prepare", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="force claim/re-review when a row is already locked")
    ap.add_argument("--heartbeat-bump-interval-s", type=float, default=300.0)
    ap.add_argument("--heartbeat-file-interval-s", type=float, default=5.0)
    ap.add_argument("--heartbeat-dir", default=str(adk_data_home() / "tui" / "workers"))
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--worker-id", default=None)
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        return asyncio.run(_drive(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
