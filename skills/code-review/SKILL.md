---
name: code-review
description: "adk - [routing] [code-review] Code review router — detects review type and routes to the right sub-skill"
user-invocable: true
argument-hint: "<target> [--help]"
allowed-tools: [Glob, Grep, Read]
workflow-tier: orchestrator
maturity: stable
---

# Code Review Router

Lightweight entry point for all code review tasks. Detects the review type from the user's input and routes to the appropriate sub-skill. Does not perform any review work itself.

## Routing

Analyze the user's request and route to the matching skill:

| Signal | Route To | Invocation |
|--------|----------|------------|
| PR URL (github.com/*/pull/*, bitbucket.org/*/pull-requests/*), "PR", "pull request", "my changes", "review this PR", diff/patch input | Code review a PR | `/adk:code-review-pr` |
| "fix comments", "address feedback", "resolve", "apply fixes", "PR comments" | Fix review comments | `/adk:code-review-fix` |
| "repo", "codebase", "architecture", "tech debt", "review this repo", no specific target | Review entire repository | `/adk:code-review-repo` |

### Routing Rules

1. If the input contains a PR URL, always route to `code-review-pr` regardless of other keywords.
2. If the input mentions fixing or addressing existing review comments, route to `code-review-fix`.
3. If the input is about reviewing a whole repo or codebase, route to `code-review-repo`.
4. If ambiguous, ask the user: "Are you reviewing a PR, fixing review comments, or auditing the codebase?"

### Parameter Forwarding

Pass all parameters from the user's original request to the target skill. The router does not consume any parameters except `--help`.

## Help

When `--help` is passed, show this routing table and the help for each sub-skill.

### Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:code-review-pr` | Review code changes in a PR, local diff, or branch. Supports review, fix, describe, finalize actions. |
| `/adk:code-review-repo` | Review an entire repository for architecture, code quality, patterns, and tech debt. |
| `/adk:code-review-fix` | Fix PR review comments — read comments, apply code fixes, reply to reviewers. |

## Adjacent Skills

- `/adk:docs-review` — review documentation (not code)
- `/adk:audit` — broader audit with security, performance, and dependency focus
- `/adk:dev-build` — implement features and fix bugs
