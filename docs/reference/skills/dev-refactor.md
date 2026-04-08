---
title: "dev-refactor"
description: Safe, tested code refactoring — extract, rename, restructure, simplify, modernize
skill_name: dev-refactor
category: task
workflow_tier: full
---

# dev-refactor

Performs safe, tested code transformations: extracting modules, renaming symbols, restructuring directories, simplifying complexity, and modernizing patterns.

## When to Use

- Extract logic into separate functions, classes, or modules
- Rename symbols across the codebase
- Reorganize file and directory structure
- Reduce cyclomatic complexity
- Modernize to current language features

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<description>` | free text | (required) | What to refactor |
| `--pattern` | `extract`, `rename`, `restructure`, `simplify`, `modernize` | auto-detect | Refactoring pattern |
| `--scope` | path(s) | repo root | Limit changes to specific directories |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Detect refactoring pattern, confirm scope |
| 1. Research | Analyze current code, identify dependencies and test coverage |
| 2. Approach | Present refactoring strategy, user approves |
| 3. Planning | Break into safe, incremental steps |
| 4. Execute | Apply transformations, maintain test coverage |
| 5. Validate | Run tests, verify no regressions, self-review |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams`, `interaction`.

## Examples

```text
/adk:dev-refactor extract validation logic from UserController into ValidationService
/adk:dev-refactor --pattern rename rename getUserData to fetchUserProfile
/adk:dev-refactor --pattern restructure move to feature-based folder structure
/adk:dev-refactor --pattern simplify reduce complexity in the payment module
/adk:dev-refactor --pattern modernize convert callbacks to async/await
/adk:dev-refactor --scope src/services/ simplify error handling
```
