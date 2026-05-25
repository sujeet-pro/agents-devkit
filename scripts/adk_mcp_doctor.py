#!/usr/bin/env python3
"""Token-first ADK MCP repair loop.

Flow:
  1. Validate mac-setup creds without printing token values.
  2. If creds are valid, re-run the ADK installer for the requested agents.
  3. Run MCP health in strict mode, including agent config checks.
  4. Repeat installer + health while failures are changing and attempts remain.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent


def _cmd_text(cmd: list[str]) -> str:
    return " ".join(cmd)


def _run(cmd: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    print(f"[adk:mcp-doctor] $ {_cmd_text(cmd)}")
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _creds_cmd() -> str | None:
    return shutil.which("creds") or str(Path.home() / ".local" / "bin" / "creds")


def validate_creds(timeout: int) -> tuple[int, dict[str, Any]]:
    creds = _creds_cmd()
    if not creds or not Path(creds).exists():
        return 1, {"error": "creds CLI not found"}
    result = _run([creds, "validate", "--json", "--no-log"], timeout=timeout)
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as e:
        data = {"error": f"invalid creds JSON: {e}"}
    return result.returncode, data


def summarize_creds(data: dict[str, Any]) -> list[str]:
    services = data.get("services", {}) or {}
    out: list[str] = []
    for name, info in sorted(services.items()):
        state = info.get("status", "?")
        if state not in {"OK", "SKIPPED"}:
            out.append(f"{name}: {state}")
    if not services and data.get("error"):
        out.append(str(data["error"]))
    return out


def run_install(targets: str, timeout: int) -> int:
    cmd = ["./install.sh", "--target", targets, "--no-deps", "--no-completions"]
    result = _run(cmd, timeout=timeout)
    if result.returncode != 0:
        sys.stdout.write(result.stdout[-4000:])
        sys.stderr.write(result.stderr[-4000:])
    return result.returncode


def run_health(*, probe: bool, timeout: int) -> tuple[int, dict[str, Any]]:
    cmd = [
        sys.executable,
        "scripts/adk_mcp_health.py",
        "--json",
        "--strict",
        "--check-agent-configs",
    ]
    if probe:
        cmd.append("--probe")
    result = _run(cmd, timeout=timeout)
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as e:
        data = {"failure_summary": [f"invalid health JSON: {e}"]}
    return result.returncode, data


def summarize_health(data: dict[str, Any]) -> list[str]:
    failures = list(data.get("failure_summary", []) or [])
    if failures:
        return failures
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate creds, install ADK MCPs, and verify all agent MCP configs.")
    parser.add_argument("--target", default="all", help="Installer target(s), e.g. all or claude,cursor,codex,junie")
    parser.add_argument("--max-rounds", type=int, default=3, help="Install/health iterations after creds pass")
    parser.add_argument("--probe", action="store_true", help="Also curl-probe HTTP MCP endpoints")
    parser.add_argument("--creds-timeout", type=int, default=240)
    parser.add_argument("--install-timeout", type=int, default=180)
    parser.add_argument("--health-timeout", type=int, default=240)
    args = parser.parse_args()

    creds_rc, creds_data = validate_creds(args.creds_timeout)
    bad_creds = summarize_creds(creds_data)
    if creds_rc != 0 or bad_creds:
        print("[adk:mcp-doctor] stopping: credentials are not all valid")
        for item in bad_creds:
            print(f"  - {item}")
        return creds_rc or 1
    print("[adk:mcp-doctor] credentials: ok")

    previous_failures: list[str] | None = None
    for round_no in range(1, args.max_rounds + 1):
        print(f"[adk:mcp-doctor] round {round_no}/{args.max_rounds}")
        install_rc = run_install(args.target, args.install_timeout)
        if install_rc != 0:
            return install_rc
        health_rc, health_data = run_health(probe=args.probe, timeout=args.health_timeout)
        failures = summarize_health(health_data)
        if health_rc == 0 and not failures:
            print("[adk:mcp-doctor] MCP health: ok")
            return 0
        print("[adk:mcp-doctor] MCP health failures:")
        for item in failures:
            print(f"  - {item}")
        if failures == previous_failures:
            print("[adk:mcp-doctor] stopping: failures did not change after reinstall")
            return health_rc or 1
        previous_failures = failures

    print("[adk:mcp-doctor] stopping: max rounds reached")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
