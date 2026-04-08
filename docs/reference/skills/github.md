---
title: "github"
description: GitHub operations via gh CLI — PRs, comments, issues, and repository access
skill_name: github
category: connector
workflow_tier: helper
user_invocable: false
---

# github

Connector skill for GitHub operations. Uses `gh` CLI as the primary interface with MCP as an optional fallback.

## Purpose

Provides GitHub PR review posting, comment management, issue operations, and repository access to task skills.

## Operations

| Operation | Method |
|-----------|--------|
| Fetch PR diff | `gh pr diff` |
| List PR comments | `gh api` |
| Post review comment | `gh api` |
| Resolve comment thread | `gh api` |
| Create/read issues | `gh issue` |
| Repository metadata | `gh repo` |

## Dependencies

- `gh` CLI (required)
- `GITHUB_TOKEN` environment variable
- GitHub MCP (optional fallback)

## Invoked By

`code-review-pr`, `code-review-fix` (for GitHub PRs). Auto-detected from GitHub URLs.
