# `audit-pr` — worked examples

## Example 1 — clean PR; all 10 Pass

**Prompt:** `/adk-review:audit-pr acme/storefront#103`

**Phase 0:** Slug `audit-storefront-pr-103`. Mode `--auto`. Local checkout from `repos.md`.

**Phase 1:** preflight green. Tools detected: `npm`, `tsc`, `eslint`, `axe-core`, `npm-license-checker`, `markdown-toc` (all present).

**Phase 2:** PR metadata fetched. Diff: +124/-22 across 5 files (3 .tsx + 2 .test.tsx). CI: green (lint, typecheck, tests all PASS upstream).

**Phase 3 — checks (parallel, 4 at a time):**

```
[adk-review:audit-pr] task=audit-storefront-pr-103 pr=acme/storefront#103 phase=3 mode=auto mcp=gh-cli checks=10-of-10 verdict=pass

| # | Check | Verdict | Notes |
| --- | --- | --- | --- |
| 1 | lint-clean | PASS | npm run lint: 0 errors, 0 warnings |
| 2 | typecheck-clean | PASS | tsc --noEmit: 0 errors |
| 3 | tests-added | PASS | tests-LOC=44, prod-LOC=80; ratio 0.55 |
| 4 | secrets-in-diff | PASS | no secrets detected |
| 5 | license-headers | PASS | 3 new .tsx files all have header |
| 6 | dep-licenses | PASS | no new deps |
| 7 | doc-updated | PASS | small change; CHANGELOG entry not required |
| 8 | a11y-regression | PASS | 0 violations on touched components (axe-core) |
| 9 | perf-regression | N/A | no hot-path files touched |
| 10 | bundle-size | PASS | within budget (delta +1.2KB; budget +5KB) |

Overall: PASS (9 checks Pass, 1 N/A).
```

**Phase 6 — surface:** "All 10 checks Pass (1 N/A: no hot-path touched). Ready to merge per audit; review-pr separately if depth needed."

---

## Example 2 — mixed: 2 Warns, 1 Fail

**Same PR but with rougher diff.**

```
| # | Check | Verdict | Notes |
| --- | --- | --- | --- |
| 1 | lint-clean | WARN | npm run lint: 0 errors, 3 warnings (no-unused-vars × 3) |
| 2 | typecheck-clean | PASS | 0 errors |
| 3 | tests-added | FAIL | tests-LOC=0, prod-LOC=120; no test for the new behavior |
| 4 | secrets-in-diff | PASS | no secrets |
| 5 | license-headers | PASS | all new files have header |
| 6 | dep-licenses | PASS | no new deps |
| 7 | doc-updated | WARN | 120 prod-LOC change but no CHANGELOG entry (recommend; not blocking) |
| 8 | a11y-regression | PASS | 0 violations |
| 9 | perf-regression | N/A | no hot-path |
| 10 | bundle-size | PASS | within budget |

Overall: FAIL (1 Fail, 2 Warns, 6 Pass, 1 N/A).
```

**Phase 6 — surface:** "1 Fail (tests-added: no test for 120 prod-LOC change). 2 Warns (lint warnings × 3, missing CHANGELOG entry). Suggest: add a test before merge; address lint warnings with `--fix`."

---

## Example 3 — `--auto --fix` for safely-fixable

**Same PR as Example 2, with `--fix`.**

