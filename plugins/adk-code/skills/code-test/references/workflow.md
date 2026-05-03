# `code-test` — workflow detail

## Phase 0 — prompt expand

1. **Restate**: "Add `<unit/integration/e2e>` tests for `<target>` in `<repo>`." One sentence.
2. **Resolve repo** via `cwd → .git → repos.md`.
3. **Identify the test framework + runner** from `package.json devDependencies`, `pyproject.toml [tool.pytest.ini_options]`, `build.gradle` `testImplementation`, etc. Record the exact run command.
4. **Identify file/location convention**: e.g. `*.test.ts` next to source / `tests/` folder / `src/test/kotlin/` / `__tests__/` / etc. Match it.
5. **Pick task slug**: `test-<target>` or `cover-<target>` (e.g. `test-order-state-machine`).
6. **Create** `.temp/task-<slug>/`. Write `prompt.txt`.
7. **Approval gate** unless `--auto`: confirm target + scope + framework.

## Phase 1 — preflight

1. `git status` clean. Dirty → ask.
2. Branch — protected → prompt `test/<slug>` (or `cover/<slug>`).
3. Resolve test command.
4. **Tests pass on HEAD** before adding new ones. If red, STOP — adding tests on top of a red baseline is unverifiable. (Optional: if the user explicitly is "trying to lock in current behavior including the failing one", revisit; but that's `code-bugfix` territory.)

## Phase 2 — read the target + existing tests

1. Read the target module end-to-end. Understand:
    - What does it do (the public surface)?
    - What are the inputs and outputs?
    - What state does it touch?
    - What are its dependencies (DB, HTTP, file system, time, randomness, etc.)?
2. Read every existing test file for the target. Cue:
    - File location and naming.
    - Framework dialect (`describe`/`it`, `test()`, `test.each`, etc.).
    - Mock policy (heavy mocks vs minimal mocks).
    - Assertion style (`expect(x).toBe(y)`, `assert.equal(x, y)`, etc.).
3. Read AGENTS.md / CLAUDE.md / CONTRIBUTING.md for testing rules. Examples of rules to honor:
    - "Tests must run in <2s each."
    - "Integration tests require Docker; mark with `@docker`."
    - "Snapshot tests are forbidden."
    - "All HTTP mocks via msw."

## Phase 3 — enumerate behaviors

For the target, list the behaviors. A behavior is a pair (input/state, expected output/effect). Examples:

- "When the cart is empty, checkout returns 400."
- "When the user is unauthenticated, the endpoint returns 401."
- "When the date string is malformed, parseDate throws ParseError."
- "When the discount code is expired, applyDiscount returns the original total."

Per behavior, design the trio:

- **Happy path** — the most common positive case (one).
- **Boundary** — the input value at the edge of acceptance (one — the most relevant).
- **Error** — the input value at the edge of rejection (one — the most relevant).

Save to `.temp/task-<slug>/behaviors.md` (shape in `references/output-format.md`).

**Approval gate** unless `--auto`. The operator may know behaviors the skill missed.

## Phase 4 — author tests (test-engineer subagent)

Spawn the `test-engineer` subagent with `behaviors.md` + the target file path.

The subagent's protocol:

1. For each behavior trio:
    a. Author the happy / boundary / error tests in the file location the conventions dictate.
    b. Run the tests. Iterate until green.
    c. **Verify fail-first**:
        - For tests on existing code: temporarily mutate the SUT (return wrong value, throw, no-op), run, observe red, restore, observe green. Document the transition.
        - For tests on new code: write the test BEFORE the implementation, observe red, then implement, observe green. (Rare for `code-test` — usually the production code already exists.)
2. Capture each red→green transition to `.temp/task-<slug>/validation/per-skill/code-test.md`.

## Phase 5 — validate

1. Run the new tests; confirm green.
2. Run the **full affected-package suite**; confirm no regressions.
3. Run typecheck + lint on the new test files.
4. (If `--coverage`) Run coverage:
    - `npm test -- --coverage` / `pytest --cov` / `cargo tarpaulin` / etc.
    - Capture lines + branches before / after.
    - Identify which lines / branches are now covered.
5. Capture all outputs to `validation/per-skill/code-test.md`.

## Phase 6 — report

Write `.temp/task-<slug>/report.md`:

- **Result** — "Added N tests covering M behaviors on `<target>`."
- **Tests added** — table: file, test name, behavior asserted, fail-first evidence.
- **Behaviors covered** — list per behavior.
- **Behaviors NOT covered** — bullet list with reason (out of scope, requires network harness, etc.).
- **Coverage delta** (if `--coverage`) — table: file, lines before → after, branches before → after.
- **Validation evidence** — final commands + exit codes.
- **Decisions** — every auto-pick.
- **Residual risk / follow-ups** — bullet list.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question.

## When the target has zero existing tests

Special case: the target module has no tests at all. The skill:

1. Surfaces this as a flag in Phase 0: "No existing tests on this target — coverage is starting from 0."
2. Prefers a small, targeted test set (the most-important 3-5 behaviors) over a sweep ("test every public method"). Sweeping is often wasteful.
3. Marks the report's residual risk: "Coverage on this module is now N%; high-priority untested behaviors: <list>."

## When the target has heavy mocking already

Some repos have a culture of heavy mocking; the new tests should match the existing style (respect autonomy) but the skill should surface the trade-off in residual risk:

- Heavy mocks → tests are fast but don't catch dependency drift.
- Light mocks → tests are slow but catch more.

The operator decides; the skill mirrors the existing style.

## Loop control

- After 3 attempts to make a test green without succeeding, STOP. The implementation may not actually do what we think it does (re-read the target).
- After 2 attempts where fail-first verification didn't show red, STOP. The mutation may not be exercising the test path; re-think the assertion or the mutation.
- Don't disable existing tests — surface that as a residual-risk callout.
