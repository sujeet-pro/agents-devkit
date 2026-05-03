# `review-code-changes` — worked examples

## Example 1 — uncommitted only, just before commit

**Prompt:** `/adk-review:review-code-changes` (no args, no flags)

**Phase 0:**
- Repo: `acme/storefront`. Branch: `feature/pricing-rework`.
- Baseline: `git rev-parse @{upstream}` → `origin/feature/pricing-rework` (source: `tracking`).
- Slug: `feature-pricing-rework`.
- Mode: `--auto` (default).

**Phase 1:** preflight green. Cheap lint: `npm run lint --silent` → 2 warnings (unused import, missing semicolon).

**Phase 2 — gather scope:**
- Branch-vs-baseline: 0 commits ahead (no committed work yet).
- Staged: 0.
- Unstaged: 7 files (`src/pricing/calc.ts`, `src/pricing/calc.test.ts`, `src/api/pricing.ts`, ...).
- Untracked: 2 files (`src/pricing/utils.ts`, `src/pricing/types.ts`).

**Phase 3 — dimension passes:**
- correctness: 1 Should-Have (untracked `utils.ts` has no error handling on `parseFloat`).
- security: 0.
- performance: 1 Should-Have (loop over prices in `calc.ts` does `Math.pow(1 + tax, ...)` per iteration; tax is loop-invariant — hoist).
- tests: 1 Critical (untracked `types.ts` exports a discriminated union but `calc.test.ts` only tests one variant).
- docs: 0.
- style: 0 (lint pre-pass already caught the 2 nits; surfaced separately).

**Phase 4 — propose:** 3 findings sorted (Critical first).

**Phase 5a — report (no `--fix`):**

```
[adk-review:review-code-changes] task=feature-pricing-rework repo=acme/storefront baseline=origin/feature/pricing-rework(tracking) scope=branch:0 staged:0 unstaged:7 untracked:2 phase=5 mode=auto findings=B0/C1/S2/M0/N0/Q0

Result: 3 findings (1 Critical in untracked, 2 Should-Have in unstaged + untracked).
Top issue: missing test variant for the discriminated union in untracked/types.ts.
Lint: 2 warnings — see lint-output.txt.
Next: address findings before commit; then `git add -A && git commit && git push`.
```

---

## Example 2 — branch vs main, all committed, ready for push

**Prompt:** `/adk-review:review-code-changes main --auto`

**Phase 0:**
- Repo: `acme/checkout-api`. Branch: `hotfix/null-checkout`.
- Baseline: `main` (source: `arg`).
- Slug: `hotfix-null-checkout`.

**Phase 1:** preflight green. Lint pre-pass not run (no quick command in this Go repo — `golangci-lint run` would be too slow).

**Phase 2 — gather scope:**
- Branch-vs-baseline: 4 commits, 8 files changed (`+240/-45`).
- Staged: 0.
- Unstaged: 0.
- Untracked: 0.
- All clean — pure committed work.

**Phase 3 — dimension passes:**
- correctness: 0.
- security: 0.
- performance: 0.
- tests: 1 Should-Have (added a fix but no regression test for the null path).
- docs: 1 Nitpick (CHANGELOG.md not updated).
- style: 0.

**Phase 4 — propose:** 2 findings.

**Phase 5a — report:**

```
Result: 2 findings (1 Should-Have, 1 Nitpick).
Top issue: missing regression test for the null path in services/checkout.go:88.
Next: optional — address the Should-Have before push, or open follow-up; nothing blocking.
```

---

## Example 3 — `--auto --fix` flow, applies + validates, stops before push

**Prompt:** `/adk-review:review-code-changes --auto --fix`

**Phase 0–4:** same as Example 1 → 3 findings (1 Critical, 2 Should-Have).

**Phase 5b — fix:**
- Build queue: 3 fixes, severity-prioritized.
- Fix 1 (Critical: missing test variant): non-trivial → delegate to `/adk-code:code-bugfix`. Returns: added 4 test cases at `src/pricing/calc.test.ts:42-78`. Validation: `npm test src/pricing/` → 14/14 PASS.
- Fix 2 (Should-Have: hoist loop-invariant): trivial → inline edit at `src/pricing/calc.ts:55`. Validation: `npm test src/pricing/` → 14/14 PASS.
- Fix 3 (Should-Have: error handling on parseFloat): trivial → inline edit at `src/pricing/utils.ts:12`. Validation: `npm test src/pricing/` → 14/14 PASS.
- Final validation: `npm run lint` → 0 warnings (the 2 lint warnings from Phase 1 also cleaned up incidentally). `npm run typecheck` → 0 errors.

**Phase 6 — report:**

```
Result: 3 findings addressed (1 Critical + 2 Should-Have); all validation green; 7 files dirty.
Next: `git diff` to eyeball, then `git add -A && git commit -m "..." && git push`.
fix-log.md has per-finding evidence.
```

The skill stops here — does NOT push.

---

## Example 4 — `-i` interactive, walks each finding

**Prompt:** `/adk-review:review-code-changes -i`

**Phase 0:** same as Example 1.

**Phase 4 — propose (interactive):**

```
3 findings to walk. Showing 1 of 3.

### [Critical] Missing test variant for discriminated union
- File: src/pricing/types.ts:14-22 (untracked)
- Dimension: tests
- Confidence: high
- Evidence:
  ```
  type Pricing = StandardPricing | TieredPricing | DynamicPricing
  ```
- Issue: types.ts exports a 3-variant union; calc.test.ts only tests StandardPricing.
- Fix: add tests covering TieredPricing + DynamicPricing branches.
- Impact if unfixed: untested branches likely to break in production on certain product types.

[a]ccept | [e]dit | [d]iscard
> a
```

User accepts all 3.

**Phase 5b** (because `--fix` not passed, just `-i`): goes to Phase 5a (report-only).

---

## Example 5 — fallback baseline (first-parent)

**Prompt:** `/adk-review:review-code-changes` on a branch with no upstream and no `origin/<branch>` and the repo doesn't have `main` or `master` (e.g. uses `default`).

**Phase 0:**
- `git rev-parse @{upstream}` → fails.
- `git rev-parse origin/<branch>` → fails.
- `git rev-parse main` → fails.
- `git rev-parse master` → fails.
- Fallback: `git rev-list --first-parent --max-count=1 HEAD~1` → `<sha>`.
- Surface in banner: `baseline=<short-sha>(first-parent)`.
- Surface to user: "no upstream / origin / main / master found — using HEAD~1 as baseline. Pass an explicit `<base-branch>` to override."

The skill continues normally with the first-parent baseline.

---

## Example 6 — working tree changed mid-review (detected)

**Phase 2:** captured 7 unstaged files at t=0.

**Phase 3:** halfway through dimension passes, the user edits `src/pricing/calc.ts` in their editor.

**Phase 5a:** the skill detects via mtime check (every in-scope file's mtime stored at end of Phase 2; compared at end of Phase 3). One file changed.

**Surface:**

```
Working tree changed during review (1 file: src/pricing/calc.ts). Findings against this file may be stale.

Recommend: re-run after you finish editing.

Showing the report against the snapshot at t=0 anyway:
...
```

The user can ignore (the report has a clear stale marker on the affected finding) or re-run.
