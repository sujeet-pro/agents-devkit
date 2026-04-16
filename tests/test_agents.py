#!/usr/bin/env python3
"""
Validate runtime-specific custom agent projections.

Usage:
    python3 tests/test_agents.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANONICAL_AGENTS_DIR = ROOT / "agent-personas"

RUNTIME_DIRS = {
    "agents-claude": ".md",
    "agents-cursor": ".md",
    "agents-codex": ".toml",
}


def canonical_agent_names() -> list[str]:
    return sorted(
        directory.name
        for directory in CANONICAL_AGENTS_DIR.iterdir()
        if directory.is_dir() and (directory / "AGENT.md").exists()
    )


def check_runtime_dirs(expected_names: list[str]) -> list[str]:
    failures: list[str] = []
    for relative_dir, suffix in RUNTIME_DIRS.items():
        runtime_dir = ROOT / relative_dir
        if not runtime_dir.is_dir():
            failures.append(f"missing runtime dir: {relative_dir}")
            continue

        actual_names = sorted(path.stem for path in runtime_dir.glob(f"adk-*{suffix}"))
        if actual_names != expected_names:
            failures.append(
                f"{relative_dir} mismatch:\n"
                f"  expected: {expected_names}\n"
                f"  actual:   {actual_names}"
            )
    return failures


def check_generator() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_agent_projections.py"), "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        return []

    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return [f"projection generator check failed:\n{output}"]


def main() -> int:
    expected_names = canonical_agent_names()
    failures = check_runtime_dirs(expected_names)
    failures.extend(check_generator())

    if failures:
        print("Agent projection validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Agent projection validation passed: "
        f"{len(expected_names)} canonical agents projected to Claude, Cursor, and Codex."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
