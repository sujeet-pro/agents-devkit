---
title: "bitbucket"
description: Bitbucket REST API operations — PRs, comments, repository access, pipelines
skill_name: bitbucket
category: connector
workflow_tier: helper
user_invocable: false
---

# bitbucket

Connector skill for Bitbucket Cloud operations. Uses REST API via `curl`/scripts with MCP as a secondary option.

## Purpose

Provides Bitbucket PR review posting, comment management, pipeline status, and repository access to task skills.

## Operations

| Operation | Method |
|-----------|--------|
| Fetch PR diff | REST API via `curl` |
| List PR comments | REST API |
| Post review comment | REST API |
| Pipeline status | REST API |
| Repository metadata | REST API |

## Dependencies

- `curl` (required)
- `BITBUCKET_TOKEN` environment variable
- Bitbucket MCP (optional)

## Invoked By

`code-review-pr`, `code-review-fix` (for Bitbucket PRs). Auto-detected from Bitbucket URLs.
