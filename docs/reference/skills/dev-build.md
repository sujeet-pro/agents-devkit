---
title: "dev-build"
description: Implement features, debug issues, enhance code, or run TDD — auto-detects mode
skill_name: dev-build
category: task
workflow_tier: full
---

# dev-build

The primary development skill. Implements features, debugs issues, enhances existing code, and supports TDD. Auto-detects the mode from your request, or set it explicitly.

## When to Use

- Build a new feature from scratch or from a spec
- Fix a bug or debug an issue
- Enhance or extend existing functionality
- Write tests first, then implement (TDD)
- Make a quick one-off change
- Experiment in an isolated worktree

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `implement`, `enhance`, `debug`, `tdd`, `verify`, `worktree`, `quick` | auto-detect | Development mode |
| `--spec` | file path | — | Reference specification for the implementation |
| `--plan` | file path | — | Reference plan to execute |
| `--fix` | flag | off | Auto-fix issues found |
| `--tdd` | flag | off | Enable TDD mode (alias for `--mode tdd`) |
| `--full` | flag | off | Include test generation alongside implementation |
| `--branch` | branch name | — | Branch name for worktree mode |
| `--scope` | path(s) | repo root | Limit changes to specific directories |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Mode Detection

| Signal in Request | Detected Mode |
|-------------------|---------------|
| "implement", "build", "create", "add" | `implement` |
| "fix", "bug", "error", "broken", "debug" | `debug` |
| "enhance", "improve", "extend", "optimize" | `enhance` |
| "tdd", "test-driven", "tests first" | `tdd` |
| "verify", "check", "validate" | `verify` |
| "experiment", "try", "prototype" | `worktree` |
| "quick", "simple", "just" | `quick` |

## Workflow

Full 6-phase workflow for `implement`, `enhance`, `tdd`. Abbreviated for `debug`, `verify`, `worktree`, `quick` (phases 2–5 skipped).

| Phase | Action |
|-------|--------|
| 0. Intent | Detect mode, confirm scope and requirements |
| 1. Research | Analyze codebase, understand patterns, load coding guidelines |
| 2. Approach | Present implementation approaches, user selects |
| 3. Planning | Break into tasks/waves |
| 4. Execute | Implement changes with parallel agents when applicable |
| 5. Validate | Run tests, self-review, check for regressions |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams` (medium+), `interaction`.

## Examples

```text
/adk:dev-build implement user authentication with OAuth2
/adk:dev-build --mode debug fix the memory leak in WebSocket handler
/adk:dev-build --mode tdd implement rate limiter with sliding window
/adk:dev-build --mode enhance add pagination to the users list API
/adk:dev-build --mode quick add a loading spinner to the dashboard
/adk:dev-build --mode worktree --branch experiment/new-auth try Passport.js
/adk:dev-build --spec ./docs/specs/auth.md --full implement the auth module
/adk:dev-build --scope src/api/ add rate limiting to all endpoints
```
