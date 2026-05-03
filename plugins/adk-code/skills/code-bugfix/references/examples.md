# `code-bugfix` — worked examples

## Example 1 — off-by-one in a date helper

**Prompt:** `/adk-code:code-bugfix "the 'last 7 days' filter on the dashboard returns 6 days of data"`

**Phase 0:** Slug `last-7-days-returns-six`. Repo `~/code/acme/dashboard`. Suspected area: `src/lib/date-range.ts` (Grep "last 7 days" finds the helper).

**Phase 1:** Clean tree. Branch `fix/last-7-days-off-by-one`. Commands: `pnpm typecheck && pnpm lint && pnpm test`. Baseline green.

**Phase 2 (REPRODUCE):** Read `date-range.ts`. The helper does `from = today.subtract(7, "day")` and `to = today.subtract(1, "day")`. Test case: assert that `lastNDays(7).to.diff(lastNDays(7).from, "day") === 7`. Test fails: actual = 6.

`reproducer.md`:
```
## Reproducer
Calling lastNDays(7) returns a window of 6 days, not 7.

## Failing test
src/lib/date-range.test.ts:
  it("lastNDays returns N days exactly", () => {
    const r = lastNDays(7);
    expect(r.to.diff(r.from, "day")).toBe(7);
  });

## Failing output
Expected: 7
Received: 6
```

**Phase 3 (DIAGNOSE):** Read the helper. The `from = today.subtract(7, "day")` and `to = today.subtract(1, "day")` together give a 6-day window (today is excluded; 7 days ago to yesterday inclusive = 6 days).

`plan.md`:
```
## Root cause
The `to` boundary uses `today.subtract(1, "day")` (yesterday end-of-day) but `from` uses `today.subtract(7, "day")`, producing a 6-day window. Either change `from` to `today.subtract(7, "day")` and `to` to `today.endOf("day")` (include today), or change `from` to `today.subtract(8, "day")` (exclude today, include 7 prior days).

## Patch
Set `to = today.endOf("day")` (include today) — matches the user expectation that "last 7 days" includes today.

## Regression test
The reproducer test from Phase 2.
```

**Phase 4 (PATCH):** Implementer changes 1 line. Re-run reproducer test → PASSES.

**Phase 5 (VALIDATE):** Full `pnpm test -- src/lib/date-range` runs; 18 tests pass. typecheck + lint green.

**Phase 6 (REPORT):** `report.md` lists: symptom, root cause, 1 file changed (+1/-1), regression test red→green, validation evidence.

---

## Example 2 — race condition in cache invalidation

**Prompt:** `/adk-code:code-bugfix "users sometimes see stale order status after an update"`

**Phase 0:** Slug `stale-order-status-after-update`. Repo `~/code/acme/orders-api`. Suspected: cache invalidation around `updateOrderStatus`.

**Phase 1:** Clean. Branch `fix/stale-order-status`. Baseline green.

**Phase 2 (REPRODUCE):** Read `services/orders/update.ts` + `services/orders/get.ts`. The cache-invalidation code does `cache.delete(key)` AFTER the DB write, but `getOrder` reads the cache before checking the DB.

Reproducer: an integration test that does `update + get` in rapid succession, asserting `get` returns the updated status. The test is flaky on first attempt — failing 4/10 runs. Document this as the reproducer signature.

`reproducer.md` notes the flakiness — under load, the cache `delete` call races with another `get` call that re-populates the cache from a stale DB read. Capture the failing pattern.

