---
name: dev-enhance
description: Use when enhancing an existing feature with impact analysis, incremental changes, and full verification of affected areas
user_invocable: true
arguments:
  - name: enhancement
    description: "Description of the enhancement or change to make"
    required: true
  - name: scope
    description: "Files or modules to focus on (comma-separated paths or module names)"
    required: false
  - name: branch
    description: "Branch name to create for this enhancement"
    required: false
---

# Feature Enhancement

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

## Preflight

Before starting, run:

`zsh scripts/check-skill-deps.zsh dev-enhance`

Verify that the project's test runner, linter, and type-checker are available and working.

## Flow

### 1. Understand Current Behavior

Analyze the existing code in the affected area:

- Read the relevant source files and tests
- Understand the current behavior, data flow, and contracts
- Identify public APIs, interfaces, and integration points
- Note existing test coverage and edge cases

If `scope` is provided, focus analysis there. Otherwise, infer the affected area from the enhancement description.

### 2. Impact Analysis

Identify the full impact of the proposed change:

- **Files to modify**: list every file that needs changes
- **Tests to update**: existing tests that will break or need extension
- **Docs to update**: READMEs, API docs, inline comments that reference changed behavior
- **Dependencies**: upstream and downstream code that depends on the changed interfaces
- **Risk areas**: parts of the change most likely to cause regressions

Present the impact analysis before proceeding. If the impact is larger than expected, confirm scope with the user.

### 3. Enhancement Plan

Create a plan that respects existing patterns:

- Order changes to minimize intermediate breakage
- Group related changes into reviewable units
- Define verification commands for each step
- Save the plan to `.temp/plans/<enhancement-slug>.md`

### 4. Implement Changes

For each planned step:

1. **Modify code** following existing patterns and conventions in the codebase
2. **Update affected tests** -- fix broken tests and add new coverage for changed behavior
3. **Verify** -- run lint, type-check, and tests after each step

Do not introduce new patterns when the codebase already has an established approach for the same concern.

### 5. Full Verification

Run the complete verification suite:

- All tests pass (not just the ones you changed)
- Linter reports no errors
- Type-checker reports no errors
- Build succeeds (if applicable)
- Manually verify the specific behavior that changed

### 6. Impact Summary

Present a before/after comparison:

```
## Enhancement Summary

Enhancement: <description>
Branch: <branch name or "current">

### Impact Analysis
- Files changed: N
- Tests updated: N
- Tests added: N
- Docs updated: N

### Before / After
| Aspect | Before | After |
|--------|--------|-------|
| <behavior> | <old> | <new> |
...

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/failure>

### Files Changed
- <file path>: <what changed>
...

### Risk Notes
- <any risks or things to watch for>
```

## Adjacent Skills

- `/devkit:dev-implement` for building new features from scratch
- `/devkit:review-local` for self-review of the changes before handoff
- `/devkit:dev-verify` for standalone verification
