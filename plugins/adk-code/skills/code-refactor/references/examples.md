# `code-refactor` — worked examples

## Example 1 — extract a validation helper

**Prompt:** `/adk-code:code-refactor "extract the cart validation logic from checkout.ts into its own module"`

**Phase 0:** Slug `extract-cart-validation`. Repo `~/code/acme/checkout-api`. Move: extract `validateCart` from `services/checkout/checkout.ts` into `services/cart/validate.ts`.

**Phase 1:** Clean tree. Branch `refactor/extract-cart-validation`. Baseline green (187 tests).

**Phase 2:** Read `checkout.ts` (450 lines). Identify the `validateCart` function (lines 47-92). Grep for `validateCart` — 3 call-sites: `checkout.ts:120`, `checkout.ts:200`, and `tests/checkout.test.ts:18`. Read existing tests for `validateCart` (4 tests in `checkout.test.ts`).

**Phase 3 plan:** `plan.md`:
```
## Move
Extract `validateCart` from `services/checkout/checkout.ts` into a new
module `services/cart/validate.ts`.

## Scope
- 1 source file edited (checkout.ts)
- 1 file created (services/cart/validate.ts)
- 1 test file edited (checkout.test.ts) — update import + add new
  test file (services/cart/validate.test.ts) co-located with new module

## Existing test coverage
4 tests in checkout.test.ts cover validateCart's behavior. Coverage is
adequate; no `code-test` prerequisite.

## Micro-steps
1. Create services/cart/validate.ts with `validateCart` (cut-paste from
   checkout.ts; old function still in checkout.ts as a re-export shim).
   Run suite. Green.
2. Update checkout.ts to import `validateCart` from the new module
   (delete the local definition, keep no shim). Run suite. Green.
3. Move the 4 existing tests from checkout.test.ts to
   services/cart/validate.test.ts. Run suite. Green.

## Validation plan
- `pnpm typecheck`
- `pnpm lint -- --max-warnings 0`
- `pnpm test -- services/checkout services/cart`

## Out of scope
- Renaming validateCart (no rename in this refactor).
- Adding more tests (validate.test.ts is moved 1:1, no new tests).
```

**Phase 4:** Apply step 1, run `pnpm test -- services/checkout` — green. Apply step 2, run — green. Apply step 3, run `pnpm test -- services/cart services/checkout` — green.

**Phase 5:** Full suite green (187 tests still). typecheck + lint green. No snapshot tests in this area.

**Phase 6:** `report.md` lists 3 files (1 created, 2 edited), 3 micro-steps, 187 tests still passing.

---

## Example 2 — rename a function across the codebase

**Prompt:** `/adk-code:code-refactor "rename getCwd to getCurrentWorkingDirectory everywhere"`

**Phase 0:** Slug `rename-getcwd-to-currentworkingdirectory`. Repo `~/code/acme/cli`. Move: mechanical rename.

**Phase 1:** Clean tree. Branch `refactor/rename-getcwd`. Baseline green (132 tests).

