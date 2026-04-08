---
title: "code-review"
description: Code review router — detects review type and routes to the right sub-skill
skill_name: code-review
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# code-review

Lightweight entry point for all code review tasks. Detects the review type from the user's input and routes to the appropriate sub-skill. Does not perform any review work itself.

## When to Use

- Start a code review without knowing which specific sub-skill to invoke
- Let the router auto-detect the right review workflow from your input
- Get a quick overview of available code review sub-skills via `--help`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<target>` | PR URL, branch name, keywords, or omitted | auto-detect | What to review. The router analyzes this to determine the correct sub-skill |
| `--help` | flag | — | Show routing table and help for each sub-skill |

All other parameters are forwarded unchanged to the target sub-skill.

## Routing Table

| Signal | Route To | Invocation |
|--------|----------|------------|
| PR URL (`github.com/*/pull/*`, `bitbucket.org/*/pull-requests/*`), "PR", "pull request", "my changes", "review this PR", diff/patch input | Code review a PR | `/adk:code-review-pr` |
| "fix comments", "address feedback", "resolve", "apply fixes", "PR comments" | Fix review comments | `/adk:code-review-fix` |
| "repo", "codebase", "architecture", "tech debt", "review this repo", no specific target | Review entire repository | `/adk:code-review-repo` |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Input contains a PR URL** | Always routes to `code-review-pr` regardless of other keywords |
| **Input mentions fixing review comments** | Routes to `code-review-fix` |
| **Input is about reviewing a whole repo** | Routes to `code-review-repo` |
| **Ambiguous input** | Asks the user: "Are you reviewing a PR, fixing review comments, or auditing the codebase?" |
| `--help` | Shows routing table and the help output for each sub-skill |

## Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:code-review-pr` | Review code changes in a PR, local diff, or branch. Supports review, fix, describe, finalize actions |
| `/adk:code-review-repo` | Review an entire repository for architecture, code quality, patterns, and tech debt |
| `/adk:code-review-fix` | Fix PR review comments — read comments, apply code fixes, reply to reviewers |

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:docs-review` | Review documentation (not code) |
| `/adk:audit` | Broader audit with security, performance, and dependency focus |
| `/adk:dev-build` | Implement features and fix bugs |

## Examples

```
/adk:code-review https://github.com/org/repo/pull/42
/adk:code-review fix the review comments on my PR
/adk:code-review review this repo for tech debt
/adk:code-review --help
```
