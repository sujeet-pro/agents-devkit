# `code-test` — worked examples

## Example 1 — backfill unit tests for a state machine

**Prompt:** `/adk-code:code-test "backfill tests for the order-state machine"`

**Phase 0:** Slug `test-order-state-machine`. Repo `~/code/acme/orders-api`. Target: `services/orders/state-machine.ts`. Framework: Vitest. Type: unit (auto-picked — pure function).

**Phase 1:** Clean tree. Branch `test/order-state-machine`. `pnpm typecheck && pnpm lint && pnpm test --filter orders-api`. Baseline green.

**Phase 2:** Read `state-machine.ts` — 8 states, ~24 transitions defined as a transition table. Read existing tests for the area (none — that's why we're here).

**Phase 3 behaviors:** Identify 4 priority behaviors (not all 24 transitions — too much):

```
B1. Valid transitions are accepted.
   Happy: created → paid is allowed; result is `paid`.
   Boundary: created → cancelled is allowed (the lowest-priority valid transition); result is `cancelled`.
   Error: created → fulfilled is rejected (skipping payment); throws InvalidTransition.

B2. Terminal states cannot transition.
   Happy: cancelled is terminal; any transition request throws.
   Boundary: refunded is terminal too.
   Error: terminal states throw a specific error type.

B3. Unknown event types are rejected.
   Happy: known event 'paid' is accepted.
   Boundary: case-sensitive — 'Paid' is rejected.
   Error: 'made-up-event' throws UnknownEvent.

B4. The transition function is pure (no side effects).
   Happy: calling twice with same args produces same result.
   Boundary: doesn't mutate the input state object.
   Error: doesn't write to any external state.
```

**Phase 4 author:** test-engineer subagent writes 12 tests (4 behaviors × 3 trio) in `services/orders/state-machine.test.ts`. For each test, fail-first verified: mutate the SUT (e.g. comment out the validity check), observe red on the test, restore, observe green.

**Phase 5 validate:** All 12 tests green. Full `orders-api` suite green (was 187, now 199). typecheck + lint green. (No `--coverage` requested.)

**Phase 6 report:** `report.md`:
- 1 file added: `services/orders/state-machine.test.ts` (+ 142 lines).
- 12 tests added; 4 behaviors covered (with trio per).
- Behaviors NOT covered: "the 24 specific transition pairs" — out of scope; trio covers the abstract behavior. Listed as residual risk: "If reviewer wants per-pair tests, follow up with another `code-test` task using `test.each([...])` to enumerate."

---

## Example 2 — integration tests for an HTTP endpoint

**Prompt:** `/adk-code:code-test "add tests for the /api/orders/:id/timeline endpoint" --integration`

**Phase 0:** Slug `test-orders-timeline-endpoint`. Repo `~/code/acme/checkout-api`. Target: `app/routes/orders.ts` (the endpoint). Framework: Jest + supertest. Type: integration (forced by `--integration`).

**Phase 1:** Clean. Branch `test/orders-timeline-endpoint`. `npm test`. Baseline green.

**Phase 2:** Read `routes/orders.ts` (Express route) + `services/orders/audit.ts` (the data source). Read existing tests in `app/routes/orders.test.ts` — uses supertest + a real Postgres test database via `docker compose up testdb`.

**Phase 3 behaviors:** 3 behaviors:

```
B1. Authenticated user gets timeline for their own order.
   Happy: GET /api/orders/<own-order-id>/timeline → 200 with array of events.
   Boundary: order with no events → 200 with [].
   Error: order with malformed UUID → 400.

B2. Authentication required.
   Happy: with valid Bearer → 200.
   Boundary: with expired Bearer → 401 (not 200; not 500).
   Error: missing Authorization header → 401.

B3. Authorization required (user can only see own orders).
   Happy: user A asking for A's order → 200.
   Boundary: user A asking for A's order with extra path component (defensive) → 200 still works.
   Error: user A asking for B's order → 404 (not 403; we leak nothing).
```

**Phase 4:** test-engineer authors 9 tests in `app/routes/orders.test.ts`. Uses supertest + the test DB. Each test fail-first: comment out the auth check, observe red, restore.

**Phase 5:** Full integration suite green (was 87, now 96). typecheck + lint green.

**Phase 6 report:** Notes that test #B3.error returns 404 (not 403) per the existing API conventions (don't leak existence). Decision recorded.

---

## Example 3 — e2e tests for a checkout flow

**Prompt:** `/adk-code:code-test "convert the manual smoke checks for the checkout flow into e2e tests" --e2e`

