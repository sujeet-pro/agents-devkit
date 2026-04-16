#!/usr/bin/env python3
"""Preflight check for adk-deps skill.

Verifies required commands are available and reports which package managers
are detected on the system.
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
    "npm": "brew install node",
    "cargo": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
    "go": "brew install go",
    "mvn": "brew install maven",
    "gradle": "brew install gradle",
    "bundle": "gem install bundler",
    "pip": "python3 -m ensurepip",
}

PACKAGE_MANAGERS: list[tuple[str, str]] = [
    ("npm", "Node.js / npm"),
    ("yarn", "Yarn"),
    ("pnpm", "pnpm"),
    ("pip", "Python / pip"),
    ("pip3", "Python / pip3"),
    ("poetry", "Python / Poetry"),
    ("pipenv", "Python / Pipenv"),
    ("cargo", "Rust / Cargo"),
    ("go", "Go modules"),
    ("mvn", "Maven"),
    ("gradle", "Gradle"),
    ("bundle", "Ruby / Bundler"),
    ("gem", "Ruby / RubyGems"),
    ("composer", "PHP / Composer"),
    ("dotnet", ".NET / NuGet"),
]


def read_required_commands(skill_dir: Path) -> list[str]:
    """Read required commands from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [
        item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()
    ]


def hint_for(command: str) -> str:
    """Return an install hint for a missing command, with macOS brew preference."""
    if platform.system() == "Darwin" and command in BREW_HINTS:
        return f"  hint: {BREW_HINTS[command]}"
    if command in BREW_HINTS:
        return f"  hint: {BREW_HINTS[command]}"
    return ""


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    missing: list[str] = []

    # Check required commands
    print("=== Required Commands ===")
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            h = hint_for(command)
            if h:
                print(h)
            missing.append(command)

    # Report available package managers (informational only)
    print()
    print("=== Detected Package Managers ===")
    found_any = False
    for cmd, label in PACKAGE_MANAGERS:
        if shutil.which(cmd):
            print(f"found {cmd} ({label})")
            found_any = True

    if not found_any:
        print("none detected")

    # Only fail if required commands are missing
    if missing:
        print()
        print(f"FAIL: missing required commands: {', '.join(missing)}")
        raise SystemExit(1)
    else:
        print()
        print("PASS: all required commands available")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
