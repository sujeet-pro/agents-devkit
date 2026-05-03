# `docs-commit-message` — worked examples

## Example 1 — Conventional Commits, bug fix

**Detection:** `recent-subjects.txt` shows `feat(...): …`,
`fix(...): …`, `chore: …`. Convention = conventional.

**Staged diff:** 1 file changed (`src/checkout/CartService.ts`),
+24 / -6 lines; 1 test added
(`tests/checkout/CartService.add.test.ts`), +42 lines.

**`commit-msg.txt`:**

```
fix(checkout): clamp add-to-cart quantity to current inventory

The add-to-cart endpoint accepted any `quantity` and inserted the
row as-is, so a user could cart 10× an SKU with inventory = 1.
Subsequent checkouts then failed at the inventory decrement step
with a low-context 500.

Clamp `quantity` to `min(quantity, available(sku))` before
creating the cart line. When the clamp fires, the response body
includes `{ clamped: true, actual: <n> }` so the UI can surface
"added 1 of 3 requested" to the user.

The clamp reads the current inventory snapshot. A race with a
concurrent decrement is possible but bounded by the existing
`(cart_id, sku)` unique constraint — the unique constraint was
added in `a1b2c3d` specifically to make this case well-defined.

Refs CHK-1238
```

## Example 2 — Conventional Commits, new feature

```
feat(exports): add async export job runner

The previous /exports endpoint was synchronous and timed out on
any order set > ~10k rows (~95% of the exports our CS team
actually runs). Move to an async job model: POST /exports returns
a job id immediately; job runner consumes from Redis list
`export:queue` and writes results to S3.

Key decisions:
- Redis list instead of Pub/Sub: we need at-least-once with
  durability through a worker crash; Pub/Sub is fire-and-forget.
- Job state machine: pending -> running -> (succeeded | failed).
  No retry loop in v1; failures surface to CS for manual rerun.
- Default behind `FEATURE_EXPORTS=false`; gradual rollout via
  Statsig gate `checkout_exports_v1`.

Follow-up: move retry policy into the job runner once we have
30-day stability data (CHK-1405).

Refs CHK-1401, CHK-1402
```

## Example 3 — semantic-release style, refactor

**Detection:** subjects include `BREAKING CHANGE:` footers and
`chore(release):` bump commits. Convention = semantic-release
(a variant of Conventional Commits with stricter footer rules).

```
refactor(common): extract Money helper from 3 services

Three services had nearly-identical inline implementations of
`addCents`, `mulCents`, and `formatCents`. This change collects
them into `services/common/Money.ts` and routes the 3 services to
the shared implementation.

No behavior change intended. Regression surface is drift vs the
existing inline math, which was byte-identical in all 3 places
(verified by diff before the extract).

Follow-up: the new `Money` helper is still `toFixed(2)`-based and
is not a proper currency library. CHK-1510 tracks moving to
`dinero.js` or equivalent.

Refs CHK-1508
```

## Example 4 — free-form repo

**Detection:** subjects are sentence-case with no `type:` prefix;
e.g. "Fix checkout timeout", "Add search filter by date range".
Convention = free-form.

```
Clamp add-to-cart quantity to available inventory

Customers could cart more units than we had in stock; checkout
then failed with a generic 500 at the inventory decrement step.
Clamping in the add-to-cart path turns this into a clear UX
affordance ("added 1 of 3 requested") and prevents the 500.

The clamp uses the current inventory snapshot. Race with a
concurrent decrement is bounded by the existing (cart_id, sku)
unique constraint added in a1b2c3d.

Refs CHK-1238
```

## Example 5 — docs-only

```
docs(readme): refresh install instructions

package.json declares packageManager=pnpm@9 but the README still
told readers to run `npm install`. Replace with `pnpm install`
and add a one-line note about installing pnpm if it's missing.

Refs CHK-1099
```