**Phase 3 (DIAGNOSE):** The cache is invalidated after the DB write returns, but the DB write is not yet committed (or the read-replica hasn't caught up). Other readers re-populate the cache with stale data between the invalidation and the commit.

`plan.md`:
```
## Root cause
`cache.delete(key)` runs after `db.commit()` returns, but read-replica replication can lag. Concurrent readers between commit and replication see the old row, then re-populate the cache.

## Patch
Move cache invalidation to AFTER read-replica acks (or invalidate inside the DB transaction commit hook). Implementation: use the existing `withTransactionalAfterCommit(() => cache.delete(key))` helper which fires after replication.

## Regression test
- The reproducer integration test (run 50 times in CI for this test).
- Plus a unit test of the helper integration.
```

**Phase 4 (PATCH):** Implementer changes 3 lines in `services/orders/update.ts` to use the `withTransactionalAfterCommit` helper.

**Phase 5 (VALIDATE):** Reproducer test now passes 50/50. Full `update.test.ts` suite green. typecheck + lint green.

**Phase 6 (REPORT):** `report.md` notes residual risk: "Other write-then-cache-delete code paths in the repo may have the same race — see follow-ups; spawn `/adk-review:audit-repo` scoped to cache patterns."

---

## Example 3 — type drift after a refactor

**Prompt:** `/adk-code:code-bugfix "checkout fails with 500 when discount field is null; stack trace pasted: TypeError: Cannot read properties of null (reading 'amount')"`

**Phase 0:** Slug `checkout-500-on-null-discount`. Repo `~/code/acme/checkout-api`. Suspected: `services/checkout/calculate.ts` — the trace top-frame.

**Phase 1:** Clean. Branch `fix/checkout-null-discount`. Baseline green.

**Phase 2 (REPRODUCE):** Write a test that calls `calculateCheckout` with `discount: null`. Test fails with the same TypeError.

**Phase 3 (DIAGNOSE):** `git log -L` on the suspected line shows a recent refactor changed the type of `Cart.discount` from `Discount | null` to `Discount | undefined`, but `calculate.ts` still treats `null` as the unset state. The check is `discount?.amount` which works for `undefined` but not when `null` is passed in by an older client.

`plan.md`:
```
## Root cause
The Cart.discount type was changed from `Discount | null` to `Discount | undefined` in commit a1b2c3, but the API still accepts `null` from older clients (the JSON parser doesn't normalize null → undefined). The `discount?.amount` access path returns null.amount → TypeError.

## Patch
At the JSON-input boundary in services/checkout/parseCart.ts, normalize `null` → `undefined` for `discount`. Internal code stays as `discount?.amount`.

## Regression test
- New test in parseCart.test.ts: null discount in input → undefined in parsed Cart.
- New test in calculate.test.ts: undefined discount → no discount applied.
```

**Phase 4 (PATCH):** Implementer adds 2 lines in `parseCart.ts`. Re-run reproducer test → green.

**Phase 5 (VALIDATE):** Full `checkout` package suite green. typecheck + lint green.

**Phase 6 (REPORT):** Notes that the fix is at the boundary, not by adding null-checks throughout `calculate.ts`. Residual risk: "Other parsers may have similar drift — track in follow-ups."

---

## Example 4 — silent exception swallow

**Prompt:** `/adk-code:code-bugfix "users report email notifications are missing for some signups, but no errors in logs"`

**Phase 0:** Slug `signup-email-missing-no-errors`. Repo `~/code/acme/auth-service`. Suspected: signup pipeline → email enqueue.

**Phase 1:** Clean. Branch `fix/signup-email-missing`. Baseline green.

**Phase 2 (REPRODUCE):** Read `services/signup/index.ts`. Find a `try { await emailQueue.enqueue(…) } catch { /* fire and forget */ }` — comment claims "fire and forget" but in practice swallows enqueue errors silently.

Reproducer: a unit test that injects a queue that throws on enqueue, expects the signup to fail (or at least log the error). Currently signup succeeds with no log.

**Phase 3 (DIAGNOSE):**

`plan.md`:
```
## Root cause
The signup pipeline wraps `emailQueue.enqueue` in `try { … } catch { /* fire and forget */ }`. When the queue is briefly unavailable (rare), the error is swallowed; the user record is created but the welcome email never sends.

## Patch
Replace the silent catch with: log the error at WARN, increment a counter metric `signup_email_enqueue_errors`. Do NOT block the signup (per existing product policy that signups must not fail because of notification failures), but make the failure observable.

## Regression test
- Unit test: queue throws → signup completes, error is logged, metric is incremented.
- Unit test: queue OK → signup completes, no error log, metric not incremented.
```

**Phase 4 (PATCH):** Implementer replaces 4 lines. Re-run reproducer test → green.

**Phase 5 (VALIDATE):** Full `signup` suite green. typecheck + lint green.

**Phase 6 (REPORT):** Notes that this is a bug fix on a *signal* gap, not on signup correctness. Residual risk: "spawn `/adk-investigate:investigate-datadog` to monitor the new metric for the first week to estimate the historical scale of missed emails."
