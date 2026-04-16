#!/usr/bin/env python3
"""Pre-flight checks for adk-review-pr."""
from __future__ import annotations

import platform
import re
import shutil
import sys
from pathlib import Path

BREW_PACKAGES = {
    "git": "git",
    "python3": "python@3",
    "gh": "gh",
}


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [c.strip().strip("'\"") for c in match.group(1).split(",") if c.strip()]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    is_mac = platform.system() == "Darwin"
    missing = []

    for cmd in read_required_commands(skill_dir):
        if shutil.which(cmd):
            print(f"ok {cmd}")
        else:
            print(f"missing {cmd}")
            missing.append(cmd)
            if is_mac and cmd in BREW_PACKAGES:
                print(f"  hint: brew install {BREW_PACKAGES[cmd]}")

    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
