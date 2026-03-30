# Fix Locally Stage

Apply review fixes to local code after a local or branch review. This stage runs when `--fix` is passed and there is no PR context.

---

## Prerequisites

This stage runs after the primary review stage (`local-review.md` or `branch-review.md`) has produced findings.

---

## Workflow

### Step 1: Prioritize Findings

Sort findings by severity:
1. Critical -- must fix immediately
2. High -- should fix before proceeding
3. Medium -- fix if time permits
4. Low -- note for later

### Step 2: Present Fix Plan

```text
## Fix Plan

### Critical (must fix)
1. <file:line> - <issue summary>
2. <file:line> - <issue summary>

### High (should fix)
1. <file:line> - <issue summary>

### Medium (optional)
1. <file:line> - <issue summary>

Fix: [A]ll critical+high | [C]ritical only | [S]elect individually | [N]one
```

### Step 3: Apply Fixes

For each approved fix:

1. Read the current file state.
2. Apply the suggested fix or implement the recommended approach.
3. Verify the fix doesn't break surrounding code.
4. Stage the change.

### Step 4: Verification

After all fixes are applied:

1. **Run tests** on affected files and their dependents.
2. **Run linter** if configured.
3. **Run type-checker** if configured.
4. Report results. If failures occur, identify which fix caused the failure and offer to revert it.

### Step 5: Commit Decision

```text
## Fixes Applied

Files modified: N
Tests: <pass/fail>
Lint: <clean/issues>
Types: <clean/issues>

Commit fixes? [Y]es with message | [N]o (keep staged) | [R]evert all
```

---

## Fix Principles

- **Verify before fixing**: confirm the issue exists in the current code before applying any change.
- **Minimal changes**: fix the reported issue without refactoring unrelated code.
- **Test after each fix**: run relevant tests to catch regressions early.
- **Preserve intent**: maintain the original code's intent and behavior, only fixing the identified issue.
- **One fix per concern**: don't bundle multiple unrelated fixes into one change.

---

## Summary

```text
## Local Fix Complete

Fixes applied: N (critical: N, high: N, medium: N)
Fixes skipped: N
Tests: <pass/fail>
Lint: <clean/issues>
Committed: [yes | no | reverted]
```
