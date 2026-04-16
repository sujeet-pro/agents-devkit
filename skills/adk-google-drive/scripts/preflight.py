#!/usr/bin/env python3
"""Pre-flight check for the adk-google-drive skill.

Verifies:
1. Required CLI commands (git, python3) are available.
2. The google-drive MCP server is configured in Claude settings files.
3. Provides auth-check hints when MCP is found, or setup instructions when missing.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

# Settings files where MCP server configuration may appear.
SETTINGS_CANDIDATES = [
    Path.home() / ".claude" / "settings.json",
    Path.home() / ".claude" / "settings.local.json",
    Path.cwd() / ".claude" / "settings.json",
    Path.cwd() / ".claude" / "settings.local.json",
    Path.cwd() / ".mcp.json",
]

BREW_HINTS: dict[str, str] = {
    "git": "brew install git",
    "python3": "brew install python3",
}

MCP_SERVER_KEY = "google-drive"


def read_required_commands(skill_dir: Path) -> list[str]:
    """Parse the commands list from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["git", "python3"]
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def check_commands(skill_dir: Path) -> list[str]:
    """Check that each required command is in PATH. Return list of missing."""
    missing: list[str] = []
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            hint = BREW_HINTS.get(command, "")
            hint_msg = f" (install with: {hint})" if hint else ""
            print(f"missing {command}{hint_msg}")
            missing.append(command)
    return missing


def find_mcp_server() -> bool:
    """Check whether the google-drive MCP server is configured in any settings file."""
    for settings_path in SETTINGS_CANDIDATES:
        if not settings_path.exists():
            continue
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        # Check top-level mcpServers key.
        mcp_servers = data.get("mcpServers", {})
        if MCP_SERVER_KEY in mcp_servers:
            print(f"ok mcp-server:{MCP_SERVER_KEY} (found in {settings_path})")
            return True

        # Check nested projects or env-level config patterns.
        for key in ("projects", "environments"):
            section = data.get(key, {})
            if isinstance(section, dict):
                for _name, cfg in section.items():
                    if isinstance(cfg, dict) and MCP_SERVER_KEY in cfg.get("mcpServers", {}):
                        print(f"ok mcp-server:{MCP_SERVER_KEY} (found in {settings_path} -> {key})")
                        return True

    return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    errors: list[str] = []

    # 1. Check required commands.
    missing_commands = check_commands(skill_dir)
    errors.extend(missing_commands)

    # 2. Check for google-drive MCP server configuration.
    mcp_found = find_mcp_server()
    if mcp_found:
        print(f"hint run adk-google-drive --action auth-check to verify OAuth scopes")
    else:
        print(f"missing mcp-server:{MCP_SERVER_KEY}")
        print("hint Configure the Google Drive MCP server with OAuth credentials")
        print("hint See the MCP server documentation for setup instructions")
        errors.append(f"mcp-server:{MCP_SERVER_KEY}")

    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
