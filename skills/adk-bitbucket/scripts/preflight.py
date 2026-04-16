#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

BREW_HINTS: dict[str, str] = {
    "git": "brew install git",
    "python3": "brew install python3",
}

BITBUCKET_MCP_SETUP_HINT = (
    "hint: Configure the Bitbucket MCP server. "
    "See: https://github.com/anthropics/anthropic-quickstarts"
)


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in match.group(1).split(",")
        if item.strip()
    ]


def check_commands(skill_dir: Path) -> list[str]:
    missing: list[str] = []
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            hint = BREW_HINTS.get(command)
            if hint:
                print(f"hint install with: {hint}")
            missing.append(command)
    return missing


def find_settings_paths() -> list[Path]:
    """Return candidate Claude settings files to scan for MCP config."""
    paths: list[Path] = []
    # project-level settings
    cwd = Path.cwd()
    paths.append(cwd / ".claude" / "settings.json")
    # user-level settings
    home = Path.home()
    paths.append(home / ".claude" / "settings.json")
    return paths


def check_bitbucket_mcp() -> bool:
    """Check whether any Claude settings file has a bitbucket MCP server configured."""
    for settings_path in find_settings_paths():
        if not settings_path.is_file():
            continue
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        mcp_servers = data.get("mcpServers", {})
        for key in mcp_servers:
            if "bitbucket" in key.lower():
                print(f"ok bitbucket MCP server found in {settings_path}")
                return True
    return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    failed = False

    # Check required CLI commands
    missing_commands = check_commands(skill_dir)
    if missing_commands:
        failed = True

    # Check Bitbucket MCP server configuration
    if not check_bitbucket_mcp():
        print("missing bitbucket MCP server")
        print(BITBUCKET_MCP_SETUP_HINT)
        failed = True

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
