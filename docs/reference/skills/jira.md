---
title: "jira"
description: Jira REST API operations — issues, comments, search, projects, boards, sprints
skill_name: jira
category: connector
workflow_tier: helper
user_invocable: false
---

# jira

Connector skill for Jira Cloud operations. Uses REST API via scripts, with MCP for common issue operations.

## Purpose

Provides Jira issue management, search, comment handling, project/board/sprint operations to task skills needing project context.

## Operations

| Operation | Method |
|-----------|--------|
| Search issues (JQL) | MCP or REST API |
| Read issue details | MCP or REST API |
| Create issue | MCP or REST API |
| Update issue | REST API |
| Add comment | MCP or REST API |
| Board/sprint data | REST API |
| Project metadata | REST API |

## Dependencies

- `curl` (required)
- `JIRA_TOKEN` + `JIRA_URL` environment variables
- Jira MCP (optional, preferred for issue operations)

## Invoked By

`docs-crud` (for context), `code-review-pr` (for context reading).
