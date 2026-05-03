# `audit-repo` — worked examples

## Example 1 — full audit, all 6 dimensions

**Prompt:** `/adk-review:audit-repo .`

**Phase 0:** repo path = CWD = `~/code/acme/checkout-api`. Slug `audit-checkout-api-2026-05-03`. Mode `--auto`. All 6 dimensions.

**Phase 1:** preflight green. Tools detected: `npm`, `npm audit`, `eslint`, `tsc`, `vitest`, `madge`. Missing: `gosec` (skipped — Go isn't the primary language; covered by eslint for the bits of Go in /scripts/).

**Phase 2 — inventory** (~90s):
- Languages: TS 78%, Python 12%, Markdown 6%, Go 2%, Other 2%.
- Framework: Next.js 15 + FastAPI 0.110.
- Dep mgr: pnpm + uv. Test: vitest + pytest + coverage.py.
- Lint: eslint + ruff. Type: tsc + mypy. CI: GitHub Actions.
- Top-20 largest: `src/billing/calculator.ts` (1820 LOC) + 19 others.
- Top-20 most-changed: `src/api/checkout.ts` (47 commits last 6mo) + 19 others.

**Phase 3 — dimension passes** (~6 min total, parallelized):

- **security:** `npm audit` clean (0 vulns). `pip-audit` 1 medium (urllib3 CVE-2024-XXXX; fixable by upgrade). `security-reviewer` agent: 1 Blocker (admin endpoint without role check at `routes/admin.go:42`), 2 Should-Have (CSRF token missing on 1 internal POST; weak hash algo SHA-1 used in legacy session derivation).
- **performance:** 1 Critical (n+1 query in `db/orders.go:117` on the dashboard hot path; documented SLO at `~/.config/adk/datadog.md.slo_thresholds.checkout_p99_ms: 500`). 2 Should-Have (per-request regex compilation in `services/billing.ts:88`; missing index implied by new query in `migrations/20260415_add_active_at.sql`).
- **quality:** eslint: 47 warnings, 0 errors (mostly `no-unused-vars` in test files). 1 god-class flagged (`src/billing/calculator.ts` — 1820 LOC, 31 methods, single-responsibility violation). Cyclomatic complexity: 3 functions over 25 (`processOrder` cc=42; `validateInvoice` cc=31; `applyDiscount` cc=27).
- **deps:** 12 outdated (8 patch, 3 minor, 1 major: react@18 → @19). 0 disallowed licenses. 4 transitively-orphaned (no top-level dep depends on them).
- **test-coverage:** vitest --coverage = 76% lines, 68% branches. Coverage gaps in `src/api/admin/` (0% line coverage on 4 routes), `services/legacy-pricing.ts` (12% line coverage). pytest --cov = 81% on Python side; healthy.
- **architecture:** `madge` reports 3 cyclic deps in `src/services/`. CODEOWNERS: 1 file under no team's ownership (`src/legacy/`). Boundary violation: 4 files in `src/api/` import from `src/internal/db/` directly (bypassing the service layer).

**Phase 4 — aggregate:**

Top-10 (severity-sorted, then by impact-area breadth):

```
1. [Blocker] Admin endpoint missing role check (security)
2. [Critical] N+1 query on dashboard hot path (performance)
3. [Critical] God-class in src/billing/calculator.ts (quality / architecture)
4. [Should-Have] 4 admin routes with 0% test coverage (test-coverage)
5. [Should-Have] React 18 → 19 major upgrade overdue (deps)
6. [Should-Have] CSRF token missing on internal POST (security)
7. [Should-Have] Per-request regex compilation in billing service (performance)
8. [Should-Have] 3 cyclic deps in src/services/ (architecture)
9. [Should-Have] Boundary violation: 4 src/api/ files bypass service layer (architecture)
10. [Should-Have] urllib3 CVE-2024-XXXX (deps)
```

What's healthy (top 5):
- 0 secrets in repo.
- npm audit clean (0 vulns on Node side).
- CI is green and fast (3.5min for the full pipeline).
- Coverage is healthy on Python side (81%).
- 0 disallowed licenses across all deps.

**Phase 6 — write:** `.temp/reports/audit-checkout-api-2026-05-03.md` (842 lines).

**Phase 7 — surface:**

```
[adk-review:audit-repo] task=audit-checkout-api-2026-05-03 repo=acme/checkout-api phase=7 mode=auto dimensions=security,performance,quality,deps,test-coverage,architecture findings=B1/C2/S7/M3/N5/Q4 healthy=5

Result: audit complete. 1 Blocker + 2 Critical + 7 Should-Have + 3 May-Have + 5 Nitpick + 4 Question. 5 healthy items.

Top-3:
  1. [Blocker] routes/admin.go:42 — missing role check on admin endpoint.
  2. [Critical] db/orders.go:117 — n+1 query on dashboard hot path.
  3. [Critical] src/billing/calculator.ts — god-class (1820 LOC, 31 methods).

Suggested next:
  - Address #1: /adk-code:code-security --scope routes/admin/
  - Address #2: /adk-code:code-perf --scope db/
  - Address #3: /adk-code:code-refactor --scope src/billing/

Full report: .temp/reports/audit-checkout-api-2026-05-03.md
Per-dimension evidence: .temp/reports/audit-checkout-api-2026-05-03-evidence/
```

---

## Example 2 — scoped audit (`--scope src/auth/`)

**Prompt:** `/adk-review:audit-repo . --scope src/auth/`

**Phase 2:** inventory limited to `src/auth/` (12 files, 2400 LOC).

**Phase 3:** dimension passes only on the scoped files. Security and quality are the dominant dimensions; performance / deps / test-coverage less relevant for a focused subsystem.

**Phase 6:** report sized to scope (~250 lines instead of 800).

```
Result: audit (scoped to src/auth/) complete. 0 Blocker + 1 Critical + 4 Should-Have + 2 May-Have + 1 Nitpick. 3 healthy items.

Top-3:
  1. [Critical] auth/middleware.ts:88 — JWT verification skips audience check.
  2. [Should-Have] auth/session.ts:42 — session cookie not Secure / HttpOnly / SameSite=Strict.
  3. [Should-Have] auth/admin.ts:120 — role check uses == (loose) instead of strict role-set membership.
```

---

## Example 3 — dimension subset (`--dimensions security,deps`)

**Prompt:** `/adk-review:audit-repo . --dimensions security,deps`

**Phase 3:** only the 2 dimensions run. Faster (~2 min instead of 6 min).

**Phase 6:** report focused on 2 dimensions; "Per-dimension detail" has 2 sections.

```
Result: audit (security + deps only) complete. Found 1 Blocker + 1 Critical + 4 Should-Have. 3 healthy items.

The 4 OTHER dimensions (performance, quality, test-coverage, architecture) were not run. Re-run without --dimensions to get the full picture.
```

---

## Example 4 — interactive (`-i`) walks Top-10

**Prompt:** `/adk-review:audit-repo . -i`

**Phase 5 — propose (interactive):**

```
Top-10 findings ready to walk.

[1/10] [Blocker] Admin endpoint missing role check
- File: routes/admin.go:42
- Dimension: security
- Confidence: high
- Evidence:
  ```
  router.POST("/admin/users/delete", adminHandler.DeleteUser)
  ```
- Issue: the new route is registered in the admin group but the handler doesn't call RequireRole("admin").
- Recommended action: /adk-code:code-security --scope routes/admin/

[a]ccept | [r]e-tier | [d]iscard | [m]erge with another
> a

[2/10] [Critical] N+1 query on dashboard hot path
- ...
> a

[3/10] [Critical] God-class in src/billing/calculator.ts
- File: src/billing/calculator.ts (whole file)
- Dimension: quality / architecture
- Confidence: med
- Issue: 1820 LOC, 31 methods. Probable single-responsibility violation.
- Recommended action: /adk-code:code-refactor --scope src/billing/

[a]ccept | [r]e-tier | [d]iscard | [m]erge with another
> r

Re-tier to: Should-Have
Reason: "the file works correctly; refactor is desirable but not urgent"

OK, re-tiered to Should-Have.

[4/10] ...
```

User walks each. Final aggregation reflects user decisions.

---

## Example 5 — M&A pre-acquisition audit

**Prompt:** `/adk-review:audit-repo ~/code/acme/target-startup --auto --dimensions security,deps,docs,architecture`

**Phase 0:** path resolves; slug `audit-target-startup-2026-05-03`.

**Phase 3:** subset of 4 dimensions (the M&A-relevant ones). Skipping perf + test-coverage + quality (those matter, but M&A focuses on legal / inheritance / scale concerns).

**Phase 6:** report tailored to M&A audience:

- Section 1 (Executive summary) leads with a verdict suitable for the acquiring team's CTO: "this codebase is healthy on security but has 3 medium-effort risks (1 GPL dep that affects open-source-ability, 1 pre-2020 monolith pattern in `src/billing/`, 1 missing CI signing for releases)".
- Section 5 (Recommendations) frames work as "before integration" / "first 90 days" / "first year".

---

## Example 6 — small repo, fewer findings; surfaces "in good shape"

**Prompt:** `/adk-review:audit-repo .` on a small (5K LOC), well-maintained library.

**Phase 4 — aggregate:** 0 Blocker + 0 Critical + 2 Should-Have + 1 May-Have + 4 Nitpick. Total: 7 findings.

**Phase 6:**

```
Result: audit complete. 7 findings (no Blockers, no Criticals). 6 healthy items.

The Top-7:
  1. [Should-Have] dep `lodash` is a polyfill candidate (bundle size delta ~12KB)
  2. [Should-Have] CHANGELOG.md hasn't been updated since v1.4.0 (now on v1.5.2)
  3. [May-Have] coverage on src/utils/ is 65% (rest of repo is >85%)
  4-7. [Nitpick] minor style consistency items

What's healthy:
  - 0 security findings.
  - 0 outdated major-version deps.
  - Coverage 87% across the repo.
  - CI green; pipeline 1.2 min.
  - 0 disallowed licenses.
  - Architecture: no cyclic deps.

The repo is in good shape. No urgent action.
```

The skill DOESN'T pad to 10 — surfaces the actual count, surfaces "in good shape".

---

## Example 7 — time-budget protects against runaway audits

**Prompt:** `/adk-review:audit-repo ~/code/acme/giant-monorepo --auto --time-budget 10`

**Phase 3:** dimension passes start. Inventory takes 4 minutes (large repo). Dimension passes started at 4:05 should finish by 9:55, but the deps pass is hung on `npm audit` (timeout).

**Time-budget:** at the 10-minute mark, the skill stops further work and assembles what it has:

```
Result: PARTIAL audit (--time-budget 10 reached). Completed:
  - inventory: yes
  - security: yes
  - performance: yes
  - quality: yes
  - deps: PARTIAL (npm audit timed out at 8:30)
  - test-coverage: NOT STARTED
  - architecture: NOT STARTED

Findings from completed dimensions:
  ... (Top-N from what we have)

To complete: re-run without --time-budget OR with --dimensions test-coverage,architecture.
```
