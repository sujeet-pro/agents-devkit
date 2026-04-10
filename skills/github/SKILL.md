---
name: github
description: "adk - [helper] [connector] GitHub operations via gh CLI — PR reviews, comments, issues, and repository access"
user-invocable: false
workflow-tier: helper
maturity: stable
dependencies:
  commands: [gh]
allowed-tools: [Read, Bash]
allowed-mcps: [github]
---

# GitHub

Platform connector for GitHub. All operations use the `gh` CLI.

## Preflight

Before any operation, run these checks. **Stop and ask the user** if either fails — do not proceed.

1. Verify `gh` is installed: `command -v gh >/dev/null 2>&1`
2. Verify authentication: `gh auth status 2>&1`

If `gh` is not installed:
> **STOP.** Tell the user:
> Install the GitHub CLI: `brew install gh` (macOS) or see https://cli.github.com/manual/installation
> Then run `/adk:setup --tool gh` to install and verify.

If not authenticated:
> **STOP.** Tell the user:
> Run `gh auth login` and follow the browser-based prompts to sign in with your GitHub account.
> This is a one-time step. Re-run the command after logging in.

## MCP Server Setup

To configure the MCP server for this connector, see `mcp-config.json` in the ADK root directory for the server definition. Copy the relevant entry to your IDE's MCP configuration file (e.g., `~/.claude.json` for Claude Code).

## gh CLI First

Always use the `gh` CLI for all GitHub operations. The `gh` CLI handles authentication, pagination, and rate limiting automatically. Do NOT use `curl` with GitHub APIs.

MCP tools (`mcp__github__*`, `mcp__plugin-adk-github__*`) may be used as a secondary option when available, but `gh` CLI is always the preferred and reliable fallback. When MCP tools fail (auth error, missing scope), fall back to `gh` CLI.

## Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference to use based on the operation needed.

## Operation References

| Domain | Reference | Common Use Cases |
|--------|-----------|-----------------|
| PR Management | `${CLAUDE_SKILL_DIR}/references/pr-operations.md` | Get PR, diff, files, create, update, merge |
| Reviews & Comments | `${CLAUDE_SKILL_DIR}/references/review-operations.md` | Post review, inline comments, reply, resolve threads |
| Repository | `${CLAUDE_SKILL_DIR}/references/repo-operations.md` | File contents, branches, search, commits |
| Issues | `${CLAUDE_SKILL_DIR}/references/issue-operations.md` | Issue CRUD, labels, milestones, assignees |
