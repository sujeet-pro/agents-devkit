#!/usr/bin/env python3
"""Preflight check for adk-handoff.

Verifies that required commands (git, python3) are available.
On macOS, suggests Homebrew install commands for missing tools.
"""
from __future__ import annotations

import platform
import re
import shutil
import sys
from pathlib import Path


BREW_HINTS: dict[str, str] = {
    "git": "brew install git",
    "python3": "brew install python3",
}


def read_required_commands(skill_dir: Path) -> list[str]:
    """Read required commands from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"warning: {skill_md} not found, skipping command check")
        return []
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    is_macos = platform.system() == "Darwin"
    missing: list[str] = []

    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            hint = ""
            if is_macos and command in BREW_HINTS:
                hint = f"  (install with: {BREW_HINTS[command]})"
            print(f"missing {command}{hint}")
            missing.append(command)

    if missing:
        print(f"\n{len(missing)} required command(s) not found.")
        if is_macos:
            print("Tip: install missing tools with Homebrew (https://brew.sh)")
        raise SystemExit(1)
    else:
        print("\nAll required commands available.")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
