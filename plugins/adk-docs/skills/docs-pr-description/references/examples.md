# `docs-pr-description` — worked examples

## Example 1 — small bug fix (3 commits, 2 files)

**Commits:**

```
abc123 fix: clamp cart quantity to inventory on add
def456 test: regression for add-to-cart > available stock
```

**PR body draft (`pr-body.md`):**

```markdown
## Summary

- **Risk:** changes the add-to-cart happy path; regression if the
  clamp is wrong.
- Clamps `quantity` to the current inventory before creating the
  cart line (`src/checkout/CartService.ts:78-95`).
- Follow-up: the "out of stock" toast copy needs a design review
  (deferred, CHK-1240).

## Changes by area

| Area | Change |
| --- | --- |
| `src/checkout/` | Add `clampToInventory(quantity, sku)` helper; call it in `addLine`. |
| `tests/checkout/` | Add regression test for `addLine(cartId, sku, qty > available)`. |

## Test plan

- **Automated:** new unit test `CartService.add.returnsClampedQuantity`.
- **Manual:** locally — `pnpm dev`, add an SKU with inventory = 1 to
  cart twice, verify the second call returns the clamped line, not a
  duplicate.

## Risks

- Clamp logic reads the current inventory snapshot; race with a
  concurrent decrement is possible. Mitigated by the existing DB
  unique constraint on (cartId, sku).

## Linked tickets

- Fixes CHK-1238.
```

## Example 2 — new feature (8 commits, 14 files, 1 migration)

**PR body draft (excerpt):**

```markdown
## Summary

- **Risk:** adds a DB migration (forward-only); rollback after deploy
  requires an explicit `alter table` script (attached below).
- New endpoint `POST /exports` creates an async export job; job
  runner consumes from Redis list `export:queue`.
- Feature flag: `FEATURE_EXPORTS` (default `false`); enabled per
  cohort via Statsig gate `checkout_exports_v1`.

## Changes by area

| Area | Change |
| --- | --- |
| `services/checkout/` | New `ExportService`; job-runner coroutine. |
| `db/migrations/` | `20260503_create_export_jobs.sql` — adds `export_jobs` table. |
| `api/openapi.yaml` | New `POST /exports` + `GET /exports/{id}`. |
| `ui/exports/` | Export-history screen + "download" affordance. |

## Test plan

- **Automated:** 7 unit tests on `ExportService`; 3 contract tests
  covering the new endpoints.
- **Staging:** deploy, run `scripts/seed-exports.sh`, confirm 5
  concurrent exports complete and the UI surfaces them.
- **Rollback rehearsal:** ran `alter table export_jobs drop …` in
  staging; verified the service boots cleanly afterwards.

## Risks

- DB migration is forward-only; rollback script attached
  (`db/migrations/rollback/20260503_drop_export_jobs.sql`).
- Job runner polls every 2s. At steady state this is ~0.04 qps on
  the Redis cluster — negligible.
- Feature flag default is `false`; zero production impact until the
  Statsig gate rollout starts.

## Linked tickets

- Implements CHK-1401, CHK-1402.
- Part of the [Q3 Exports epic](https://acme.atlassian.net/browse/EPIC-220).
```

## Example 3 — dependency bump

```markdown
## Summary

- **Risk:** upstream `react@19.0.0` removed `ReactDOM.render`;
  migrated every entry point to `createRoot`.
- No user-visible behavior change.
- Follow-up: the `react-beautiful-dnd` library is now unmaintained
  under React 19; replacing with `@dnd-kit` is tracked in CHK-1510.

## Changes by area

| Area | Change |
| --- | --- |
| `package.json` | `react`/`react-dom` 18.2 → 19.0.0. |
| `src/entry.tsx` | `ReactDOM.render` → `createRoot().render`. |
| `src/**/*.tsx` | Removed `defaultProps` from 4 function components (deprecated in 19). |

## Test plan

- **Automated:** full test suite green (`pnpm test`).
- **Manual:** ran the app locally, clicked through checkout + exports,
  no console warnings, no visual regressions.

## Risks

- React 19 changes SSR error boundaries. Our SSR is opt-in and
  disabled in staging by default; monitored `error_tracking` in DD.

## Linked tickets

- Tracks React 19 rollout (CHK-1500).
```

## Example 4 — refactor

```markdown
## Summary

- **Risk:** zero behavior change; regression surface is drift vs the
  existing implementation.
- Extracted 3 shared helpers from `CartService`, `OrderService`, and
  `InventoryService` into `services/common/Money.ts`.

## Changes by area

| Area | Change |
| --- | --- |
| `services/common/` | New `Money.ts` with `add`, `mul`, `format`. |
| `services/checkout/`, `services/orders/`, `services/inventory/` | Replaced inline money math with `Money` helpers. |

## Test plan

- **Automated:** existing money-related tests across the 3 services
  still pass (no changes to test files).
- **Manual:** inspected `git diff --stat` — no new paths except
  `Money.ts`; all changes are delete-and-import substitutions.

## Risks

- Minor: `Money.format` uses `toFixed(2)` which is how the old
  inline code worked. Future currency work should move to a proper
  currency library (out of scope for this PR).

## Linked tickets

- None (internal refactor).
```
