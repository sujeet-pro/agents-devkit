# Quick Task Mode

Fast execution for simple, well-defined tasks. Escalate to implement mode when complexity exceeds thresholds.

## Workflow

This stage uses the **Quick Action** workflow: confirm → execute → verify.

## Exploration Guidance

Classify the task against complexity thresholds:

| Signal | Trivial | Small | Medium | Too Complex |
|---|---|---|---|---|
| Files affected | 1 | 2-3 | 4-5 | >5 |
| Architectural decisions | none | none | minor | any significant |
| Requirements clarity | fully clear | fully clear | mostly clear | unclear |
| New abstractions | none | none | none | any |

**Too Complex?** Stop and re-route to implement or enhance mode.

## Execution Instructions

### 1. Confirm Approach

When `mode=interactive` (default):
```text
## Quick Task

Task: <description>
Approach: <concise explanation>
Files affected: <list>
Scope: [trivial|small|medium]

Proceed? [Y]es | [E]dit approach | [U]pgrade to full implementation
```

When `mode=auto-approve`, skip confirmation.

### 2. Implement

- **Trivial**: execute directly, no child agents
- **Small**: 1 child agent if available, otherwise direct
- **Medium**: 1 child agent with full context

### 3. Quick Verify

When `verify=true` (default):
1. Run tests covering changed files (scoped)
2. Run linter on changed files
3. Run type-checker if available

If any check fails, fix and re-verify (max 2 rounds).

### 4. Full Verify (optional)

When `full=true`:
1. Plan check: implementation matches stated approach
2. Goal-backward verification: every requirement satisfied
3. Full test suite
4. Build check

### 5. Commit (optional)

```text
Ready to commit. Suggested message:
  <type>: <concise description>

[C]ommit | [E]dit message | [S]kip
```

## Validation Criteria

1. Task completed as described
2. No unnecessary changes beyond the task
3. Verification passed (targeted or full)
4. No over-engineering introduced
5. Code follows existing codebase patterns

## Output Format

```markdown
## Quick Task Complete

Task: <description>
Files changed: N
Verification: [passed|skipped]
Commit: <sha or "not committed">
```

When `full=true`:
```markdown
## Quick Task Complete

Task: <description>
Files changed: N

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/N/A>

Commit: <sha or "not committed">
```