**Phase 0:** Slug `e2e-checkout-flow`. Repo `~/code/acme/storefront`. Target: the checkout flow (multi-page). Framework: Playwright. Type: e2e (forced).

**Phase 1:** Clean. Branch `test/e2e-checkout-flow`. `pnpm test:e2e`. Baseline green (15 e2e tests already pass).

**Phase 2:** Read `e2e/checkout.spec.ts` (existing happy-path test). Read the manual checklist file `docs/qa/checkout-smoke.md` (the source the user wants to convert). Read AGENTS.md → "e2e tests use page object model; selectors are role-based, not class-based; use `data-testid` only as last resort".

**Phase 3 behaviors:** 4 behaviors from the manual checklist:

```
B1. New user signs up and completes checkout.
   Happy: signup → add to cart → checkout → confirmation page.
   Boundary: cart with single item.
   Error: payment declined → user sees retry option.

B2. Existing user with saved payment method.
   Happy: login → add to cart → 1-click checkout → confirmation.
   Boundary: saved-method-expired → fallback to add-method form.
   Error: declined saved method → retry options.

B3. Guest checkout.
   Happy: guest → add to cart → enter email/payment → confirmation.
   Boundary: guest with previously-used email → asked to login.
   Error: invalid email → form validation.

B4. Cart abandonment recovery.
   Happy: leave checkout mid-flow; return → cart preserved.
   Boundary: 30 days later → cart cleared (per product policy).
   Error: cart with out-of-stock items → user sees out-of-stock notice.
```

**Phase 4:** test-engineer authors 12 tests in `e2e/checkout-full.spec.ts` using the page object model. Fail-first: each test verified by temporarily breaking the relevant page (commenting out the checkout button handler), observe red, restore.

**Phase 5:** All 12 e2e tests green. Total e2e suite: 27 tests, all green. Run time +3 min (e2e is slow; surfaced as residual risk).

**Phase 6 report:** Notes the trade-off ("3 min added to e2e CI time; consider parallelizing in CI config — see follow-up `code-write`"). Lists 4 behaviors covered.

---

## Example 4 — raise coverage on a discount calculator

**Prompt:** `/adk-code:code-test "raise coverage on the discount calculator from 50% to >85%" --coverage`

**Phase 0:** Slug `cover-discount-calculator`. Repo `~/code/acme/checkout-api`. Target: `services/checkout/discount.ts`. Framework: Vitest. Type: unit (auto). `--coverage` requested.

**Phase 1:** Clean. Branch `test/discount-calculator-coverage`. `pnpm test --filter checkout-api`. Baseline green.

**Phase 2:** Read `discount.ts`. ~150 lines. Functions: `applyDiscount`, `validateCode`, `calculatePercentageOff`, `calculateFlatOff`, `combineMultipleCodes`. Existing tests cover the happy path of `applyDiscount`. Coverage baseline (from `pnpm test --coverage`): 50% lines, 35% branches.

**Phase 3 behaviors:** Identify uncovered branches via the coverage report:

```
B1. Expired discount codes are rejected.
   Happy: future-expiry code → applied.
   Boundary: code expiring today end-of-day → still valid until midnight.
   Error: code expired yesterday → not applied; original total returned.

B2. Single-use codes can only be applied once.
   Happy: first use → applied.
   Boundary: second use by the same user → not applied.
   Error: second use by a different user → not applied.

B3. Combining multiple codes obeys the cap.
   Happy: 2 codes within cap → both applied.
   Boundary: 2 codes at exactly the cap → both applied.
   Error: 2 codes exceeding cap → highest-value applied; second rejected.

B4. Flat-off discounts can't exceed the cart total.
   Happy: flat $10 off on $50 cart → $10 off.
   Boundary: flat $50 off on $50 cart → $50 off (zero total).
   Error: flat $100 off on $50 cart → $50 off (capped, not negative total).
```

**Phase 4:** test-engineer authors 12 tests in `services/checkout/discount.test.ts`. Fail-first verified per test.

**Phase 5:** All 12 green. Full `checkout-api` suite green (was 187, now 199). typecheck + lint green.

**Coverage delta** (from `pnpm test --coverage`):
- Lines: 50% → 88% on `discount.ts`.
- Branches: 35% → 79% on `discount.ts`.

**Phase 6 report:** Notes the coverage delta + the specific lines / branches still uncovered (3 remaining in error handling for upstream-API failures — listed as "could be covered with mock-injection but adds little signal; deferred").
