---
name: dev
description: "adk - [routing] [dev] Development router — detects dev task type and routes to the right sub-skill"
user-invocable: true
argument-hint: "<task> [--help]"
allowed-tools: [Glob, Grep, Read]
workflow-tier: orchestrator
---

# Development Router

Lightweight entry point for all development tasks. Detects the task type from the user's input and routes to the appropriate sub-skill. Does not perform any dev work itself.

## Routing

Analyze the user's request and route to the matching skill:

| Signal | Route To | Invocation |
|--------|----------|------------|
| "implement", "build", "add feature", "fix bug", "debug", "TDD", "test-driven", "enhance", "improve", "quick fix", "worktree" | Build and implement | `/adk:dev-build` |
| "refactor", "extract", "rename across", "restructure", "simplify", "modernize", "clean up" | Refactor code | `/adk:dev-refactor` |
| "migrate", "upgrade from X to Y", "migration", "breaking changes", "update dependency" | Migrate or upgrade | `/adk:dev-migrate` |
| "commit", "commit message", "PR description", "changelog entry" | Commit and describe | `/adk:dev-commit` |

### Routing Rules

1. If the input mentions implementing, building, debugging, or enhancing code, route to `dev-build`.
2. If the input is about code restructuring without changing behavior, route to `dev-refactor`.
3. If the input mentions migrating from one version/framework to another, route to `dev-migrate`.
4. If the input is specifically about creating commits or PR descriptions, route to `dev-commit`.
5. If the input could be either build or refactor, prefer `dev-build` (it has internal modes for enhancement).
6. If ambiguous, ask the user what kind of development task they need.

### Parameter Forwarding

Pass all parameters from the user's original request to the target skill. The router does not consume any parameters except `--help`.

## Help

When `--help` is passed, show this routing table and the help for each sub-skill.

### Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:dev-build` | Implement features, debug issues, enhance code, run TDD — auto-detects mode |
| `/adk:dev-refactor` | Refactor code — extract, rename, restructure, simplify, modernize |
| `/adk:dev-migrate` | Migrate frameworks, libraries, or language versions |
| `/adk:dev-commit` | Create commits or PR descriptions with conventional messages |

## Adjacent Skills

- `/adk:code-review-pr` — review code after development
- `/adk:plan` — plan before development
- `/adk:spec` — write specifications before implementation
- `/adk:handoff` — pause long development sessions
