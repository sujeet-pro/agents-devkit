---
name: dev-implement
description: Use when building a new feature end-to-end with planning, TDD, review checkpoints, and full verification before handoff
user_invocable: true
arguments:
  - name: feature
    description: "Description of the feature to build"
    required: true
  - name: plan
    description: "Path to an existing plan file to follow instead of generating a new one"
    required: false
  - name: tdd
    description: "Enable test-driven development: write failing tests before implementation (default: true)"
    required: false
  - name: branch
    description: "Branch name to create for this feature"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
  - name: spec
    description: "Path to a specification file to implement against (from /devkit:spec-write)"
    required: false
  - name: scope
    description: "Scope definition: v1, v2, full (default: v1 — only must-have requirements)"
    required: false
---

# Feature Implementation

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

## Preflight

Before implementation, run:

`zsh scripts/check-skill-deps.zsh dev-implement`

Verify that the project's test runner, linter, and type-checker are available and working. If a build tool is configured, confirm it produces a clean build from the current state.

## Flow

### 0. Interactive Discussion

When `mode=interactive` (default), run a discussion phase before planning:
- Surface gray areas and implementation choices
- Confirm scope boundaries (v1/v2/out-of-scope)
- Capture decisions in `.temp/plans/<feature-slug>-context.md`

Present decisions for approval:
```text
## Implementation Approach

Scope: [v1 only | full]
Key decisions:
1. <decision 1>
2. <decision 2>

Gray areas resolved:
- <gray area>: <chosen approach>

Proceed to planning? [Y]es | [E]dit decisions | [D]iscuss more
```

If `spec` is provided, load the specification and extract scope from it instead of asking.

### 1. Planning

If `plan` is provided, load it from the given path. Otherwise, create a plan following `/devkit:plan-write` conventions:

- Analyze the feature requirements
- Break into discrete, verifiable tasks
- Identify files to create or modify
- Define verification commands per task
- Save the plan to `.temp/plans/<feature-slug>.md`

Run a child-agent review pass on the plan before proceeding.

### 2. Branch Setup

If `branch` is provided, create and switch to the feature branch:

```bash
git checkout -b <branch>
```

If no branch is provided, work on the current branch.

### 3. Task Execution

For each planned task:

#### TDD Mode (default, `tdd=true`)

1. **Write failing test** -- specify the expected behavior in a test before writing any production code
2. **Run test** -- confirm it fails for the right reason
3. **Implement** -- write the minimum code to make the test pass
4. **Run test** -- confirm it passes
5. **Refactor** -- clean up while keeping tests green
6. **Verify** -- run lint, type-check, and full test suite

#### Non-TDD Mode (`tdd=false`)

1. **Implement** -- write the production code
2. **Write tests** -- cover the new behavior
3. **Verify** -- run lint, type-check, and full test suite

### 4. Review Checkpoints

After each major task, launch review child agents in parallel:

- `code-reviewer` for correctness, patterns, and maintainability
- a spec/requirement review pass to confirm the implementation matches the plan

Fix issues surfaced by reviewers before moving to the next task.

### 5. Final Verification

After all tasks are complete, run a full verification pass:

- All tests pass
- Linter reports no errors
- Type-checker reports no errors
- Build succeeds (if applicable)
- No regressions in existing functionality

Use `/devkit:dev-verify` patterns for parallel verification when child agents are available.

### 6. Summary

Present a completion summary:

```
## Implementation Summary

Feature: <feature description>
Branch: <branch name or "current">
Plan: <plan file path>

### Completed Tasks
- [x] Task 1: <description>
- [x] Task 2: <description>
...

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/failure>

### Files Changed
- <file path>: <what changed>
...
```

### 7. User Acceptance Testing

After automated verification passes, run interactive UAT:
- Extract testable deliverables from the spec or plan
- Walk user through each one using `/devkit:verify-uat` patterns
- Present each deliverable for manual verification:
```text
## UAT [N/total] - <testable behavior>

Expected: <what should happen>

Result: [P]ass | [F]ail (describe) | [S]kip
```

For failures, offer to loop back to Phase 3 (Task Execution) with a targeted fix.

Display final UAT summary alongside the implementation summary.

## Adjacent Skills

- `/devkit:plan-write` for standalone planning without implementation
- `/devkit:dev-tdd` for TDD-only focus without the full implementation flow
- `/devkit:dev-verify` for standalone verification
- `/devkit:pr-finalize` to prepare a pull request after implementation is complete
- `/devkit:spec-write` for writing specifications before implementation
- `/devkit:verify-uat` for standalone UAT
- `/devkit:session-handoff` for pausing long implementations
