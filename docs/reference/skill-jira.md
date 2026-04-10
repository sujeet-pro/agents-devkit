---
title: 'jira'
description: 'Jira REST API operations — issue management, comments, search, projects, boards, and sprints'
skill_name: jira
category: connector
workflow_tier: helper
user_invocable: false
---

# jira

`jira` centralizes platform-specific operations so higher-level skills do not need to own authentication, transport choice, and fallback logic themselves. The calling skill owns the user-facing workflow; this connector owns authentication checks, transport choice, and operation boundaries.

## Overview

`jira` belongs to the `connector` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

Connector skills deliberately centralize platform-specific behavior. That keeps authentication, fallback order, and operation families in one place so higher-level task skills can focus on review, documentation, or implementation logic instead of API plumbing.

## Parameters

This connector does not define a standalone user-facing parameter table. The calling skill decides the operation and passes the relevant context through the connector contract.

## How It Works

Connector behavior starts with preflight. The skill validates authentication, tooling, or MCP access first, then routes the requested operation through the preferred transport and fallback path defined in `SKILL.md`.

That split matters for developers because task skills depend on this page to understand what is guaranteed before a networked action happens and what should happen when auth or transport is unavailable.

### Operation References

| Domain | Reference | Script | Common Use Cases |
|--------|-----------|--------|-----------------|
| Issues | `${CLAUDE_SKILL_DIR}/references/issue-operations.md` | `scripts/issues.sh` | Get, create, update, transition, assign, link |
| Comments | `${CLAUDE_SKILL_DIR}/references/comment-operations.md` | `scripts/comments.sh` | Add, update, delete, list comments |
| Search | `${CLAUDE_SKILL_DIR}/references/search-operations.md` | `scripts/search.sh` | JQL queries, filters |
| Projects | `${CLAUDE_SKILL_DIR}/references/project-operations.md` | `scripts/projects.sh` | List, get, versions, components |
| Boards & Sprints | `${CLAUDE_SKILL_DIR}/references/board-operations.md` | `scripts/boards.sh` | Boards, sprints, backlog management |

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
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

Uses the same API token type as Confluence. Generate at: https://id.atlassian.com/manage-profile/security/api-tokens

### Validation

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/auth.sh
```

If auth fails or token is expired:
> Add or update your Jira credentials in `~/.zshenv`:
> ```bash
> export JIRA_URL="https://your-domain.atlassian.net"
> export JIRA_USERNAME="your-email@example.com"
> export JIRA_API_TOKEN="your-api-token"
> ```
> Then run `source ~/.zshenv` and retry.

### MCP Server Setup

To configure the MCP server for this connector, see `mcp-config.json` in the ADK root directory for the server definition. Copy the relevant entry to your IDE's MCP configuration file (e.g., `~/.claude.json` for Claude Code).

### MCP Connector Detection

Before using scripts, check if an official Atlassian/Jira MCP connector is available:

1. Look for tools matching `mcp__atlassian__*`, `mcp__jira__*`, `mcp__plugin-atlassian-atlassian__*`, or `mcp__plugin-adk-atlassian__*` pattern
2. If available, prefer MCP tools for supported operations
3. Fall back to scripts for operations not covered by the MCP

### Known MCP Connector Capabilities

The official Atlassian MCP connector typically supports:
- Get issue details — use MCP
- Create issues — use MCP
- Update issues — use MCP
- Search via JQL — use MCP
- Add comments — use MCP

Operations that typically require scripts:
- Board/sprint management — use `scripts/boards.sh`
- Bulk operations — use `scripts/issues.sh`
- Transition with custom fields — use `scripts/issues.sh`
- Worklog management — use `scripts/issues.sh`
- Component/version management — use `scripts/projects.sh`

### API Base

- REST API v3: `${JIRA_URL}/rest/api/3`
- Agile API v1: `${JIRA_URL}/rest/agile/1.0`

### Script Usage

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/issues.sh <action> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/comments.sh <action> --key <issue-key> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/search.sh <jql-query> [--max-results N] [--fields field1,field2]
bash ${CLAUDE_SKILL_DIR}/scripts/projects.sh <action> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/boards.sh <action> [args...]
```

Scripts output JSON to stdout. Errors go to stderr. Non-zero exit on failure.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
