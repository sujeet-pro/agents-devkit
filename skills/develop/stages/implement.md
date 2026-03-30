# Implement Mode

Build a new feature end-to-end: from interactive discussion through planning, test-driven development, review checkpoints, and full verification.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze requirements, scan codebase for patterns, identify constraints; Focused research on chosen approach, produce proposal with task breakdown |
| 2. Approach Selection | yes | Surface gray areas, confirm scope, present 2-3 implementation approaches; Iterate on proposal — scope, architecture, testing strategy |
| 3. Planning | yes | Break into discrete tasks with TDD steps, group into waves |
| 4. Execute | yes | TDD cycle per task, review checkpoints between waves |
| 5. Validate & Learn | yes | Full test suite, lint, type-check, build, UAT |

## Exploration Guidance

- Read relevant source files, tests, and documentation
- Understand existing patterns, data flow, and contracts
- Identify public APIs, interfaces, and integration points
- Note existing test coverage and edge cases
- If `spec` is provided, load the specification and extract scope

**End with 2-3 suggested implementation approaches** ranked by fit:
- Each approach should describe: architecture, key files, testing strategy, risks
- Include trade-offs (complexity vs flexibility, speed vs correctness)

## Brainstorm

When `mode=interactive` (default), run a discussion phase:

- Present the suggested approaches from Exploration
- Surface gray areas and implementation choices
- Confirm scope boundaries (v1/v2/out-of-scope)
- The user picks an approach or mixes elements from multiple approaches

Present decisions for approval:
```text
## Implementation Approach

Scope: [v1 only | full]
Approach: [chosen approach or mix]
Key decisions:
1. <decision 1>
2. <decision 2>

Gray areas resolved:
- <gray area>: <chosen approach>

Proceed to deep research? [Y]es | [E]dit decisions | [D]iscuss more
```

Save brainstorm notes to `.temp/<feature-slug>/01-brainstorm.md`.

## Deep Research and Proposal

Research the chosen approach in depth:
- Launch child agents in parallel (see `references/agentic-teams.md`):
  - **Implementation researcher**: patterns, examples, libraries relevant to chosen approach
  - **Risk analyst**: edge cases, failure modes, performance implications
- Produce a finalized proposal at `./temp/proposal/<feature-slug>.md` containing:
  - Goals and acceptance criteria
  - Architecture and approach details
  - File-by-file change plan
  - Testing strategy (what to test, how)
  - Risks and mitigations

## Interactive Improvement

- Present the proposal to the user for review
- After each round of feedback, update `./temp/proposal/<feature-slug>.md` in place
- Continue until the user accepts the proposal

## Implementation Plan

Create a plan following `/plan --mode write` conventions:
- Break into discrete, verifiable tasks
- Identify files to create or modify per task
- Define verification commands per task
- Group independent tasks into waves for parallel execution
- Assign team shapes from `references/agentic-teams.md`
- Save the plan to `.temp/<feature-slug>/02-plan.md`

Run a child-agent review pass on the plan before proceeding.

## Execution Instructions

If `branch` is provided, create and switch to the feature branch:
```bash
git checkout -b <branch>
```

For each planned task, execute waves sequentially (tasks within each wave in parallel):

### TDD Mode (default, `tdd=true`)

1. **Write failing test** — specify the expected behavior in a test before writing any production code
2. **Run test** — confirm it fails for the right reason
3. **Implement** — write the minimum code to make the test pass
4. **Run test** — confirm it passes
5. **Refactor** — clean up while keeping tests green
6. **Verify** — run lint, type-check, and full test suite

### Non-TDD Mode (`tdd=false`)

1. **Implement** — write the production code
2. **Write tests** — cover the new behavior
3. **Verify** — run lint, type-check, and full test suite

### Review Checkpoints

After each wave, launch review child agents in parallel:
- `code-reviewer` for correctness, patterns, and maintainability
- A spec/requirement review pass to confirm the implementation matches the plan

Fix issues surfaced by reviewers before moving to the next wave.

Update progress in `.temp/<feature-slug>/03-progress.md`.

## Validation Criteria

Run the self-review loop (up to 10 iterations):

1. **Validation**: all tests pass, linter clean, type-checker clean, build succeeds
2. **Self-review**: check against proposal acceptance criteria, look for correctness and security issues
3. **Simplify**: remove over-engineering, unnecessary abstractions, verbose patterns
4. **Fix and re-validate**: fix any issues found, run validation again
5. **Stop when**: all checks pass and no further simplification possible

After automated verification, run interactive UAT:
- Extract testable deliverables from the spec or plan
- Walk user through each one:
```text
## UAT [N/total] - <testable behavior>

Expected: <what should happen>

Result: [P]ass | [F]ail (describe) | [S]kip
```

For failures, loop back to execution with a targeted fix.

Save summary to `.temp/<feature-slug>/04-summary.md`.

## Output Format

```markdown
## Implementation Summary

Feature: <feature description>
Branch: <branch name or "current">
Plan: <plan file path>

### Completed Tasks
- [x] Task 1: <description>
- [x] Task 2: <description>

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/failure>

### Files Changed
- <file path>: <what changed>

### UAT Results
- [x] <behavior 1>: Pass
- [x] <behavior 2>: Pass
```
