#!/usr/bin/env python3
"""
Preflight checker for the adk-confluence skill.
Validates required commands and Atlassian Confluence MCP server configuration.

Usage:
    python3 preflight.py <skill-dir>
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

# macOS Homebrew install hints for common commands
BREW_HINTS: dict[str, str] = {
    "git": "brew install git",
    "python3": "brew install python3",
    "node": "brew install node",
    "npm": "brew install node",
    "curl": "brew install curl",
    "jq": "brew install jq",
}

# Known MCP settings file locations
MCP_SETTINGS_PATHS: list[Path] = [
    Path.home() / ".claude.json",
    Path.home() / ".claude" / "settings.json",
    Path("mcp-config.json"),
    Path(".mcp.json"),
    Path(".claude" / Path("settings.json")),
    Path(".cursor" / Path("mcp.json")),
]


def read_required_commands(skill_dir: Path) -> list[str]:
    """Parse the commands list from the SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"error: SKILL.md not found in {skill_dir}")
        raise SystemExit(1)
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def read_required_mcp_servers(skill_dir: Path) -> list[str]:
    """Parse the mcp-servers list from the SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"mcp-servers:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def check_mcp_server_in_file(config_path: Path, server_name: str) -> bool:
    """Check if a named MCP server is configured in a JSON settings file."""
    if not config_path.exists():
        return False
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    # Check top-level mcpServers key (Claude Code format)
    servers = data.get("mcpServers", {})
    if server_name in servers:
        return True

    # Check nested projects -> default -> mcpServers (Claude settings.json format)
    projects = data.get("projects", {})
    if isinstance(projects, dict):
        for _project_key, project_val in projects.items():
            if isinstance(project_val, dict):
                nested = project_val.get("mcpServers", {})
                if server_name in nested:
                    return True

    # Check mcp -> servers (Cursor format)
    mcp_block = data.get("mcp", {})
    if isinstance(mcp_block, dict):
        mcp_servers = mcp_block.get("servers", {})
        if server_name in mcp_servers:
            return True

    return False


def check_mcp_server(server_name: str) -> tuple[bool, str | None]:
    """
    Check all known settings file locations for the named MCP server.
    Returns (found, config_path_that_matched_or_None).
    """
    for config_path in MCP_SETTINGS_PATHS:
        if check_mcp_server_in_file(config_path, server_name):
            return True, str(config_path)
    return False, None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    # -- Check required commands --
    print("Checking required commands...")
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"  ok {command}")
        else:
            hint = BREW_HINTS.get(command, "")
            hint_msg = f" (hint: {hint})" if hint else ""
            print(f"  missing {command}{hint_msg}")
            errors.append(command)

    # -- Check required MCP servers --
    print("Checking MCP servers...")
    required_servers = read_required_mcp_servers(skill_dir)

    for server_name in required_servers:
        found, matched_path = check_mcp_server(server_name)
        if found:
            print(f"  ok MCP: {server_name} (found in {matched_path})")
        else:
            print(f"  missing MCP: {server_name}")
            print(f"  hint: Configure the Atlassian Confluence MCP server in your IDE settings.")
            print(f"  hint: For Claude Code, add to ~/.claude.json under mcpServers.")
            print(f"  hint: See: https://github.com/anthropics/anthropic-quickstarts")
            errors.append(f"mcp:{server_name}")

    # -- Summary --
    print()
    if errors:
        print(f"Preflight failed. Missing: {', '.join(errors)}")
        print("Fix the above issues before running the skill.")
        raise SystemExit(1)
    elif warnings:
        print(f"Preflight passed with {len(warnings)} warning(s).")
    else:
        print("Preflight passed. All dependencies satisfied.")


if __name__ == "__main__":
    main()
