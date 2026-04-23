# TDD discipline — Red-Green-Refactor and the test pyramid

Optional reference loaded by `build-test` (and recommended for `build-feature` / `build-bugfix`) when the work warrants test-first discipline. Encodes the principles from the Google testing canon ("Software Engineering at Google") and the Beck / Beedle / Jeffries Red-Green-Refactor rhythm.

## Red-Green-Refactor cycle

```
RED ── Green ── Refactor ── (loop)
 │       │          │
 │       │          └── improve structure with tests still green
 │       └────────────── make the test pass with the simplest code that works
 └────────────────────── write a test that fails (and fails for the RIGHT reason)
```

Rules:

- The RED test must fail with a meaningful message before any production code is written. A test that errors out (compile error, missing import) is NOT a valid RED — fix the test first.
- The GREEN step writes the smallest amount of production code that makes the test pass. Resist the urge to write the "real" implementation early.
- The REFACTOR step changes the structure of code or test, with tests staying green throughout. No new behavior in this step.
- Repeat. One failing test at a time.

## Beyonce Rule

> *"If you liked it then you should have put a test on it."*

If a behavior is worth depending on, it's worth putting a test on. Conversely: any behavior NOT covered by a test is something the next change can break without anyone noticing — including the AI agent.

## Test pyramid (default mix)

```
       ┌────────┐
       │ ~5% E2E │   Slow, brittle, real browser / real network
       ├────────┤
       │ ~15%   │   Integration — collaborating modules + real adapters
       │  Int.  │
       ├────────┤
       │  ~80%  │   Unit — pure functions, isolated modules
       │  Unit  │
       └────────┘
```

The exact ratio varies by stack, but the SHAPE is fixed: many fast unit tests, fewer integration tests, very few E2E tests. An inverted pyramid (many E2E) is a smell — the suite will be slow, flaky, and expensive to maintain.

## Test sizing (Google's small / medium / large)

| Size | Resources | Wall time | Examples |
| --- | --- | --- | --- |
| **Small** | Single process, no I/O, no sleep, no clock | < 1 second | Pure function tests, classic unit tests |
| **Medium** | Single machine, may use localhost network, may use real disk, must be hermetic | < 1 minute | DB-backed integration tests, in-process HTTP tests |
| **Large** | May span machines, real services, longer sleeps | minutes | True E2E, browser tests, environment validation |

Small tests are the workhorse. Medium tests cover real adapter behavior. Large tests validate the full system but are not the place to test logic.

## DAMP over DRY in tests

> Test code should be **DAMP** — Descriptive And Meaningful Phrases — even at the cost of some duplication.

- A reader of one test should understand it without scrolling around.
- Don't extract helpers that hide what's being tested. A 5-line setup that reads top-to-bottom beats a 1-line `setupCommonFixture()` that hides 30 lines elsewhere.
- Shared fixtures are fine for *data*; shared assertions are usually a smell.

## State, not interactions

Assert on observable outcomes, not on which methods were called.

- ✅ "After saving a user, querying that user returns the saved values."
- ❌ "After saving a user, `repository.save()` was called once with these arguments."

Interaction tests freeze the implementation; state tests freeze the contract.

## Real impl > fake > stub > mock

Preference order for test doubles:

1. **Real implementation** (e.g. real in-memory DB, real Zod schema). Highest fidelity.
2. **Fake** — a working alternative implementation (e.g. in-memory file system).
3. **Stub** — returns canned data. Use when the real thing has too much surface area.
4. **Mock** — verifies interactions. Use sparingly, mostly at architectural boundaries.

Heavy mocking in unit tests usually means the seams are wrong; revisit the design.

## Arrange-Act-Assert (AAA)

Every test, in order:

1. **Arrange** — set up inputs, doubles, environment.
2. **Act** — invoke the system under test.
3. **Assert** — check outcomes.

Visually separated. One reason to fail per test.

## Anti-patterns

- A test that passes when the code is deleted (no real assertion).
- Mocking the system under test (you're testing the mock).
- Sleeping for time. Use fake timers.
- Snapshot tests for behavior — snapshots are for shape, not correctness.
- "Coverage farming" tests that touch lines without verifying behavior.
- Disabling a failing test because it's "flaky" without diagnosis. The flake is the bug.
- Testing private internals. They will churn; lock down the public contract instead.
