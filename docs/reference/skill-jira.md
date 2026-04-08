---
title: "jira"
description: Jira REST API operations — issue management, comments, search, projects, boards, and sprints
skill_name: jira
category: connector
workflow_tier: helper
user_invocable: false
---

# jira

Platform connector for Jira Cloud. Wraps the Jira REST API v3 and Agile REST API v1 via `curl`, providing issue management, JQL search, comments, project administration, board and sprint management to task skills that need Jira integration.

## Purpose

- Provide Jira Cloud API access to task skills like `docs-crud` for context reading and issue tracking
- Create, read, update, transition, assign, and link issues through the full issue lifecycle
- Search issues with JQL queries for filtering, sprint planning, and reporting
- Manage comments on issues — add, update, delete, and list
- Access project metadata including versions, components, and statuses
- Manage agile boards, sprints, backlogs, and issue ranking

## Authentication & Setup

### Requirements

| Dependency | Check | Install |
|------------|-------|---------|
| `curl` | `command -v curl` | Pre-installed on macOS/Linux |
| `jq` | `command -v jq` | `brew install jq` (macOS) |
| Jira credentials | `bash scripts/auth.sh` | Set env vars in `~/.zshenv` |

### Environment Variables

Add to `~/.zshenv`:

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

Uses the same API token type as Confluence. Generate at: https://id.atlassian.com/manage-profile/security/api-tokens

### Validation

Run `bash scripts/auth.sh` to verify credentials. If auth fails, the skill stops and prompts the user to add or update credentials in `~/.zshenv`, then `source ~/.zshenv`.

## Available Operations

### Issue Management

| Operation | Script Command |
|-----------|----------------|
| Get issue details | `issues.sh get --key PROJ-123` |
| Create issue | `issues.sh create --project PROJ --type Task --summary "..."` |
| Update issue fields | `issues.sh update --key PROJ-123 --fields '{"summary": "..."}'` |
| Delete issue | `issues.sh delete --key PROJ-123` |
| List transitions | `issues.sh transitions --key PROJ-123` |
| Transition issue | `issues.sh transition --key PROJ-123 --transition-id ID` |
| Assign issue | `issues.sh assign --key PROJ-123 --account-id ACC_ID` |
| Link issues | `issues.sh link --from PROJ-123 --to PROJ-456 --type "Blocks"` |
| Get watchers | `issues.sh watchers --key PROJ-123` |
| Add watcher | `issues.sh add-watcher --key PROJ-123 --account-id ACC_ID` |
| Get worklogs | `issues.sh worklog --key PROJ-123` |
| Add worklog | `issues.sh add-worklog --key PROJ-123 --time-spent "2h"` |

### Comment Operations

| Operation | Script Command |
|-----------|----------------|
| List comments | `comments.sh list --key PROJ-123` |
| Get comment | `comments.sh get --key PROJ-123 --comment-id ID` |
| Add comment | `comments.sh add --key PROJ-123 --body "..."` |
| Update comment | `comments.sh update --key PROJ-123 --comment-id ID --body "..."` |
| Delete comment | `comments.sh delete --key PROJ-123 --comment-id ID` |

### Search (JQL)

| Operation | Script Command |
|-----------|----------------|
| Search issues | `search.sh "<JQL query>" [--max-results N] [--fields field1,field2]` |

Common JQL patterns:

| Use Case | JQL Pattern |
|----------|-------------|
| My open issues | `assignee = currentUser() AND statusCategory != Done` |
| Sprint work | `sprint in openSprints() AND project = PROJ` |
| Recent bugs | `issuetype = Bug AND created >= -7d AND project = PROJ` |
| Blocked items | `status = Blocked OR status = "On Hold"` |
| Text search | `text ~ "search term" AND project = PROJ` |
| Unassigned | `assignee is EMPTY AND project = PROJ AND statusCategory != Done` |
| High priority | `priority in (Highest, High) AND statusCategory != Done` |
| Updated recently | `updated >= -1d AND project = PROJ` |

### Project Management

| Operation | Script Command |
|-----------|----------------|
| List projects | `projects.sh list` |
| Get project | `projects.sh get --key PROJ` |
| List versions | `projects.sh versions --key PROJ` |
| Create version | `projects.sh create-version --key PROJ --name "v1.0"` |
| List components | `projects.sh components --key PROJ` |
| Create component | `projects.sh create-component --key PROJ --name "Backend"` |
| List statuses | `projects.sh statuses --key PROJ` |

### Boards & Sprints (Agile API)

| Operation | Script Command |
|-----------|----------------|
| List boards | `boards.sh list --project PROJ` |
| Get board | `boards.sh get --board-id ID` |
| Board config | `boards.sh config --board-id ID` |
| List sprints | `boards.sh sprints --board-id ID` |
| Sprint issues | `boards.sh sprint-issues --sprint-id ID` |
| Move to sprint | `boards.sh move-to-sprint --sprint-id ID --issues PROJ-1,PROJ-2` |
| Get backlog | `boards.sh backlog --board-id ID` |
| Move to backlog | `boards.sh move-to-backlog --issues PROJ-1,PROJ-2` |
| Rank issues | `boards.sh rank --issues PROJ-1 --before PROJ-2` |

## MCP vs API Fallback Behavior

| Priority | Method | When Used |
|----------|--------|-----------|
| **Primary** | MCP tools (`mcp__atlassian__*`, `mcp__jira__*`, `mcp__plugin-atlassian-atlassian__*`) | Checked first; preferred for supported operations |
| **Secondary** | REST API via `curl` (bundled scripts) | For operations not covered by MCP, or when MCP unavailable |
| **Fallback** | Direct `curl` commands | When scripts are not accessible via `${CLAUDE_SKILL_DIR}` |

### MCP-Eligible Operations

The official Atlassian MCP connector typically supports:

- Get issue details
- Create issues
- Update issues
- Search via JQL
- Add comments

### Script-Only Operations

These **always require direct API calls** via scripts:

| Operation | Reason |
|-----------|--------|
| Board/sprint management | MCP connectors don't expose Agile API |
| Bulk operations | MCP connectors lack batch endpoints |
| Transition with custom fields | MCP connectors may not support field payloads on transition |
| Worklog management | MCP connectors typically lack worklog support |
| Component/version management | MCP connectors may not expose project admin |

## Key Behaviors

- **MCP-first when available**: unlike other connectors, Jira checks for MCP connector availability first and prefers MCP for supported operations
- **Dual API surfaces**: uses REST API v3 for core operations and Agile REST API v1 for boards, sprints, and backlog management
- **Shared Atlassian token**: uses the same API token type as Confluence — one token generation at https://id.atlassian.com covers both
- **Routing-based dispatch**: uses internal routing table to map workflows (story details, project management, search, issue lifecycle) to the correct scripts and actions
- **JSON output**: scripts output JSON to stdout, errors to stderr, non-zero exit on failure
- **API base**: REST API v3 at `${JIRA_URL}/rest/api/3`, Agile API v1 at `${JIRA_URL}/rest/agile/1.0`

## Invoked By

| Skill | When |
|-------|------|
| `/adk:docs-crud` | Context references Jira — reads issue details and comments for document context |
| `/adk:code-review-pr` | Context reading — reads linked Jira tickets for review context (via `--context` parameter) |