**Phase 2:** Grep `getCwd` — 23 call-sites across 14 files + the definition in `lib/fs.ts`. Read 3 representative call-sites for naming-style cues. Confirm: no public exports use `getCwd` (it's an internal helper only).

**Phase 3 plan:**
```
## Move
Rename internal function `getCwd` → `getCurrentWorkingDirectory` across
14 files (1 definition + 22 call-sites + 1 test import).

## Existing test coverage
3 tests reference getCwd; they will rename mechanically.

## Micro-steps
1. Update lib/fs.ts: rename the function definition. Add a temporary
   `export const getCwd = getCurrentWorkingDirectory` aliasing line to
   keep call-sites green. Run suite. Green.
2. Update 22 call-sites + 1 test import (all in src/ and test/). Use
   ts-morph or rg+sed; verify each replacement is exact. Run suite. Green.
3. Delete the temporary alias line in lib/fs.ts. Run suite. Green.

## Validation plan
- `pnpm typecheck` (catches any missed rename)
- `pnpm lint`
- `pnpm test`

## Out of scope
- The function's docstring is preserved (not updated for new name); see
  follow-ups.
```

**Phase 4:** Step 1 done — test green. Step 2 done — test green. Step 3 done — test green.

**Phase 5:** Full suite green. typecheck green (which is the most-valuable check for renames).

**Phase 6:** `report.md` lists 14 files changed, 23 occurrences renamed, 3 micro-steps, no behavior change.

---

## Example 3 — deduplicate three near-identical helpers

**Prompt:** `/adk-code:code-refactor "deduplicate the three near-identical date-parsing helpers in src/utils/"`

**Phase 0:** Slug `dedupe-date-parsers`. Repo `~/code/acme/dashboard`. Three helpers: `src/utils/parseDate.ts`, `src/utils/parseFlexible.ts`, `src/utils/parseInput.ts`. Read all three.

**Phase 1:** Clean. Branch `refactor/dedupe-date-parsers`. Baseline green.

**Phase 2:** Diff the three. They differ in:
- `parseDate` accepts ISO strings.
- `parseFlexible` accepts ISO + relative ("yesterday").
- `parseInput` accepts ISO + relative + epoch.

**Concern:** these are NOT actually duplicates — they have different input acceptance. If we collapse, the behavior changes. STOP. Re-read.

**Re-think:** Maybe they share a core (the ISO parsing) and differ only in pre-processing? Yes. Plan: extract the common ISO core; each existing helper becomes a thin wrapper around the core + its specific pre-processing.

**Phase 3 plan:**
```
## Move
Extract the common ISO-parsing core from the three near-identical
helpers into `src/utils/parseDateCore.ts`. The three existing helpers
become thin wrappers (kept for backwards compat).

## Scope
1 file created, 3 files edited (each loses ~10 lines), no public API change.

## Micro-steps
1. Create parseDateCore.ts with the ISO-parsing function. Run suite. Green.
2. Update parseDate.ts to delegate to parseDateCore. Run. Green.
3. Update parseFlexible.ts to use parseDateCore for the ISO branch.
   Run. Green.
4. Update parseInput.ts similarly. Run. Green.

## Out of scope
- Combining the three into one (would change input acceptance —
  behavior change).
```

**Phase 4-5:** All steps green. Full suite green.

**Phase 6:** `report.md` notes the move was NOT a 3-into-1 dedupe (which would have changed behavior); it's a "extract common core" move. Residual risk: "If a future change makes the three helpers truly equivalent, a 3-into-1 dedupe would be the natural next step — but that requires explicit input-acceptance unification, which is `code-write` not `code-refactor`."

---

## Example 4 — split an 800-line file by concern

**Prompt:** `/adk-code:code-refactor "split src/checkout/index.ts by concern — it's 850 lines"`

**Phase 0:** Slug `split-checkout-index`. Repo `~/code/acme/checkout-api`. Move: split.

**Phase 1:** Clean. Branch `refactor/split-checkout-index`. Baseline green (412 tests).

**Phase 2:** Read `index.ts`. Identify natural concern boundaries:
- Cart-validation logic (~200 lines).
- Pricing logic (~250 lines).
- Discount logic (~150 lines).
- Public API surface (the exported `checkout` function, ~50 lines, glues them together).
- Helpers (~200 lines).

Read external call-sites: 8 callers, all importing `checkout` (the public function). No callers import the internal helpers.

**Phase 3 plan:**
```
## Move
Split src/checkout/index.ts into:
- src/checkout/cart-validation.ts
- src/checkout/pricing.ts
- src/checkout/discount.ts
- src/checkout/helpers.ts
- src/checkout/index.ts (now ~80 lines: the public function + re-exports)

## Existing test coverage
412 tests in tests/checkout/. Adequate for the change.

## Micro-steps
1. Create cart-validation.ts (cut-paste). Update index.ts to import.
   Run suite. Green.
2. Same for pricing.ts. Run. Green.
3. Same for discount.ts. Run. Green.
4. Same for helpers.ts. Run. Green.
5. Verify index.ts now contains only the public function + re-exports.
   Run. Green.

## Out of scope
- Renaming any of the extracted symbols.
- Changing any function signature.
- Adding new abstractions.
```

**Phase 4:** Each step green. After step 3, one snapshot test that diffs the import order in `index.ts` flagged red. Investigated: re-export order changed slightly. **STOP per the rule.** Reconsidered: snapshot is on `index.ts`'s exports — the re-export ORDER changed (which is observable in TypeScript module graph). Decision: re-order the re-exports to match the original; re-run; green. (No snapshot update needed.)

**Phase 5:** Full suite green. typecheck + lint green. Snapshot tests untouched.

**Phase 6:** `report.md` lists 5 files changed (4 created, 1 reduced from 850 → 80 lines), 5 micro-steps, residual risk "the re-export order is sensitive — consider whether `code-api` should formalize the export contract".
