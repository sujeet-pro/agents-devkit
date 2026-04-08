---
title: "bitbucket"
description: Bitbucket REST API operations — PR reviews, comments, repository access, and pipeline status
skill_name: bitbucket
category: connector
workflow_tier: helper
user_invocable: false
---

# bitbucket

Platform connector for Bitbucket Cloud. Wraps the Bitbucket REST API v2.0 via `curl`, providing PR management, inline review comments, task tracking, and repository access to task skills that need Bitbucket integration.

## Purpose

- Provide Bitbucket Cloud API access to task skills like `code-review-pr` and `code-review-fix`
- Fetch PR metadata, diffs, diffstats, commits, and pipeline status for review workflows
- Post inline and general comments, reply to threads, and manage tasks on PRs
- Read repository info, file contents, branches, and compare branches
- Approve, merge, decline, and manage PRs

## Authentication & Setup

### Requirements

| Dependency | Check | Install |
|------------|-------|---------|
| `curl` | `command -v curl` | Pre-installed on macOS/Linux |
| `jq` | `command -v jq` | `brew install jq` (macOS) |
| Bitbucket credentials | `bash scripts/auth.sh` | Set env vars in `~/.zshenv` |

### Environment Variables

Add to `~/.zshenv`:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_TOKEN="your-app-password"
```

Generate an app password at: https://bitbucket.org/account/settings/app-passwords/

Required scopes: `repository:read`, `pullrequest:read`, `pullrequest:write`

### Validation

Run `bash scripts/auth.sh` to verify credentials. If auth fails, the skill stops and prompts the user to add or update credentials in `~/.zshenv`, then `source ~/.zshenv`.

## Available Operations

### PR Management

| Operation | Script Command |
|-----------|----------------|
| Get PR details | `pr.sh get <ws> <repo> <pr-id>` |
| Get full diff | `pr.sh diff <ws> <repo> <pr-id>` |
| Get diffstat (file-level summary) | `pr.sh diffstat <ws> <repo> <pr-id>` |
| List PR commits | `pr.sh commits <ws> <repo> <pr-id>` |
| Check pipeline/build status | `pr.sh statuses <ws> <repo> <pr-id>` |
| List open PRs | `pr.sh list <ws> <repo> --state OPEN` |
| List merged PRs | `pr.sh list <ws> <repo> --state MERGED` |
| Create PR | `pr.sh create <ws> <repo> --title "..." --source-branch feature --dest-branch main` |
| Update PR | `pr.sh update <ws> <repo> <pr-id> --title "..." --description "..."` |
| Merge PR | `pr.sh merge <ws> <repo> <pr-id> --strategy squash --close-source true` |
| Decline PR | `pr.sh decline <ws> <repo> <pr-id>` |
| Approve PR | `pr.sh approve <ws> <repo> <pr-id>` |
| Remove approval | `pr.sh unapprove <ws> <repo> <pr-id>` |
| View activity feed | `pr.sh activity <ws> <repo> <pr-id>` |

### Comment Operations

| Operation | Script Command |
|-----------|----------------|
| List all comments | `comments.sh list <ws> <repo> <pr-id>` |
| Get single comment | `comments.sh get <ws> <repo> <pr-id> --comment-id N` |
| Post general comment | `comments.sh create <ws> <repo> <pr-id> --body "..."` |
| Post inline comment | `comments.sh create <ws> <repo> <pr-id> --body "..." --file path --line N` |
| Reply to comment | `comments.sh reply <ws> <repo> <pr-id> --parent-id N --body "..."` |
| Update comment | `comments.sh update <ws> <repo> <pr-id> --comment-id N --body "..."` |
| Delete comment | `comments.sh delete <ws> <repo> <pr-id> --comment-id N` |
| List tasks | `comments.sh list-tasks <ws> <repo> <pr-id>` |
| Create task | `comments.sh create-task <ws> <repo> <pr-id> --body "..." --comment-id N` |
| Resolve/reopen task | `comments.sh resolve-task <ws> <repo> <pr-id> --task-id N --state RESOLVED` |

### Repository Access

| Operation | Script Command |
|-----------|----------------|
| Get repo info | `repo.sh get <ws> <repo>` |
| Read file contents | `repo.sh file <ws> <repo> --path src/main.py --ref main` |
| List branches | `repo.sh branches <ws> <repo>` |
| List commits | `repo.sh commits <ws> <repo> --branch main` |
| Compare branches | `repo.sh diff <ws> <repo> --spec main..feature` |

## MCP vs API Fallback Behavior

| Priority | Method | When Used |
|----------|--------|-----------|
| **Primary** | REST API via `curl` (bundled scripts) | Always preferred. Works in any environment without MCP dependencies |
| **Secondary** | MCP tools (`mcp__bitbucket__*`) | Used when available, for supported operations |
| **Fallback** | Direct `curl` commands | When scripts are not accessible via `${CLAUDE_SKILL_DIR}`, construct `curl` commands from reference docs |

The API-first approach ensures the connector works in any environment (Claude Code, Codex, etc.) without MCP dependencies. If scripts are inaccessible, direct `curl` commands are constructed — new shell scripts are never created.

## Key Behaviors

- **API-first**: direct REST API calls via bundled `scripts/` always preferred over MCP tools
- **Inline comments default**: "comments" means inline (file + line) comments unless explicitly requesting general PR-level comments
- **Structured script interface**: all scripts accept subcommands with consistent patterns — `<script>.sh <action> <workspace> <repo> [args...]`
- **JSON output**: scripts output JSON to stdout, errors to stderr, non-zero exit on failure
- **API base**: all endpoints use `https://api.bitbucket.org/2.0`
- **Task management**: supports creating, resolving, and reopening tasks attached to PR comments

## Invoked By

| Skill | When |
|-------|------|
| `/adk:code-review-pr` | Target is a Bitbucket PR — fetches PR details, diff, posts inline comments, manages tasks |
| `/adk:code-review-fix` | Target is a Bitbucket PR — reads unresolved comments/tasks, applies fixes, replies to threads |
