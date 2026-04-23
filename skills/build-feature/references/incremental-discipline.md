# Incremental implementation discipline

Optional reference loaded by `build-feature` when the change is multi-file or otherwise non-trivial. Encodes the "thin vertical slices" discipline that makes large changes shippable in small reviewable steps.

## The core idea: vertical slices, not horizontal layers

Implement end-to-end in thin vertical slices, validated and committed one at a time. Avoid the temptation to "build the data layer first, then the service layer, then the API, then the UI" — by the time the last layer lands, the first one is stale and unproven.

```
Horizontal (BAD):                    Vertical (GOOD):
                                      
[       UI       ]                    ┌─UI─┬─UI─┬─UI─┐
[      API       ]                    ├─API├─API├─API┤
[    Service     ]                    ├Svc─┼Svc─┼Svc─┤
[      Data      ]                    └Data┴Data┴Data┘
                                       slice slice slice
                                       1     2     3
```

Each vertical slice produces user-visible (or at least integration-testable) behavior. Each slice is its own commit, its own PR if useful, and its own validation cycle.

## The 100-line rule

If you have written ~100 lines of new code without running validation, **stop**. Run something — the type checker, the relevant unit test, a smoke test. The rule is heuristic; the principle is: feedback loops should be tight.

Common violations:

- "I'll just finish this method, then run the tests" → that 5-line method becomes 200 lines.
- "I need to wire all 4 modules before anything works" → split the wiring into stub-and-replace slices.
- "Tests don't apply to scaffolding" → if it's worth scaffolding, it's worth a smoke test.

## Per-slice cycle

```
plan slice ── implement ── validate ── commit ── repeat
              ≤ ~100 LOC   tightest    descriptive
                           feedback    message
```

For each slice:

1. **State the slice's goal in one sentence.** "End-to-end signup with hard-coded plan."
2. **Implement the smallest correct change.** No extra layers. No "while I'm here".
3. **Validate.** Run the relevant test, lint on changed files, type-check on the touched module. Capture output.
4. **Commit (or stage).** Descriptive message. Conventional prefix (feat/fix/refactor/docs/test/chore).
5. **Note what's STILL OPEN.** Residual scope, follow-up items, things noticed-but-not-touched.

## Feature flags for in-progress work

Multi-slice features land behind a flag (default OFF in prod). This lets you ship slice-by-slice without exposing partial behavior. See `@adk:publish-ship` (a.k.a. `adk-publish-ship`)'s `references/feature-flag-lifecycle.md` for the lifecycle.

```ts
const isNewSignupEnabled = await flags.get('new_signup_v2', { default: false });
return isNewSignupEnabled ? <NewSignup /> : <LegacySignup />;
```

Rules:

- Flag default OFF in prod, ON in dev/test/staging (so the new path is exercised in CI).
- Flag check at the boundary, not inside hot loops.
- Flag-cleanup ticket filed at the same time as the flag is created.

## "Noticed but not touching"

When you read code adjacent to your change and notice unrelated issues, RESIST the urge to fix them in the same slice.

- Add them to the **residual scope** section of the report.
- Or open a follow-up issue / TODO with a tracked owner.
- Or commit them as a SEPARATE refactor in `@adk:build-refactor` (a.k.a. `adk-build-refactor`).

The cost of mixing scopes is paid at review time and at debug time, not at implementation time — that's why the agent feels like "it's free to fix this too".

## Commit hygiene per slice

- One logical change per commit.
- Commit message starts with conventional prefix (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Body explains **why**, not what.
- Avoid mixing format-only changes with behavior changes.
- Run pre-commit hooks (lint-staged, format) on every commit.

## Anti-patterns

- "I'll test it all at the end" — by then the implementation has drifted from intent.
- "It's faster to do all 4 layers at once" — measured per change, not per file.
- "These changes are too small to commit separately" — small commits are easier to review and revert.
- "I'll add the feature flag later" — later usually means the new path is already live.
- "This refactor is small enough to include" — that's how 100-line PRs become 1000-line PRs.
- "Validation each slice slows me down" — validation each slice catches bugs when context is fresh.

## When NOT to slice

- Truly atomic single-function changes (one config key, one field rename).
- Changes that have no observable behavior until they're whole (e.g. a parser switchover).
- Hotfix during an active incident — fix forward fast, then split for review later.
