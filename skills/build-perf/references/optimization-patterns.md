# Optimization patterns — catalog by surface

Pick the pattern that matches the **identified bottleneck** (per Phase 2 of the validator). Do not apply patterns speculatively.

## Image / media

- Use modern formats: AVIF → WebP → JPEG/PNG fallback (`<picture><source ...>...</picture>`).
- Use `srcset` + `sizes` so the browser picks the right asset per device.
- Always set `width` and `height` (or `aspect-ratio`) to reserve space (kills CLS).
- Lazy-load below-the-fold images (`loading="lazy"`).
- Above-the-fold LCP image: use `fetchpriority="high"` and `<link rel="preload" as="image">`.
- Self-host fonts (`font-display: swap`) or use `font-display: optional` for absolute LCP.

## JavaScript

- **Code-split per route** (dynamic `import()`); don't ship admin code to logged-out users.
- **Tree-shake**: ESM imports, no `import * as X`; check the bundle for accidental whole-library inclusion.
- **Defer non-critical**: `<script defer>` / `<script async>` on third-party tags.
- **Replace heavy deps**: `lodash` → per-method imports, `moment` → `date-fns`/`dayjs`/native `Intl`.
- **`scheduler.yield()` / `postTask` / `requestIdleCallback`** for non-urgent work to break long tasks.
- **`isInputPending()`** to interrupt long sync work when the user interacts.
- **Web Workers** for genuinely CPU-bound work (parsing, image processing, crypto).

## CSS

- **Critical CSS inline** in `<head>`; defer the rest with `media="print"` swap or `<link rel="preload" as="style">`.
- **Eliminate render-blocking CSS** — measure with DevTools Coverage tab.
- **Avoid expensive selectors** (`:has()` on large trees, complex sibling combinators).
- **`content-visibility: auto`** on large below-the-fold sections to skip rendering until visible.
- **Use `transform` / `opacity`** for animations; avoid layout-triggering properties (`top`, `left`, `width`).

## React / framework rendering

- Memoize ONLY measured-hot components (`React.memo`, `useMemo`, `useCallback`); over-memoization adds work.
- Move state DOWN — avoid re-rendering the whole tree from a top-level state change.
- Virtualize long lists (`react-window`, `@tanstack/react-virtual`) — anything over ~100 items.
- Suspense + streaming for slow data (RSC, `Suspense`, `use()`).
- `useDeferredValue` for input → expensive list filter patterns.
- For client-side queries: cache + dedupe via `@tanstack/react-query` or equivalent.

## Backend / API

- **Eliminate N+1**: batch with `IN (...)` or DataLoader pattern; one query per page/section.
- **Add indexes** on the column(s) the slow query filters/joins on (verify with `EXPLAIN ANALYZE`).
- **Pagination** is mandatory for any list endpoint (cursor preferred).
- **Cache reads**: HTTP cache (`Cache-Control`, `ETag`), CDN, in-process (LRU), or Redis — one layer that gives the win, not all four.
- **Avoid synchronous I/O in request hot path**: queue async work, return 202 with status URL.
- **Connection pooling** correctly sized for the host (Postgres / Mongo / Redis).
- **Compression**: gzip / brotli at the edge (CDN) or framework middleware.

## Database

- **Add the right index** — composite indexes match the WHERE+ORDER BY pattern.
- **Drop unused indexes** — they slow writes and inflate cache.
- **Use `LIMIT` + `WHERE`** on every query that scans (`SELECT ... LIMIT 1` for existence checks).
- **Avoid `SELECT *`** — fetch only the columns you use.
- **Materialized views** for expensive read patterns that tolerate slight staleness.
- **Read replicas** for analytics-style reads (NOT for read-after-write paths).

## Build / CI

- **Cache the cache**: lockfile-keyed dep cache, build cache, test cache.
- **Parallel jobs** for independent steps (lint vs typecheck vs unit tests).
- **Skip what didn't change** — use changed-file detection (e.g. `nx affected`, `turbo run --filter`, manual diff).
- **Profile the build** (`vite build --profile`, `tsc --diagnostics`) — usually one slow plugin / one slow project reference.
- **Smaller test matrix** — pick one Node version per OS for PR; full matrix for main only.

## Anti-patterns (general)

- "Memoize everything" — adds memory and complexity, often slower in practice.
- Adding a cache to mask a slow query — fix the query.
- Removing logs to "make it faster" — measure; logs are almost never the bottleneck.
- Bundle splitting based on intuition — open the bundle visualizer first.
- Optimizing the cold path while the hot path regresses — measure WHICH path is hot.
- Comparing dev-mode bundle size to prod — meaningless.
