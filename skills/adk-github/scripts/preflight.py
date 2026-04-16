#!/usr/bin/env python3
"""
Preflight check for the adk-github skill.

Verifies required commands, GitHub MCP server configuration, gh CLI
availability and authentication. The skill requires at least one of
MCP or gh CLI to operate.

Usage:
    python3 preflight.py <skill-dir>
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

# macOS brew install hints for common commands
BREW_HINTS: dict[str, str] = {
    "git": "git",
    "python3": "python@3",
    "gh": "gh",
}

# Claude settings files that may contain MCP server configuration
SETTINGS_FILENAMES: list[str] = [
    "settings.json",
    "settings.local.json",
]


def read_required_commands(skill_dir: Path) -> list[str]:
    """Read the required commands list from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"  error: SKILL.md not found in {skill_dir}")
        sys.exit(1)

    text = skill_md.read_text(encoding="utf-8")

    # Match the 'commands:' line under 'dependencies:' -- handles both
    # top-level and indented forms like "  commands: [git, python3]"
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in match.group(1).split(",")
        if item.strip()
    ]


def read_optional_commands(skill_dir: Path) -> list[str]:
    """Read the optional-commands list from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"optional-commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in match.group(1).split(",")
        if item.strip()
    ]


def read_mcp_servers(skill_dir: Path) -> list[str]:
    """Read the mcp-servers list from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"mcp-servers:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [
        item.strip().strip("'\"")
        for item in match.group(1).split(",")
        if item.strip()
    ]


def install_hint(command: str) -> str:
    """Return a platform-appropriate install hint for a missing command."""
    is_macos = platform.system() == "Darwin"
    if is_macos and command in BREW_HINTS:
        return f"brew install {BREW_HINTS[command]}"
    # Generic fallback
    hints: dict[str, str] = {
        "git": "Install git from https://git-scm.com/downloads",
        "python3": "Install Python 3 from https://www.python.org/downloads/",
        "gh": "Install gh CLI from https://cli.github.com",
    }
    return hints.get(command, f"Install {command}")


def check_mcp_server_configured(server_name: str) -> bool:
    """
    Check if an MCP server is configured in Claude settings files.

    Scans these locations (in order):
      - .claude/settings.json and .claude/settings.local.json in cwd
      - ~/.claude/settings.json and ~/.claude/settings.local.json
    """
    search_dirs: list[Path] = [
        Path.cwd() / ".claude",
        Path.home() / ".claude",
    ]

    for directory in search_dirs:
        for filename in SETTINGS_FILENAMES:
            settings_path = directory / filename
            if not settings_path.exists():
                continue
            try:
                data = json.loads(settings_path.read_text(encoding="utf-8"))
                servers = data.get("mcpServers", {})
                if server_name in servers:
                    return True
            except (json.JSONDecodeError, KeyError, OSError):
                continue

    return False


def check_gh_auth() -> tuple[bool, str]:
    """
    Check gh CLI authentication status.

    Returns:
        (authenticated: bool, message: str)
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, "gh CLI is authenticated"
        else:
            # gh auth status prints details to stderr
            detail = result.stderr.strip() or result.stdout.strip()
            return False, f"gh CLI is not authenticated: {detail}"
    except FileNotFoundError:
        return False, "gh CLI is not installed"
    except subprocess.TimeoutExpired:
        return False, "gh auth status timed out"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    is_macos = platform.system() == "Darwin"

    required_commands = read_required_commands(skill_dir)
    optional_commands = read_optional_commands(skill_dir)
    mcp_servers = read_mcp_servers(skill_dir)

    print(f"Checking dependencies for: adk-github")

    errors = 0
    warnings = 0

    # --- Required commands ---
    print("\nRequired commands:")
    for cmd in required_commands:
        if shutil.which(cmd):
            print(f"  ok   {cmd}")
        else:
            hint = install_hint(cmd)
            print(f"  MISS {cmd}")
            print(f"       hint: {hint}")
            errors += 1

    # --- Optional commands ---
    gh_available = False
    if optional_commands:
        print("\nOptional commands:")
        for cmd in optional_commands:
            if shutil.which(cmd):
                print(f"  ok   {cmd}")
                if cmd == "gh":
                    gh_available = True
            else:
                hint = install_hint(cmd)
                print(f"  skip {cmd} (not installed)")
                print(f"       hint: {hint}")
                warnings += 1

    # --- MCP server check ---
    mcp_available = False
    if mcp_servers:
        print("\nMCP servers:")
        for server in mcp_servers:
            if check_mcp_server_configured(server):
                print(f"  ok   {server} (configured)")
                mcp_available = True
            else:
                print(f"  skip {server} (not configured)")
                warnings += 1

    # --- Connectivity check: need at least MCP or gh CLI ---
    print("\nGitHub connectivity:")
    if mcp_available:
        print("  ok   MCP server 'github' is configured (primary path)")
    if gh_available:
        # Check auth status
        authed, auth_msg = check_gh_auth()
        if authed:
            print(f"  ok   gh CLI authenticated (fallback path)")
        else:
            print(f"  warn gh CLI installed but not authenticated")
            print(f"       {auth_msg}")
            if is_macos:
                print(f"       hint: gh auth login")
            else:
                print(f"       hint: gh auth login")
            warnings += 1

    if not mcp_available and not gh_available:
        print("  FAIL No GitHub connectivity available")
        print()
        print("  At least one of the following is required:")
        print()
        print("  Option 1 -- Configure the GitHub MCP server (recommended):")
        print("    hint: Configure the GitHub MCP server in .claude/settings.json")
        print('    Add "github" to the "mcpServers" object in your settings file.')
        print()
        print("  Option 2 -- Install and authenticate the gh CLI:")
        if is_macos:
            print("    hint: brew install gh && gh auth login")
        else:
            print("    hint: Install gh CLI from https://cli.github.com")
            print("    Then run: gh auth login")
        errors += 1

    # --- Summary ---
    print()
    if errors > 0:
        print(f"Preflight FAILED with {errors} error(s) and {warnings} warning(s).")
        print("Fix the items above before running the skill.")
        raise SystemExit(1)
    elif warnings > 0:
        print(f"Preflight passed with {warnings} warning(s).")
    else:
        print("Preflight passed.")


if __name__ == "__main__":
    main()
