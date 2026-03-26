---
name: dev-tdd
description: Use when implementing features or bug fixes so behavior is specified by failing tests before code is written
user_invocable: true
arguments:
  - name: feature
    description: "Feature or bug fix to implement with TDD"
    required: true
  - name: scope
    description: "Scope: unit, integration, e2e (default: unit)"
    required: false
---

# Test-Driven Development

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

## Core Rule

No production code before a failing test proves the behavior gap.

## Preflight

Before starting the TDD cycle, run:

`zsh scripts/check-skill-deps.zsh dev-tdd`

Verify that the project's test runner is available and working. Confirm the test suite passes in its current state before writing new tests.

## Required Child Agents

Run at least these child agents in parallel:

- **Test designer**: analyzes the feature requirements and identifies test scenarios. Produces a test plan covering happy path, edge cases, error conditions, and integration boundaries. Names tests after the scenario they verify, not the implementation detail.
- **Implementation agent**: after the test fails, writes the minimum production code to make it pass. Follows the principle of doing the simplest thing that works.
- **Review agent**: confirms the test covers behavior rather than internals, the implementation is minimal and clean, and no existing tests were broken. Flags tests that would pass even if the feature were broken.

## Workflow

1. **Identify scenarios.** Analyze the feature and list the user scenarios and workflows it serves.
2. **Write failing test.** Express the first scenario as a concrete test case. Run it and confirm it fails for the right reason.
3. **Implement.** Write the minimum code to make the test pass. Do not add behavior beyond what the test requires.
4. **Verify.** Run the test and confirm it passes. Run the full test suite to check for regressions.
5. **Refactor.** Clean up the implementation while keeping all tests green. Improve naming, extract helpers, remove duplication.
6. **Repeat.** Return to step 2 for the next scenario until all scenarios are covered.
7. **Final verification.** Run lint, type-check, and full test suite.

## Coverage Categories

Every scenario should cover:

- **Happy path**: expected input produces expected output
- **Edge cases**: boundary values, empty inputs, maximum sizes, concurrent access
- **Error conditions**: invalid input, missing dependencies, network failures, timeouts
- **Integration boundaries**: behavior at the seams between modules, services, or APIs

## Anti-Patterns to Avoid

| Pattern | Why It Fails |
|---------|-------------|
| Testing implementation details (private methods, internal state) | Can change without affecting behavior |
| Testing mocks instead of real behavior | Mocks should simplify setup, not replace the system under test |
| Tests that pass when the feature is broken | A test that never fails is not a test |
| Asserting on incidental structure (JSON key order, log format) | Breaks on irrelevant changes |
| Writing production code before the test fails | Defeats the purpose of TDD |

## Output

Present a completion summary:

```
## TDD Summary

Feature: <feature description>
Scenarios covered: N
Tests written: N
Tests passing: N

### Scenarios
- [x] Scenario 1: <description>
- [x] Scenario 2: <description>
...

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
```

## Adjacent Skills

- `/devkit:dev-implement` for the full implementation flow with TDD as an option
- `/devkit:dev-verify` for standalone verification
- `/devkit:dev-debug` for investigating test failures
