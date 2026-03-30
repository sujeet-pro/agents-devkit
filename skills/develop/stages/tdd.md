# TDD Mode

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze requirements, scan test patterns, identify test framework; Research test patterns for chosen approach, define test plan |
| 2. Approach Selection | yes | Discuss test strategy, API design, edge cases to cover; Iterate on test plan and API design with user |
| 3. Planning | yes | Sequence of red-green-refactor cycles |
| 4. Execute | yes | Strict red-green-refactor cycle |
| 5. Validate & Learn | yes | Verify all tests meaningful, no over-engineering |

## Exploration Guidance

- Identify the test framework and patterns used in the codebase
- Read existing tests for style, naming conventions, and structure
- Understand the feature requirements and edge cases
- Identify integration points and dependencies

**End with 2-3 suggested testing approaches:**
- Unit-first vs. integration-first
- Mock strategy (real code vs. test doubles)
- API shape options

## Brainstorm

- Present testing approaches with trade-offs
- Discuss API design — what should the public interface look like?
- Identify edge cases and error conditions to cover
- User picks approach or mixes elements
- Save to `.temp/<feature-slug>/01-brainstorm.md`

## Deep Research and Proposal

Produce a test plan at `./temp/proposal/<feature-slug>.md`:
- List of test cases with descriptions
- Expected API shape
- Edge cases and error conditions
- Mocking strategy (minimize mocks, prefer real code)

## Interactive Improvement

- Present test plan for review
- Iterate on test cases, API design, and scope
- Update proposal in place until accepted

## Implementation Plan

Sequence the red-green-refactor cycles:
- Order tests from simplest to most complex
- Group related tests into cycles
- Identify refactoring opportunities between cycles

## Execution Instructions

### The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

### Red-Green-Refactor Cycle

#### RED — Write Failing Test

Write one minimal test showing what should happen:
- One behavior per test
- Clear name describing the behavior
- Real code, not mocks (unless unavoidable)

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };
  const result = await retryOperation(operation);
  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

#### Verify RED — Watch It Fail

**MANDATORY. Never skip.**

Confirm: test fails (not errors), failure message is expected, fails because feature missing (not typos).

#### GREEN — Minimal Code

Write the simplest code to pass the test. Don't add features, refactor, or "improve" beyond the test.

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try { return await fn(); }
    catch (e) { if (i === 2) throw e; }
  }
  throw new Error('unreachable');
}
```

#### Verify GREEN — Watch It Pass

Confirm: test passes, other tests still pass, output clean.

#### REFACTOR — Clean Up

After green only: remove duplication, improve names, extract helpers. Keep tests green. Don't add behavior.

### Repeat

Next failing test for next behavior.

### Good Tests

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One thing. "and" in name? Split it. | `test('validates email and domain')` |
| **Clear** | Name describes behavior | `test('test1')` |
| **Shows intent** | Demonstrates desired API | Obscures what code should do |

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc is not systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost. Keeping unverified code is debt. |
| "TDD will slow me down" | TDD faster than debugging. |

### Red Flags — STOP and Start Over

- Code before test
- Test passes immediately
- Can't explain why test failed
- "Just this once"
- "Keep as reference"

**All of these mean: Delete code. Start over with TDD.**

## Validation Criteria

Run the self-review loop (up to 10 iterations):

1. Every new function/method has a test
2. Watched each test fail before implementing
3. Each test failed for expected reason
4. Wrote minimal code to pass each test
5. All tests pass, linter clean, type-checker clean
6. Tests use real code (mocks only if unavoidable)
7. Edge cases and errors covered
8. No over-engineering — no unused abstractions

## Output Format

```markdown
## TDD Summary

Feature: <description>

### Test Cycles
| # | Test | Status | Notes |
|---|------|--------|-------|
| 1 | <test name> | Pass | <notes> |

### Coverage
- New tests: N
- Behaviors covered: N
- Edge cases: N

### Verification
- Tests: <pass/fail count>
- Lint: <clean/issues>
- Types: <clean/issues>
```
