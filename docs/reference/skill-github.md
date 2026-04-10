---
title: 'github'
description: 'GitHub operations via gh CLI — PR reviews, comments, issues, and repository access'
skill_name: github
category: connector
workflow_tier: helper
user_invocable: false
---

# github

`github` centralizes platform-specific operations so higher-level skills do not need to own authentication, transport choice, and fallback logic themselves. The calling skill owns the user-facing workflow; this connector owns authentication checks, transport choice, and operation boundaries.

## Overview

`github` belongs to the `connector` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

Connector skills deliberately centralize platform-specific behavior. That keeps authentication, fallback order, and operation families in one place so higher-level task skills can focus on review, documentation, or implementation logic instead of API plumbing.

## Parameters

This connector does not define a standalone user-facing parameter table. The calling skill decides the operation and passes the relevant context through the connector contract.

## How It Works

Connector behavior starts with preflight. The skill validates authentication, tooling, or MCP access first, then routes the requested operation through the preferred transport and fallback path defined in `SKILL.md`.

That split matters for developers because task skills depend on this page to understand what is guaranteed before a networked action happens and what should happen when auth or transport is unavailable.

### Preflight

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

### Operation References

| Domain | Reference | Common Use Cases |
|--------|-----------|-----------------|
| PR Management | `${CLAUDE_SKILL_DIR}/references/pr-operations.md` | Get PR, diff, files, create, update, merge |
| Reviews & Comments | `${CLAUDE_SKILL_DIR}/references/review-operations.md` | Post review, inline comments, reply, resolve threads |
| Repository | `${CLAUDE_SKILL_DIR}/references/repo-operations.md` | File contents, branches, search, commits |
| Issues | `${CLAUDE_SKILL_DIR}/references/issue-operations.md` | Issue CRUD, labels, milestones, assignees |

## Modes & Variations

The important variations here are usually transport choice, operation family, or platform-specific fallback behavior rather than a user-visible workflow mode.


### Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference to use based on the operation needed.

## Output

Connectors typically return platform data or perform side effects for the calling skill. They do not usually define the final human-facing narrative on their own.


## Additional Reference

### MCP Server Setup

To configure the MCP server for this connector, see `mcp-config.json` in the ADK root directory for the server definition. Copy the relevant entry to your IDE's MCP configuration file (e.g., `~/.claude.json` for Claude Code).

### gh CLI First

Always use the `gh` CLI for all GitHub operations. The `gh` CLI handles authentication, pagination, and rate limiting automatically. Do NOT use `curl` with GitHub APIs.

MCP tools (`mcp__github__*`, `mcp__plugin-adk-github__*`) may be used as a secondary option when available, but `gh` CLI is always the preferred and reliable fallback. When MCP tools fail (auth error, missing scope), fall back to `gh` CLI.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
