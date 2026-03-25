---
name: dev-tdd
description: Use when implementing features or bug fixes so behavior is specified by failing tests before code is written
---

# Test-Driven Development

## Core Rule

No production code before a failing test proves the behavior gap.

## Child-Agent Pattern

When the platform supports child agents, run in parallel:

- a test design pass
- an implementation pass after the test fails
- a review pass to confirm the test covers behavior rather than internals

## Use-Case-Driven Tests

Tests should be driven by real use cases, not just code coverage metrics.

### Identify Scenarios First

For each feature or function under development:

1. Identify the user scenarios and workflows it serves.
2. Express each scenario as a concrete test case that exercises the feature end-to-end, not just individual function calls.
3. Name tests after the scenario they verify, not the implementation detail they touch.

### Coverage Categories

Every scenario should cover:

- **Happy path** — the expected input produces the expected output.
- **Edge cases** — boundary values, empty inputs, maximum sizes, concurrent access.
- **Error conditions** — invalid input, missing dependencies, network failures, timeouts.
- **Integration boundaries** — behavior at the seams between modules, services, or APIs.

### Anti-Patterns to Avoid

- Testing implementation details (private methods, internal state) that can change without affecting behavior.
- Testing mocks instead of real behavior — mocks should simplify setup, not replace the system under test.
- Tests that pass when the feature is broken — a test that never fails is not a test.
- Asserting on incidental structure (JSON key order, log message format) rather than semantic correctness.
