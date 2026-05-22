---
title: 'guidelines/testing'
description: '1. **Test behavior, not implementation**. The test fails when behavior changes, not when refactoring touches a private method.'
source: 'shared/guidelines/testing.md'
group: 'shared-guidelines'
order: 6310
---
# shared/guidelines/testing

> Source: `shared/guidelines/testing.md`

# guideline: testing

> Loaded when the task involves adding, modifying, or reviewing tests.

## Hard rules

1. **Test behavior, not implementation**. The test fails when behavior changes, not when refactoring touches a private method.
2. **Each test is named for the behavior**: `it("rejects negative coupon amount")` not `it("amount > 0 check works")`.
3. **One assertion concept per test** — multiple `expect()` calls fine if they're testing the same property.
4. **Red → green → commit**. Write the test failing first; make it pass; commit.
5. **Cover happy path + ≥1 boundary + ≥1 error per behavior**.

## Test pyramid (most → least)

- **Unit**: fast, isolated, no I/O. ~70% of tests.
- **Integration**: real DB / cache / sibling service. ~20%.
- **End-to-end**: full stack, browser-driven. ~10%. Slow + flaky if overused.
- **Contract tests**: between services, based on OpenAPI / proto. Catches breaking changes early.

## What to mock

- **Mock**: external HTTP APIs, time, randomness, file system writes, message queues to other services.
- **Don't mock**: the system under test, the language runtime, the test framework, your own pure functions.
- **Real instead of mock**: in-memory DB > mocked DB; testcontainers > heavy mocks; fake clock library > full time mock.

## Anti-patterns

- Tests that pass when the code is deleted. Means you're testing the test framework.
- Tests with no assertion. The function returned; that's not behavior verification.
- Tests with sleep / wait-and-hope. Use proper synchronization or fake clocks.
- Test name = function name. Useless.
- One test per code branch. Test behavior, not the implementation tree.
- Snapshot tests for everything. Useful for narrow stable output (CLI output, error messages); harmful for HTML / complex objects (you'll regenerate without reading).

## Fixtures / setup

- Factory functions > raw fixture data. Easy to construct variants.
- Setup state explicitly per test. No "shared mutable state in module-level setUp".
- Use the language's standard test discovery; don't invent custom runners.

## Coverage

- Coverage % alone is meaningless. 100% with shallow assertions = useless.
- Care about branch coverage of business logic.
- Don't gate PRs on coverage % unless you also gate on test quality (review).

## Cite when reviewing

- The repo's test framework + runner config (`vitest.config.ts`, `pytest.ini`, etc.).
- The specific behavior the new test should cover.
- The existing test for similar behavior (consistency).
