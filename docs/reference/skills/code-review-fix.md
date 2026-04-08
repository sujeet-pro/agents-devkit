---
title: "code-review-fix"
description: Read PR review comments, apply code fixes, reply to reviewers, resolve threads
skill_name: code-review-fix
category: task
workflow_tier: full
---

# code-review-fix

Reads unresolved PR review comments, categorizes them by severity, applies code fixes, replies to reviewers, and marks threads as resolved.

## When to Use

- Reviewers left comments on your PR and you want to address them efficiently
- Batch-fix all review feedback in one go

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<pr-url>` | GitHub or Bitbucket PR URL | (required) | The PR with review comments |
| `--filter` | `blocker`, `critical`, `all` | `all` | Only address comments at or above this severity |
| `--dry-run` | flag | off | Show what would be fixed without making changes |
| `--auto` | flag | off | Skip confirmations, fix everything |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm PR URL and scope |
| 1. Research | Fetch unresolved comments, categorize by severity |
| 2. Approach | Present categorized comments, user selects which to fix |
| 3. Planning | Create fix plan per comment |
| 4. Execute | Apply code changes, reply to reviewers, resolve threads |
| 5. Validate | Verify fixes, run tests if available |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `review-standards`, `interaction`, `github`/`bitbucket`.

## Examples

```text
/adk:code-review-fix https://github.com/org/repo/pull/42
/adk:code-review-fix https://github.com/org/repo/pull/42 --filter blocker
/adk:code-review-fix https://github.com/org/repo/pull/42 --dry-run
/adk:code-review-fix https://github.com/org/repo/pull/42 --auto
```
