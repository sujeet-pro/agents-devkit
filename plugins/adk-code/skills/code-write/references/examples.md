# `code-write` — worked examples

## Example 1 — add a CLI flag

**Prompt:** `/adk-code:code-write "add a --since flag to the export command that defaults to 7 days ago"`

**Phase 0:** Slug `add-since-flag-export`. Repo resolved to `~/code/acme/cli` from `repos.md`. Likely files (via Grep `commander|yargs|argparse`): `src/commands/export.ts`, `src/commands/export.test.ts`, `docs/cli/export.md`.

**Phase 1:** `git status` clean. On branch `feat/export-since`. Commands: `npm run typecheck`, `npm run lint -- --max-warnings 0`, `npm test -- src/commands/export`. Baseline green.

**Phase 2:** Read `export.ts` (uses `commander`), `export.test.ts` (uses Vitest), 2 adjacent commands for option-style consistency (`--since` exists on `import` already; reuse the same parser). Read `AGENTS.md` (says "use `dayjs` for date math, never `moment`").

**Phase 3:** `plan.md`:
- Goal: Accept `--since <duration|date>` on `export`; default `7d`.
- Files touched: `src/commands/export.ts` (edit, add option + parse + thread to query), `src/commands/export.test.ts` (edit, add 3 tests: default, explicit duration, explicit date).
- Edge cases: invalid string → exit code 2 with `commander`'s built-in error.
- Out of scope: refactoring the existing date-parsing helper.

**Phase 4:** Implementer adds the option, threads `since` to the query, reuses the existing helper. Test-engineer adds the 3 tests + 1 boundary test (zero-day window). All four tests fail-first.

**Phase 5:** typecheck green, lint green, 47 tests in `src/commands/export*` pass.

**Phase 6:** `report.md` lists 2 files (+18 / -2), 4 new tests, the auto-decisions ("default = 7d, picked from prompt"), residual risk ("docs/cli/export.md not updated — see follow-ups").

---

## Example 2 — add a new HTTP endpoint

**Prompt:** `/adk-code:code-write "add a GET /api/orders/:id/timeline endpoint that returns the audit log for the order"`

**Phase 0:** Slug `orders-id-timeline-endpoint`. Repo `~/code/acme/checkout-api`. Likely files: `app/routes/orders.ts`, `app/routes/orders.test.ts`, `app/services/orders/audit.ts`. Check for an existing `audit.ts` first via Glob.

**Phase 1:** Clean tree. Branch `feat/orders-timeline`. Commands `./gradlew :app:test :app:check`. Baseline green.

**Phase 2:** Read `orders.ts` (Express + zod for validation), `orders.test.ts` (supertest), the existing audit-log table query in `app/services/orders/audit.ts`. Read `CONTRIBUTING.md` (says "all routes use `asyncHandler` wrapper, all responses use `OkResponse<T>`").

**Phase 3:** `plan.md`:
- Goal: GET `/api/orders/:id/timeline` → `OkResponse<TimelineEvent[]>`.
- Files touched: `app/routes/orders.ts` (add route + zod schema), `app/services/orders/audit.ts` (add `getTimelineForOrder(id)` if not present), `app/routes/orders.test.ts` (3 tests: 200 happy, 404 unknown id, 401 if not authenticated).
- Edge cases: missing order → 404. Empty timeline → 200 with `[]`.
- Validation at boundary: `id` validated as UUID via zod. No internal null checks.
- Out of scope: streaming the timeline (current scale is fine with one query); permissioning beyond the standard auth middleware.

**Phase 4:** Implementer adds the route + service method. Reuses the existing `asyncHandler` + `OkResponse`. Test-engineer authors the 3 tests with supertest, fail-first verified.

**Phase 5:** Gradle test green, lint green, 8 tests in `orders` pass.

**Phase 6:** `report.md` lists 3 files (+47 / -0), 3 new tests, 1 auto-decision (response shape), residual risk ("rate-limit not added — current API has no rate-limit framework yet — see follow-ups").

---

## Example 3 — extend a dashboard with a new column

**Prompt:** `/adk-code:code-write "add a 'last login' column to the users dashboard"`

**Phase 0:** Slug `users-dashboard-last-login`. Repo `~/code/acme/admin-dashboard`. Likely files: `src/dashboards/users/columns.tsx`, `src/dashboards/users/page.tsx`, possibly `src/api/users.ts`.

**Phase 1:** Clean. Branch `feat/users-last-login`. Commands `npm run typecheck && npm run lint && npm test -- users`. Baseline green.

**Phase 2:** Read `columns.tsx` (uses TanStack Table column defs), `users/page.tsx`, `src/api/users.ts` (query returns `User[]` — does it include `lastLoginAt`? Read the type). It does — backend already exposes it. Read `AGENTS.md` (says "format dates with the `<RelativeTime>` component, not `Intl.DateTimeFormat` directly").

**Phase 3:** `plan.md`:
- Goal: Add a "Last login" column showing relative time.
- Files touched: `src/dashboards/users/columns.tsx` (one new column def).
- Edge cases: never-logged-in user → "—". Pulled from the field being null.
- Validation: existing snapshot test will refresh; add 1 test for the empty-state cell.

**Phase 4:** Implementer adds 8 lines to `columns.tsx`. Test-engineer adds the empty-state test.

**Phase 5:** typecheck + lint + tests green. Snapshot test required `--update`; flagged for review (the user accepts under `-i`; under `--auto`, treated as a documented decision).

**Phase 6:** `report.md` lists 1 file (+8 / -0), 1 new test, 1 auto-decision under `--auto` (snapshot updated).

---

## Example 4 — wire a feature flag into an existing flow

**Prompt:** `/adk-code:code-write "wire the new statsig gate `checkout_v3` to gate the new payment provider in the checkout flow"`

**Phase 0:** Slug `wire-checkout-v3-gate`. Repo `~/code/acme/storefront`. Likely files: `src/checkout/payment.ts`, `src/checkout/payment.test.ts`, possibly the statsig provider wrapper. Confirm gate name with the user under `-i`; under `--auto`, trust the prompt.

**Phase 1:** Clean. Branch `feat/checkout-v3-gate`. Commands `pnpm typecheck && pnpm lint && pnpm test -- checkout`. Baseline green.

**Phase 2:** Read `payment.ts` (already has 2 paths: `legacy` and `experimental`). Read `src/lib/statsig.ts` (existing wrapper exposes `useGate(name)`). Read recent commits — last gate wired (`pricing_v2`) used the same pattern. Read `AGENTS.md` (says "every new gate gets a fallback path in case statsig is unavailable").

**Phase 3:** `plan.md`:
- Goal: Use `checkout_v3` to switch between current provider and new provider in the payment step.
- Files touched: `src/checkout/payment.ts` (read gate, branch on it), `src/checkout/payment.test.ts` (2 new tests: gate on, gate off; mock `useGate`).
- Edge case: statsig unavailable → fall back to current provider (per AGENTS.md).
- Out of scope: the new payment provider implementation itself (assumed to exist as `src/checkout/providers/v3.ts`; if not, STOP and ask).

**Phase 4:** Implementer adds the branch (~10 lines). Test-engineer adds 3 tests (on, off, unavailable).

**Phase 5:** typecheck + lint + tests green.

**Phase 6:** `report.md` lists 2 files, 3 new tests, residual risk ("monitor `checkout_v3` rollout; default exposure is 0% — see `/adk-investigate:investigate-statsig` for pulse").
