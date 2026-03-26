---
name: quick-task
description: "Use for simple, well-defined tasks that don't need full planning overhead — direct execution with optional verification"
user_invocable: true
arguments:
  - name: task
    description: "Description of the task to execute"
    required: true
  - name: verify
    description: "Run verification after execution (default: true)"
    required: false
  - name: full
    description: "Enable plan-checking and verification even for quick tasks (default: false)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Quick Task Execution

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

## Preflight

Before execution, run:

`zsh scripts/check-skill-deps.zsh quick-task`

Verify that the project's test runner, linter, and type-checker are available and working so verification can run after execution.

## Complexity Classification

Before doing any work, classify the task to decide whether this skill is the right fit.

### Thresholds

| Signal | Trivial | Small | Medium | Too Complex |
|---|---|---|---|---|
| Files affected | 1 | 2-3 | 4-5 | >5 |
| Architectural decisions | none | none | minor | any significant |
| Requirements clarity | fully clear | fully clear | mostly clear | unclear or ambiguous |
| Cross-cutting concerns | none | none | 1 | >1 |
| New abstractions needed | none | none | none | any |
| Test surface | single unit | few units | module-level | cross-module |

### Routing Rules

- **Trivial**: single-file rename, typo fix, config tweak, adding an import, updating a constant. Execute directly in the parent session with no child agents.
- **Small**: adding a function, updating a component, fixing a bug with a known root cause. Use 1 child agent for implementation if the platform supports child agents.
- **Medium**: touches 4-5 files but the approach is clear and mechanical. Use 1 child agent for implementation.
- **Too Complex**: if the task touches >5 files, requires architectural decisions, introduces new abstractions, has unclear requirements, or spans multiple modules with cross-cutting concerns, stop and suggest:

```text
This task is too complex for quick execution. Recommended:
- /devkit:dev-implement — full planning, TDD, review checkpoints, and verification
- /devkit:dev-enhance — if this is an enhancement to an existing feature
```

## Flow

### 1. Classify Complexity

Analyze the task description against the thresholds above. Determine scope: `trivial`, `small`, or `medium`. If the task exceeds medium, route to `/devkit:dev-implement` and stop.

### 2. Confirm Approach

When `mode=interactive` (default), present the plan for approval:

```text
## Quick Task

Task: <description>
Approach: <concise explanation of what will be done>
Files affected: <list of files>
Estimated scope: [trivial|small|medium]

Proceed? [Y]es | [E]dit approach | [U]pgrade to full implementation
```

- **Y**: continue to execution.
- **E**: let the user refine the approach, then re-present.
- **U**: hand off to `/devkit:dev-implement` with the task context.

When `mode=auto-approve`, skip this step and proceed directly to execution.

### 3. Execute

Execute the task based on classified scope:

#### Trivial Tasks

Execute directly in the parent session. No child agents. Make the change, move to verification.

#### Small Tasks

If the platform supports child agents, launch 1 implementation agent with:
- The full task description
- The list of files to modify
- The approach from step 2
- Any relevant context from the codebase

If child agents are unavailable, execute directly in the parent session.

#### Medium Tasks

Launch 1 implementation agent with the same context as small tasks. Medium tasks always use a child agent when available because the file count (4-5) benefits from focused execution.

If child agents are unavailable, execute sequentially in the parent session.

### 4. Quick Verify

When `verify=true` (default), run targeted verification on affected files only:

1. **Tests**: run tests that cover the changed files. Use the project's test runner with file-scoped or pattern-based filtering when available.
2. **Lint**: run the linter on changed files only.
3. **Type-check**: run the type-checker if the project uses one.

If any check fails, fix the issue and re-verify. Limit fix attempts to 2 rounds before surfacing the failure to the user.

When `verify=false`, skip this step entirely.

### 5. Full Verify

When `full=true`, run additional verification on top of the quick verify:

1. **Plan check**: verify the implementation matches the stated approach from step 2.
2. **Goal-backward verification**: starting from the task description, confirm every requirement is satisfied by the changes made.
3. **Full test suite**: run the complete test suite, not just affected files.
4. **Build check**: if the project has a build step, confirm it succeeds.

Use `/devkit:dev-verify` patterns for parallel verification when child agents are available.

### 6. Commit

Offer to commit the changes with a descriptive message:

```text
Ready to commit. Suggested message:

  <type>: <concise description of what changed>

[C]ommit | [E]dit message | [S]kip
```

When `mode=auto-approve`, commit automatically with the suggested message.

### 7. Summary

Present the completion summary:

```text
## Quick Task Complete

Task: <description>
Files changed: N
Verification: [passed|skipped]
Commit: <sha or "not committed">
```

If `full=true`, expand the verification section:

```text
## Quick Task Complete

Task: <description>
Files changed: N

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/N/A>
- Plan check: <passed/issues>
- Goal check: <passed/issues>

Commit: <sha or "not committed">
```

## Adjacent Skills

- `/devkit:dev-implement` for complex features needing full planning, TDD, and review checkpoints
- `/devkit:dev-enhance` for enhancements to existing features with broader scope
- `/devkit:dev-verify` for standalone verification outside of quick-task
- `/devkit:plan-write` for standalone planning when a task turns out to need more structure
