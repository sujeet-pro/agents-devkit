---
title: 'bitbucket'
description: 'Bitbucket REST API operations — PR reviews, comments, repository access, and pipeline status'
skill_name: bitbucket
category: connector
workflow_tier: helper
user_invocable: false
---

# bitbucket

`bitbucket` centralizes platform-specific operations so higher-level skills do not need to own authentication, transport choice, and fallback logic themselves. The calling skill owns the user-facing workflow; this connector owns authentication checks, transport choice, and operation boundaries.

## Overview

`bitbucket` belongs to the `connector` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

Connector skills deliberately centralize platform-specific behavior. That keeps authentication, fallback order, and operation families in one place so higher-level task skills can focus on review, documentation, or implementation logic instead of API plumbing.

## Parameters

This connector does not define a standalone user-facing parameter table. The calling skill decides the operation and passes the relevant context through the connector contract.

## How It Works

Connector behavior starts with preflight. The skill validates authentication, tooling, or MCP access first, then routes the requested operation through the preferred transport and fallback path defined in `SKILL.md`.

That split matters for developers because task skills depend on this page to understand what is guaranteed before a networked action happens and what should happen when auth or transport is unavailable.

### Operation References

| Domain | Reference | Script | Common Use Cases |
|--------|-----------|--------|-----------------|
| PR Management | `${CLAUDE_SKILL_DIR}/references/pr-operations.md` | `scripts/pr.sh` | Get PR, diff, diffstat, create, update, merge, approve |
| Comments | `${CLAUDE_SKILL_DIR}/references/comment-operations.md` | `scripts/comments.sh` | List, create inline, reply, update, delete |
| Repository | `${CLAUDE_SKILL_DIR}/references/repo-operations.md` | `scripts/repo.sh` | File contents, branches, commits |

## Modes & Variations

The important variations here are usually transport choice, operation family, or platform-specific fallback behavior rather than a user-visible workflow mode.


### Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference and script to use.

## Output

Connectors typically return platform data or perform side effects for the calling skill. They do not usually define the final human-facing narrative on their own.


## Additional Reference

### Auth

Requires environment variables in `~/.zshenv`:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_TOKEN="your-app-password"
```

Generate an app password at: https://bitbucket.org/account/settings/app-passwords/
Required scopes: `repository:read`, `pullrequest:read`, `pullrequest:write`

### Validation

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/auth.sh
```

If auth fails or token is expired, tell the user:
> Add or update your Bitbucket credentials in `~/.zshenv`:
> ```bash
> export BITBUCKET_USERNAME="your-username"
> export BITBUCKET_TOKEN="your-app-password"
> ```
> Then run `source ~/.zshenv` and retry.

### MCP Server Setup

To configure the MCP server for this connector, see `mcp-config.json` in the ADK root directory for the server definition. Copy the relevant entry to your IDE's MCP configuration file (e.g., `~/.claude.json` for Claude Code).

### API-First Approach

Always prefer direct REST API calls (via `curl`) over MCP tools. The bundled scripts under `scripts/` wrap the Bitbucket REST API and work in any environment (Claude Code, Codex, etc.) without MCP dependencies. If the scripts are not accessible via `${CLAUDE_SKILL_DIR}`, construct `curl` commands directly from the reference docs below — do NOT create new shell scripts.

MCP tools (`mcp__bitbucket__*`, `mcp__plugin-adk-atlassian__*`, `mcp__plugin-atlassian-atlassian__*`, `mcp__atlassian__*`) may be used as a secondary option when available, but fall back to direct API calls for any operation not covered or if MCP fails.

### Comments

By default, "comments" means **inline comments** — comments attached to a specific file and line in a PR. Use the `--file` and `--line` flags with `comments.sh create`, or the `inline` field in the REST API body. General (non-inline) comments are only used for PR-level summaries.

### API Base

All endpoints use: `https://api.bitbucket.org/2.0`

### Script Usage

All scripts accept subcommands:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/pr.sh <action> <workspace> <repo> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/comments.sh <action> <workspace> <repo> <pr-id> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/repo.sh <action> <workspace> <repo> [args...]
```

Scripts output JSON to stdout. Errors go to stderr. Non-zero exit on failure.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
