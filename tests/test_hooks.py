#!/usr/bin/env python3
"""
Validate runtime-specific hook projections.

Usage:
    python3 tests/test_hooks.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOOK_FILES = [
    ROOT / "hooks" / "settings.json",
    ROOT / "hooks" / "hooks-cursor" / "hooks.json",
    ROOT / "hooks" / "hooks-codex" / "hooks.json",
]


def check_files_exist_and_parse() -> list[str]:
    failures: list[str] = []
    for path in HOOK_FILES:
        if not path.is_file():
            failures.append(f"missing hook projection: {path.relative_to(ROOT)}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return failures


def check_generator() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_hook_projections.py"), "--check"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        return []

    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return [f"hook projection generator check failed:\n{output}"]


def main() -> int:
    failures = check_files_exist_and_parse()
    failures.extend(check_generator())

    if failures:
        print("Hook projection validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Hook projection validation passed: Claude, Cursor, and Codex hook files are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
