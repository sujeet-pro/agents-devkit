---
name: dev-refactor
description: "adk - [full] [dev] Refactor code — extract, rename, restructure, simplify, or modernize patterns across files with safe, tested transformations"
user-invocable: true
argument-hint: "<description> [--scope <path>] [--pattern extract|rename|restructure|simplify|modernize] [--auto] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: standard-task
---

# Refactor

Systematic code refactoring with safety guarantees. Analyzes the codebase, identifies the transformation scope, generates a plan with test coverage, and applies changes incrementally with validation after each step.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents for parallel analysis and refactoring. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

---

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<description>` | free text | required | What to refactor and why |
| `--scope` | `<path>` | auto-detect | Limit refactoring to specific files/directories |
| `--pattern` | `extract`, `rename`, `restructure`, `simplify`, `modernize` | auto-detect | Force a specific refactoring pattern |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Behavior Variations

- **`extract`**: Extract functions, classes, modules, or components from existing code
- **`rename`**: Rename symbols across the codebase (variables, functions, classes, files)
- **`restructure`**: Reorganize file/directory structure, move modules, update imports
- **`simplify`**: Reduce complexity — flatten nested logic, remove dead code, consolidate duplicates
- **`modernize`**: Update to modern patterns — replace deprecated APIs, adopt new language features
- **Auto-detect** (default): analyzes the request and picks the best pattern

### Examples

```text
/adk:dev-refactor extract the auth logic from UserController into a separate AuthService
/adk:dev-refactor rename getUserData to fetchUserProfile across the codebase
/adk:dev-refactor restructure src/utils into domain-specific modules
/adk:dev-refactor simplify the payment processing flow -- too many nested callbacks
/adk:dev-refactor modernize the error handling to use Result types
```

---

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

## Safety Guarantees

1. **Test first**: verify existing tests pass before any changes
2. **Incremental**: apply changes in small, reversible steps
3. **Validate after each step**: run tests between transformation steps
4. **Preserve behavior**: refactoring must not change observable behavior
5. **Rollback ready**: every step can be reverted independently

---

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

Generate ordered steps, each independently verifiable:

```
## Refactoring Plan

**Pattern**: extract
**Scope**: 8 files, 3 modules
**Risk**: Low — all affected code has test coverage

| Step | Change | Files | Verify |
|------|--------|-------|--------|
| 1 | Create AuthService class | 1 new file | tests pass |
| 2 | Move auth methods from UserController | 2 files | tests pass |
| 3 | Update imports in consumers | 5 files | tests pass |
| 4 | Remove dead code from UserController | 1 file | tests pass |
```

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

---

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

---

## Adjacent Skills

- `/adk:dev-build` for implementing new features after refactoring
- `/adk:code-review-pr` for reviewing the refactoring PR
- `/adk:audit` for identifying refactoring opportunities
- `/adk:coding` for loading language-specific refactoring patterns
