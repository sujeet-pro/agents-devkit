# `code-test` — clarifying questions

Asked one at a time, only when the answer changes the plan. Under `--auto`, defaults apply silently.

## Phase 0 — prompt expand

1. **Target: `<resolved>` (e.g. `services/checkout/discount.ts`). Correct?**
   - _Default under `--auto`:_ proceed.

2. **Test type: `<unit|integration|e2e>`. Correct?**
   - _Default under `--auto`:_ pick based on target's nature (see decision tree). Record in Decisions.

3. **Framework + runner: `<vitest run|jest --ci|pytest|...>`. Correct?**
   - _Default under `--auto`:_ proceed with the resolved command.

4. **Test file location: `<path>`. Correct?**
   - _Default under `--auto`:_ use the repo's existing convention (read 1-2 existing test files; mirror).

## Phase 1 — preflight

5. **Working tree dirty. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if unrelated; STOP if overlapping.

6. **On `<branch>`. Create `test/<slug>` or stay?**
   - _Default under `--auto`:_ create `test/<slug>` if protected.

7. **Tests RED on HEAD. Adding tests on a red baseline is unverifiable. STOP — fix baseline?**
   - _Default under `--auto`:_ STOP. Always.

## Phase 3 — enumerate behaviors

8. **Behavior list: `<list>`. Add, remove, reorder?**
   - _Default under `--auto`:_ proceed with the inferred list. The operator can suggest more in residual risk later.

9. **For behavior `B<N>`, the trio is: happy=`<x>`, boundary=`<y>`, error=`<z>`. Correct?**
   - _Default under `--auto`:_ proceed; record in Decisions if non-obvious.

10. **The target has zero existing tests. This is a from-scratch coverage backfill. Continue?**
    - _Default under `--auto`:_ proceed; flag in residual risk: "starting from 0% coverage; covering the most-important behaviors first; full sweep deferred to follow-up if needed".

11. **The repo's testing rules forbid `<X>` (e.g. snapshot tests, network in unit tests). Confirm constraint applies?**
    - _Default under `--auto`:_ honor the rule from AGENTS.md / CLAUDE.md.

## Phase 4 — author

12. **Test-engineer wants to mock `<dep>`. Confirm?**
    - _Default under `--auto`:_ allow if the dep is at IO boundary (DB, HTTP, file system, time, randomness, external SDK). Refuse if the dep IS the SUT.

13. **Fail-first didn't show red on `<test>`. The mutation may not exercise the test path. Try a different mutation, or accept (rare)?**
    - _Default under `--auto`:_ try a different mutation up to 2 times; STOP and surface if still no red.

14. **The new test relies on a harness the repo doesn't have (e.g. e2e on a repo with no Playwright config). Skip this test or set up the harness?**
    - _Default under `--auto`:_ skip + flag in residual risk: "harness setup is out of scope for `code-test`; spawn `code-write` if needed".

## Phase 5 — validate

15. **Coverage tool not configured. Skip the delta or fall back to manual line-counting?**
    - _Default under `--auto`:_ skip + flag in residual risk: "no coverage tool; can't measure delta".

16. **Test count is now `<N>`, was `<M>` at baseline. Differs by `<diff>`. Expected (we added tests)?**
    - _Default under `--auto`:_ if `diff = number of new tests added`, OK. If different, investigate.

17. **A snapshot test changed. STOP — was the change intentional?**
    - _Default under `--auto`:_ STOP. Snapshot drift on a test-only change is suspect; surface.

## Phase 6 — report

18. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip; offer-depth.

## Anti-rules

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #7 baseline-red, #13 fail-first-no-red-after-2-tries, #17 snapshot-changed — those gate even under `--auto`).
- Surface defaults before asking.
