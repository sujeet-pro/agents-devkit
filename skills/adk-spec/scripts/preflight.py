#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

BREW_HINTS: dict[str, str] = {
    "git": "brew install git",
    "python3": "brew install python3",
}


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
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
    missing: list[str] = []
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            hint = BREW_HINTS.get(command, "")
            hint_msg = f"  (macOS hint: {hint})" if hint else ""
            print(f"missing {command}{hint_msg}")
            missing.append(command)

    if missing:
        print(f"\n{len(missing)} required command(s) not found in PATH.")
        raise SystemExit(1)
    else:
        print("\nAll required commands available.")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
