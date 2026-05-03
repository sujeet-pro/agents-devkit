---
title: Claude Code and Desktop
description: How adk skills handle dependency checks in Claude Code and Claude Desktop.
order: 3
---

# Claude Code and Desktop

adk skills are written for both Claude Code CLI and Claude Desktop, but MCP loading differs:

- Claude Code can load custom MCP servers declared in a plugin-local `.mcp.json`.
- Claude Desktop does not obey plugin-local `.mcp.json` files.
- Workspace connectors, such as Atlassian, Google Drive, Slack, Mixpanel, and Snowflake, must be configured by the user's workspace or Desktop connector settings.

## Skill Preflight

Every non-trivial skill has a Phase 1 preflight. The preflight classifies dependencies as:

- Required now: the selected mode cannot complete without it.
- Optional capability: useful for richer output, but not necessary for the current mode.
- Write-only dependency: only required when posting, publishing, pushing, or mutating remote state.

If a required dependency is missing, the skill stops before doing the main work and prints the exact connector, CLI, meta-info file, or environment variable that must be configured.

## Skipping a Check

The user can explicitly skip a dependency check when the current mode does not need that capability. For example, a dry-run review that only drafts comments can skip a write-capable PR connector, while a mode that posts comments must verify it.

Skipped checks are always listed in the final report with the reason and residual risk.
