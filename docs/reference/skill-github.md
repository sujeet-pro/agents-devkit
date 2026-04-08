---
title: "github"
description: GitHub operations via gh CLI — PR reviews, comments, issues, and repository access
skill_name: github
category: connector
workflow_tier: helper
user_invocable: false
---

# github

Platform connector for GitHub. Wraps all GitHub operations through the `gh` CLI, providing PR management, code reviews, inline comments, repository access, and issue tracking to task skills that need GitHub integration.

## Purpose

- Provide GitHub API access to task skills like `code-review-pr` and `code-review-fix`
- Fetch PR metadata, diffs, changed files, and CI status for review workflows
- Post review comments (inline and general), reply to threads, and resolve conversations
- Read repository contents, branches, commits, and search code
- Manage issues: create, update, close, label, assign, and comment

## Authentication & Setup

### Requirements

| Dependency | Check | Install |
|------------|-------|---------|
| `gh` CLI | `command -v gh` | `brew install gh` (macOS) or [cli.github.com](https://cli.github.com/manual/installation) |
| Auth | `gh auth status` | `gh auth login` (browser-based, one-time) |

If `gh` is not installed or not authenticated, the skill stops and prompts the user with setup instructions. Run `/adk:setup --tool gh` to install and verify.

### No Environment Variables Required

Unlike other connectors, `github` uses `gh auth login` for authentication — no manual token or environment variable configuration needed. The `gh` CLI handles auth tokens, pagination, and rate limiting automatically.

## Available Operations

### PR Management

| Operation | Command Pattern |
|-----------|----------------|
| Get PR details | `gh pr view <number>` |
| Get PR diff | `gh pr diff <number>` |
| Get changed files | `gh pr view <number> --json files` |
| Create PR | `gh pr create` |
| Update PR | `gh pr edit <number>` |
| Merge PR | `gh pr merge <number>` |
| Check CI status | `gh pr checks <number>` |

### Reviews & Comments

| Operation | Command Pattern |
|-----------|----------------|
| Post review with inline comments | `gh api` with review create endpoint |
| List review comments | `gh api` repos endpoint |
| Reply to a comment | `gh api` with reply endpoint |
| Resolve a thread | `gh api` with resolve endpoint |
| Create standalone comment | `gh api` with comment endpoint |

### Repository Access

| Operation | Command Pattern |
|-----------|----------------|
| Read file contents | `gh api` with contents endpoint (supports `ref` param for branch) |
| Search code | `gh search code` |
| List branches | `gh api` with branches endpoint |
| Compare branches | `gh api` with compare endpoint |
| List commits | `gh api` with commits endpoint |
| Get single commit | `gh api` with commit endpoint |

### Issue Management

| Operation | Command Pattern |
|-----------|----------------|
| View an issue | `gh issue view <number>` |
| Create an issue | `gh issue create` |
| Update an issue | `gh issue edit <number>` |
| Close an issue | `gh issue close <number>` |
| Comment on an issue | `gh issue comment <number>` |
| Manage labels | `gh issue edit --add-label` / `--remove-label` |
| Assign users | `gh issue edit --add-assignee` |
| List milestones | `gh api` with milestones endpoint |

## MCP vs CLI Fallback Behavior

| Priority | Method | When Used |
|----------|--------|-----------|
| **Primary** | `gh` CLI | Always preferred. Handles auth, pagination, rate limiting automatically |
| **Secondary** | MCP tools (`mcp__github__*`) | Used when available, as a convenience option |
| **Fallback** | `gh` CLI | When MCP tools fail (auth error, missing scope, unavailable) |

The `gh` CLI is always the reliable fallback — never `curl` with raw GitHub APIs. MCP tools are a secondary convenience, not a dependency.

## Key Behaviors

- **gh CLI first**: all operations go through `gh` CLI; MCP is supplementary, never primary
- **Preflight validation**: checks `gh` install and auth status before any operation; stops with actionable instructions on failure
- **Routing-based dispatch**: uses internal routing table to map use cases to the correct operation reference and command pattern
- **Idempotency-aware**: review comment operations check for existing comments before posting to avoid duplicates
- **Inline comments default**: when posting review feedback, inline (file + line) comments are preferred over general PR comments

## Invoked By

| Skill | When |
|-------|------|
| `/adk:code-review-pr` | Target is a GitHub PR — fetches PR details, diff, posts review comments |
| `/adk:code-review-fix` | Target is a GitHub PR — reads unresolved comments, applies fixes, resolves threads |
