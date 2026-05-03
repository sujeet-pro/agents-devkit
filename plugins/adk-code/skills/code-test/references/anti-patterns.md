# `code-test` — anti-patterns

## Vacuous coverage

- **`expect(result).toBeTruthy()`** on a hardcoded `{ ok: true }` — passes regardless of whether the code is right.
- **`expect(result).toBeDefined()`** when `result` is the return of a function that always returns something. The assertion can't fail.
- **`it("works", () => { someFunction(); })`** — no assertion. The test passes if `someFunction` doesn't throw. That's not an assertion.
- **Tests that exercise the line so coverage goes up** but assert nothing useful. Coverage is the side-effect; assertions are the goal.

## Function-named tests

- **`it("calculateCheckout()")`** — tells you nothing about what fails when red.
- **`it("checks the cart")`** — vague; what about the cart?
- **`it("works for empty input")`** — works how? returns what?
- **Good shape**: `it("returns 400 when the cart is empty at checkout")` — tells you what the failing assertion was about.

See `references/test-naming-conventions.md` for the full naming guide.

## Tests that pass without the implementation

- **Skipping the fail-first step.** If you don't observe red before the test is green, you might be testing the test (or testing nothing).
- **Test passes because the assertion is loose.** `expect(result.length).toBeGreaterThan(0)` when the right assertion is `expect(result).toEqual([1, 2, 3])`.
- **Test passes because the mock returns the expected value.** The mock IS the test now; the SUT is irrelevant.

## Mocking the system under test

- **Mocking the function the test is supposed to test.** You're now testing the mock, not the system.
- **Sealing every dependency** with a mock so the test exercises nothing real. Use real implementations where they're cheap (no network, no DB); mock at the IO boundary only.
- **Mocking time without controlling it.** `Date.now()` mocked to a fixed value across the suite — but the SUT might be reading other time sources (process.hrtime, performance.now). Use a clock abstraction.
- **Mocking the framework.** "I'll mock React's useState." That's testing your mock, not your component. Use the framework as-is; mock the data + API boundaries.

## Testing private internals

- **`expect(component.state.internalCounter).toBe(3)`** — the state is private; the assertion couples the test to the implementation.
- **Calling private methods directly** (`(component as any)._privateHelper()`) — same.
- **Asserting on private mock-call counts** (`expect(spy).toHaveBeenCalledTimes(3)`) when the public assertion would be `expect(result).toEqual([…])`.
- The right level: assert on the public API. If the only way to verify the behavior is to look at internals, the public API is missing an observable.

## One giant test

- **17 assertions in one test** — when one fails, you don't know which behavior is broken.
- **Long arrange / act / assert blocks with multiple unrelated acts** — split into multiple tests.
- **A "smoke test" that just runs through the happy path with 8 assertions** — useful, but should be 8 small tests for diagnostic purposes.

## Snapshot abuse

- **Snapshot of a 5-page object.** Nobody reads it; nobody updates it honestly.
- **Snapshot tests as a substitute for targeted assertions.** Targeted assertions tell you what's expected; snapshots tell you "it changed".
- **Inline snapshots used to "lock in" the current output without thinking about whether it's right** — easy to write; easy to drift; easy to update without thinking.
- The good use of snapshots: small, intentional outputs (e.g. a generated file, a CLI usage string) where you want to see the diff in PR reviews.

## Dependency-injection theatre

- **Refactoring the SUT to be testable** by adding 4 layers of dependency injection that are unused outside tests. The test is now a refactor + test combo; the production code is harder to read.
- **Adding a `__mocks__/` folder to fake an entire module** when one mock at the call-site would do.

## Coverage as goal

- **"100% coverage" with vacuous assertions.** Coverage measures what was executed; not what was verified.
- **Treating untested branches as a problem to solve in this task** when some branches are intentionally untested (e.g. defensive code for impossible cases — should be removed, not tested).
- **Branch coverage on `||` short-circuits** — covering both branches of `a || b` may require artificial tests.

## Test independence violations

- **Tests that share state** — test 1 sets a global; test 2 reads it; test 1 must run first.
- **Tests that depend on order** — `beforeAll` does heavy setup; tests assume it ran.
- **Tests that mutate the file system** without cleanup — leaves cruft for the next test run.
- **Tests with `setTimeout`-based waits** — flaky.

## Flaky tests

- **A test that passes 95% of the time.** Either fix the source of non-determinism (use a deterministic clock, deterministic random, deterministic ordering) or don't add the test.
- **A test that fails on CI but passes locally** — there's an env or timing difference. Investigate before merging.
- **A test that fails when run in parallel** — shared state somewhere. Investigate.

## Disabling other tests

- **`it.skip("…")`** added to make the new test pass. Surface it; don't hide.
- **Removing an assertion that's now wrong because of a change** — that's a behavior change in disguise; re-categorize as `code-write` or `code-bugfix`.

## Reporting

- **"Added 14 tests"** — without listing the behaviors. The behavior list is the artifact.
- **"Coverage went up"** — by how much, on what file?
- **Hiding behaviors NOT covered.** List them with reason.
- **Snapshot tests in the count without disclosure.** Differentiate snapshot tests from targeted-assertion tests in the report — they have different value.
