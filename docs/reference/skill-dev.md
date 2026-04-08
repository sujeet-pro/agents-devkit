---
title: "dev"
description: Development router — detects dev task type and routes to the right sub-skill
skill_name: dev
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# dev

Lightweight entry point for all development tasks. Detects the task type from the user's input and routes to the appropriate sub-skill. Does not perform any dev work itself — it analyzes intent, matches signals, and forwards all parameters to the target skill.

## When to Use

- Start a development task without knowing which specific sub-skill to invoke
- Let the router auto-detect whether the task is build, refactor, migrate, or commit
- Get an overview of all available dev sub-skills with `--help`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | free text | required | Description of the development task to route |
| `--help` | flag | — | Show routing table and help for each sub-skill |

All other parameters are forwarded to the target sub-skill unchanged.

## Routing Logic

The router analyzes the user's request and matches it to a sub-skill based on keyword signals:

| Signal | Route To | Invocation |
|--------|----------|------------|
| "implement", "build", "add feature", "fix bug", "debug", "TDD", "test-driven", "enhance", "improve", "quick fix", "worktree" | Build and implement | `/adk:dev-build` |
| "refactor", "extract", "rename across", "restructure", "simplify", "modernize", "clean up" | Refactor code | `/adk:dev-refactor` |
| "migrate", "upgrade from X to Y", "migration", "breaking changes", "update dependency" | Migrate or upgrade | `/adk:dev-migrate` |
| "commit", "commit message", "PR description", "changelog entry" | Commit and describe | `/adk:dev-commit` |

## Routing Rules

1. If the input mentions implementing, building, debugging, or enhancing code, route to `dev-build`
2. If the input is about code restructuring without changing behavior, route to `dev-refactor`
3. If the input mentions migrating from one version/framework to another, route to `dev-migrate`
4. If the input is specifically about creating commits or PR descriptions, route to `dev-commit`
5. If the input could be either build or refactor, prefer `dev-build` (it has internal modes for enhancement)
6. If ambiguous, ask the user what kind of development task they need

## Downstream Skills

| Skill | Description |
|-------|-------------|
| `/adk:dev-build` | Implement features, debug issues, enhance code, run TDD — auto-detects mode |
| `/adk:dev-refactor` | Refactor code — extract, rename, restructure, simplify, modernize |
| `/adk:dev-migrate` | Migrate frameworks, libraries, or language versions |
| `/adk:dev-commit` | Create commits or PR descriptions with conventional messages |

## Key Behaviors

- **Signal-based routing**: matches keywords and intent patterns to select the right sub-skill
- **Parameter forwarding**: passes all parameters from the original request to the target skill untouched
- **Ambiguity handling**: when signals overlap (e.g., build vs refactor), prefers `dev-build`; when truly ambiguous, asks the user
- **No execution**: the router never performs development work itself

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:code-review-pr` | Review code after development |
| `/adk:plan` | Plan before development |
| `/adk:spec` | Write specifications before implementation |
| `/adk:handoff` | Pause long development sessions |

## Examples

```
/adk:dev add user authentication with JWT tokens
/adk:dev fix the login form crash on empty email
/adk:dev refactor the auth logic into a separate service
/adk:dev migrate react@17 to react@19
/adk:dev commit
/adk:dev --help
```
