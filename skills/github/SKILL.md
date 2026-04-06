---
name: adk-github
description: "adk - [helper] [connector] GitHub operations via gh CLI — PR reviews, comments, issues, and repository access"
user-invocable: false
workflow-tier: helper
dependencies:
  commands: [gh]
---

# GitHub

Platform connector for GitHub. All operations use the `gh` CLI.

## Preflight

Before any operation:

1. Verify `gh` is installed: `command -v gh >/dev/null 2>&1`
2. Verify authentication: `gh auth status 2>&1`

If `gh` is not installed:
> Install the GitHub CLI: `brew install gh` (macOS) or see https://cli.github.com/manual/installation

If not authenticated:
> Run `gh auth login` and follow the prompts.

## MCP Connector Detection

Before falling back to `gh` CLI, check if a GitHub MCP connector is available:

1. Look for tools matching `mcp__github__*` pattern
2. If available, prefer MCP tools for supported operations
3. Use `gh` CLI for operations not covered by the MCP

When MCP tools exist but fail (auth error, missing scope), fall back to `gh` CLI.

## Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference to use based on the operation needed.

## Operation References

| Domain | Reference | Common Use Cases |
|--------|-----------|-----------------|
| PR Management | `${CLAUDE_SKILL_DIR}/references/pr-operations.md` | Get PR, diff, files, create, update, merge |
| Reviews & Comments | `${CLAUDE_SKILL_DIR}/references/review-operations.md` | Post review, inline comments, reply, resolve threads |
| Repository | `${CLAUDE_SKILL_DIR}/references/repo-operations.md` | File contents, branches, search, commits |
| Issues | `${CLAUDE_SKILL_DIR}/references/issue-operations.md` | Issue CRUD, labels, milestones, assignees |
