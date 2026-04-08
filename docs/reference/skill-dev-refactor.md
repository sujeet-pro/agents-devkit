---
title: "dev-refactor"
description: Refactor code — extract, rename, restructure, simplify, or modernize patterns across files with safe, tested transformations
skill_name: dev-refactor
category: task
workflow_tier: full
user_invocable: true
---

# dev-refactor

Systematic code refactoring with safety guarantees. Analyzes the codebase, identifies the transformation scope, generates a plan with test coverage, and applies changes incrementally with validation after each step.

## When to Use

- Extract functions, classes, modules, or components from existing code
- Rename symbols (variables, functions, classes, files) across the codebase
- Reorganize file/directory structure, move modules, update imports
- Reduce complexity — flatten nested logic, remove dead code, consolidate duplicates
- Update to modern patterns — replace deprecated APIs, adopt new language features

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | free text | required | What to refactor and why |
| `--scope` | `<path>` | auto-detect | Limit refactoring to specific files/directories |
| `--pattern` | `extract` \| `rename` \| `restructure` \| `simplify` \| `modernize` | auto-detect | Force a specific refactoring pattern |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Pattern | Behavior |
|---------|----------|
| `extract` | Extract functions, classes, modules, or components from existing code |
| `rename` | Rename symbols across the codebase (variables, functions, classes, files) |
| `restructure` | Reorganize file/directory structure, move modules, update imports |
| `simplify` | Reduce complexity — flatten nested logic, remove dead code, consolidate duplicates |
| `modernize` | Update to modern patterns — replace deprecated APIs, adopt new language features |
| Auto-detect (default) | Analyzes the request and picks the best pattern |

## Safety Guarantees

1. **Test first**: verify existing tests pass before any changes
2. **Incremental**: apply changes in small, reversible steps
3. **Validate after each step**: run tests between transformation steps
4. **Preserve behavior**: refactoring must not change observable behavior
5. **Rollback ready**: every step can be reverted independently

## Key Behaviors

- **Scope analysis**: maps all files and symbols affected, counts blast radius, checks test coverage
- **Safety baseline**: runs existing tests before changes and records pre-existing failures
- **Incremental execution**: applies each step sequentially with test runs between steps
- **Ordered transformation plan**: generates steps that are each independently verifiable
- **Quality metrics**: reports cyclomatic complexity, lines of code, and test coverage before and after

## Workflow

Follows the 6-phase workflow. All phases apply for refactoring tasks.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm what to refactor, identify pattern |
| 1. Research & Options | yes | Scope analysis — files, symbols, dependencies, blast radius |
| 2. Approach Selection | yes | Present refactoring strategy options |
| 3. Planning | yes | Generate ordered transformation plan with verification steps |
| 4. Execute | yes | Apply changes step by step, run tests after each |
| 5. Validate & Learn | yes | Full test suite, lint check, complexity metrics, summary |

## Refactoring Process

### 1. Scope Analysis

- Identify all files and symbols affected by the refactoring
- Map dependencies and usage sites
- Estimate blast radius — how many files, tests, and downstream consumers are impacted
- Check for existing test coverage on affected code

### 2. Safety Baseline

- Run the existing test suite and record results
- Note any pre-existing failures to avoid false attribution
- If test coverage is low on affected code, suggest adding tests first

### 3. Transformation Plan

Generate ordered steps, each independently verifiable with a step-by-step table showing the change, files affected, and verification criteria.

### 4. Execution

- Apply each step sequentially
- Run tests after each step
- If a test fails, diagnose and fix before proceeding
- Track which steps are complete for resume capability

### 5. Validation

- Run full test suite
- Verify no new lint warnings
- Check that the refactored code is simpler (fewer lines, lower complexity, clearer naming)
- Produce a summary of what changed and why

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping. |
| `communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `preflight-check` | before work | Run preflight.py for tool dependencies. |
| `output-format` | producing output | short/standard/detailed verbosity. |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents for parallel analysis and refactoring. |
| `interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

## Output Format

```markdown
# Refactoring Report

## Summary
- **Pattern**: extract / rename / restructure / simplify / modernize
- **Files changed**: N
- **Lines added/removed**: +N / -N
- **Tests**: all passing

## Changes
1. Step 1: [description] — [files]
2. Step 2: [description] — [files]

## Quality Metrics
- Cyclomatic complexity: before → after
- Lines of code: before → after
- Test coverage on affected code: N%
```

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:dev-build` | Implementing new features after refactoring |
| `/adk:code-review-pr` | Reviewing the refactoring PR |
| `/adk:audit` | Identifying refactoring opportunities |
| `/adk:coding` | Loading language-specific refactoring patterns |

## Examples

```
/adk:dev-refactor extract the auth logic from UserController into a separate AuthService
/adk:dev-refactor rename getUserData to fetchUserProfile across the codebase
/adk:dev-refactor restructure src/utils into domain-specific modules
/adk:dev-refactor simplify the payment processing flow -- too many nested callbacks
/adk:dev-refactor modernize the error handling to use Result types
```