**Phase 5b — fix:**
- lint-clean (WARN): run `npm run lint -- --fix`. Resolved 3 of 3 warnings (auto-fix removed unused vars). Re-run lint: 0 warnings (PASS).
- doc-updated (WARN): NOT auto-fixed (requires writing a CHANGELOG entry; that's `/adk-docs:docs-changelog`). Surface as "remaining; consider `/adk-docs:docs-changelog`".
- tests-added (FAIL): NOT auto-fixed (writing tests requires `/adk-code:code-test`). Surface as "remaining; consider `/adk-code:code-test`".

**PUSH-GATE:** "push 1 commit (lint auto-fix) to acme/storefront/feat-pricing? [y/N]". User: `y`.

**Pushed.**

**Phase 6 — surface:**

```
Result: 1 fix applied + pushed (lint auto-fix); 2 issues remain (1 Fail, 1 Warn).
- tests-added: FAIL — not auto-fixable. Suggest: /adk-code:code-test for the new behavior at <file:line>.
- doc-updated: WARN — not auto-fixable. Suggest: /adk-docs:docs-changelog.

Re-run audit-pr after addressing to confirm all checks Pass.
```

---

## Example 4 — secrets-in-diff Fail

**Phase 3:**
- secrets-in-diff: FAIL.

**Per-check evidence (`per-check/secrets-in-diff.md`):**

```markdown
# secrets-in-diff

## Verdict: FAIL

## Evidence
| File:line | Type | Detected by |
| --- | --- | --- |
| `config/dev.env:5` | AWS access key (AKIA...) | regex match |
| `config/dev.env:6` | AWS secret key | entropy heuristic |

## Mitigation (NOT auto-fixed; user action required)
1. Rotate the leaked credentials at the AWS console.
2. Remove from the diff: `git rm config/dev.env`.
3. Add to `.gitignore` (if not already).
4. If pushed: rewrite history (`git filter-repo` or BFG); force-push (NOT to protected branches; per github.md).
5. Notify security@acme.com.

## Notes
The actual secret values are NOT quoted here (per security policy).
```

**Phase 6:** "FAIL (secrets-in-diff). User action required — see per-check/secrets-in-diff.md for the mitigation steps. NOT auto-fixed."

---

## Example 5 — `-i` interactive walks each Warn/Fail

**Prompt:** `/adk-review:audit-pr acme/storefront#103 -i`

**Phase 4 — propose (interactive):**

```
3 non-Pass results to walk.

[1/3] WARN — lint-clean
  3 warnings (no-unused-vars × 3) at:
    - components/ProductCard.tsx:12 (unused 'useState')
    - components/ProductCard.tsx:22 (unused 'product')
    - utils/format.ts:5 (unused 'numeral')

  Options: [s]uggest fix (run --fix on lint only) | [d]owngrade to Pass for this run | [o]pen follow-up issue | [n]o action
  > s

  Will run npm run lint -- --fix on the 3 files in Phase 5b.

[2/3] FAIL — tests-added
  ...
```

User walks each.

---

## Example 6 — `--checks` subset

**Prompt:** `/adk-review:audit-pr acme/storefront#103 --checks lint,secrets`

Only 2 checks run (parallelized). Verdict is based on those 2 + everything else surfaced as "not requested".

```
| # | Check | Verdict | Notes |
| --- | --- | --- | --- |
| 1 | lint-clean | PASS | 0 errors, 0 warnings |
| 4 | secrets-in-diff | PASS | no secrets detected |

Overall: PASS (2 of 2 requested checks Pass; 8 not requested).
```

Useful for fast targeted audits (e.g. "did this PR introduce a secret?").

---

## Example 7 — N/A for missing tool

**Phase 1 detection:** `axe-core` not installed.

**Phase 3:**
- a11y-regression: N/A.

**Per-check evidence (`per-check/a11y-regression.md`):**

```markdown
# a11y-regression

## Verdict: N/A

## Reason
`axe-core` not installed. Required for a11y check on UI files.

## Install
```
npm install -D @axe-core/cli
```

## To re-enable
After install, re-run audit-pr.

## Notes
This check would have run because the diff touched UI files (.tsx). Verdict NOT counted in overall.
```

The overall verdict is `mixed` (one N/A); the user is informed about the install command.

---

## Example 8 — `--post-comment` posts the audit summary to the PR

**Prompt:** `/adk-review:audit-pr acme/storefront#103 --post-comment`

**Phase 5c:**

Posts a top-level comment:

```
**audit-pr summary** (from /adk-review:audit-pr)

| # | Check | Verdict |
| --- | --- | --- |
| 1 | lint-clean | PASS |
| 2 | typecheck-clean | PASS |
| 3 | tests-added | PASS |
| 4 | secrets-in-diff | PASS |
| 5 | license-headers | PASS |
| 6 | dep-licenses | PASS |
| 7 | doc-updated | PASS |
| 8 | a11y-regression | PASS |
| 9 | perf-regression | N/A (no hot-path) |
| 10 | bundle-size | PASS |

Overall: PASS (9 checks, 1 N/A).

— /adk-review:audit-pr
```

POST-CONFIRMATION: 5s → re-fetch → confirmed.
