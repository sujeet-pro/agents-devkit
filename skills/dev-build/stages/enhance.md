# Enhance Mode

Enhance an existing feature with impact analysis, incremental changes, and full verification. Unlike implement mode (new features from scratch), this mode respects existing patterns and minimizes disruption.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze current behavior, scan affected code, identify constraints; Impact analysis + focused research on chosen approach |
| 2. Approach Selection | yes | Present 2-3 enhancement approaches with impact trade-offs; Iterate on scope and approach with user |
| 3. Planning | yes | Order changes to minimize intermediate breakage |
| 4. Execute | yes | Incremental changes following existing patterns |
| 5. Validate & Learn | yes | Full verification including regression checks |

## Exploration Guidance

Analyze the existing code in the affected area:
- Read the relevant source files and tests
- Understand the current behavior, data flow, and contracts
- Identify public APIs, interfaces, and integration points
- Note existing test coverage and edge cases

If `scope` is provided, focus analysis there. Otherwise, infer the affected area.

**End with 2-3 suggested enhancement approaches** with trade-offs:
- Minimal change vs. deeper refactor
- Backward compatibility vs. clean break
- Scope of affected files and tests

## Brainstorm

- Present the suggested approaches with concrete impact estimates
- Ask targeted clarifying questions about scope boundaries
- The user picks an approach or mixes elements
- Confirm what is in-scope vs. out-of-scope
- Save to `.temp/<enhancement-slug>/01-brainstorm.md`

## Deep Research and Proposal

Identify the full impact of the proposed change:
- **Files to modify**: list every file that needs changes
- **Tests to update**: existing tests that will break or need extension
- **Docs to update**: READMEs, API docs, inline comments
- **Dependencies**: upstream and downstream code that depends on changed interfaces
- **Risk areas**: parts of the change most likely to cause regressions

Produce a finalized proposal at `.temp/proposal/<enhancement-slug>.md`.

## Interactive Improvement

- Present the impact analysis and proposal to the user
- If the impact is larger than expected, confirm scope adjustments
- Update `.temp/proposal/<enhancement-slug>.md` after each round of feedback
- Continue until accepted

## Implementation Plan

Create a plan that respects existing patterns:
- Order changes to minimize intermediate breakage
- Group related changes into reviewable units
- Define verification commands for each step
- Save to `.temp/<enhancement-slug>/02-plan.md`

## Execution Instructions

For each planned step:
1. **Modify code** following existing patterns and conventions in the codebase
2. **Update affected tests** — fix broken tests and add new coverage for changed behavior
3. **Verify** — run lint, type-check, and tests after each step

Do not introduce new patterns when the codebase already has an established approach.

Update progress in `.temp/<enhancement-slug>/03-progress.md`.

## Validation Criteria

Run the self-review loop (up to 10 iterations):
1. All tests pass (not just the ones changed)
2. Linter and type-checker report no errors
3. Build succeeds (if applicable)
4. Self-review against the proposal acceptance criteria
5. Check for over-engineering — remove unnecessary abstractions
6. Verify the specific behavior that changed matches expectations
7. Stop when all checks pass and no further simplification possible

Save to `.temp/<enhancement-slug>/04-summary.md`.

## Output Format

```markdown
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

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
- Build: <success/failure>

### Files Changed
- <file path>: <what changed>

### Risk Notes
- <any risks or things to watch for>
```
