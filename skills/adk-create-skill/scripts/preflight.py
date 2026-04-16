#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


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
    missing = []
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            missing.append(command)

    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
