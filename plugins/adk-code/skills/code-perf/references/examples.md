# `code-perf` — worked examples

## Example 1 — endpoint p99 spike (N+1 query)

**Prompt:** `/adk-code:code-perf "checkout API p99 jumped from 250ms to 1.2s after Tuesday's deploy"`

**Phase 0:** Slug `perf-checkout-p99-spike`. Repo `~/code/acme/checkout-api`. Service tag (per `datadog.md`): `checkout-api`. Metric: p99 latency.

**Phase 1:** Clean tree. Branch `perf/checkout-p99-spike`. Tests green on HEAD. DD MCP reachable; `DATADOG_API_KEY` + `DATADOG_APP_KEY` present.

**Phase 2 baseline:** Pull DD APM trace for `checkout-api` over last 24h.

`measurement-baseline.md`:
```markdown
## Baseline
- Tool: Datadog APM (link to dashboard)
- Window: 2026-05-01 to 2026-05-03 (covers the deploy)
- Metric:
  - p50: 80ms (stable)
  - p95: 320ms (was 180ms; +78%)
  - p99: 1240ms (was 250ms; +396%)
- Affected route: POST /api/checkout (p99 unchanged on other routes)
- Slowest trace ID: abc-def-123
```

**Phase 3 identify:** Pull a slow trace; see the spans. Bottleneck: 47 sequential `getUser(userId)` calls inside the request handler — N+1.

`bottleneck.md`:
```markdown
## Hypothesis
The new "show recent buyers" feature in the checkout response triggers an
N+1: for each item in the cart, the handler fetches the buyer list, then
for each buyer fetches the user record sequentially.

## Evidence
DD trace span tree (depth 4):
  POST /api/checkout (1240ms)
    → getCart (12ms)
    → getRecentBuyers (8ms)
    → for buyer in buyers: getUser(id) — 47 sequential spans, ~25ms each
    → calculateTotal (4ms)

Quote (≤15 words): "47 sequential getUser spans inside POST /api/checkout"

## Confidence
High. The pattern (47 sequential spans of the same shape, all on the same
DB connection) is the signature of an N+1.

## Proposed fix
Replace the per-buyer getUser call with a single batched getUsers(ids)
call.
```

**Phase 4 fix:** Implementer changes `services/checkout/recent-buyers.ts` to use the existing `getUsers(ids: string[])` helper. ~6 lines changed.

**Phase 5 verify:** Re-measure (deploy to staging; pull DD trace).

`measurement-after.md`:
```markdown
## After
- Tool: Datadog APM (staging)
- Window: 5 min post-deploy
- Metric:
  - p50: 78ms (unchanged)
  - p95: 165ms (was 320ms; -48%)
  - p99: 240ms (was 1240ms; -81%)
- Same trace shape: getUsers(ids) is now 1 span (~30ms) instead of 47.
```

Metric moved as expected.

**Phase 6 guardrail:** Add a perf test asserting checkout completes in < 500ms with a 50-buyer test cart. Recommend adding a DD monitor for `p99 > 500ms over 5min`.

**Phase 7 report:** `report.md` summarizes before/after, the fix, the guardrail, and notes residual risk: "Other endpoints with similar patterns (orders/timeline, recommendations) may have the same N+1; spawn `audit-repo` for a sweep."

---

## Example 2 — memory leak in a worker

**Prompt:** `/adk-code:code-perf "memory keeps growing on the document-processor workers; OOM-killed after 6 hours"`

**Phase 0:** Slug `perf-doc-processor-memory-leak`. Repo `~/code/acme/document-processor`. Metric: RSS over time.

**Phase 1:** Clean. Branch `perf/doc-processor-memory-leak`. Tests green.

**Phase 2 baseline:** Run a controlled load: 1000 docs through the worker; capture heap snapshots at t=0, 200, 500, 1000.

`measurement-baseline.md`:
```markdown
## Baseline
- Tool: Node V8 heap snapshots (Chrome DevTools)
- Workload: 1000 sample docs through the worker
- RSS at t=0:    180 MB
- RSS at t=200:  340 MB
- RSS at t=500:  680 MB
- RSS at t=1000: 1.3 GB (and growing)
- Heap retained: large arrays of `ProcessedDoc` keep growing.
```

**Phase 3 identify:** Diff the heap snapshots. Find: `ProcessingCache` (a singleton) accumulates `ProcessedDoc` objects keyed by docID; nothing evicts.

`bottleneck.md`:
```markdown
## Hypothesis
ProcessingCache (Map<docID, ProcessedDoc>) is intended as a per-batch
cache, but it's a module-level singleton — entries accumulate across
batches and are never evicted.

## Evidence
Heap snapshot diff:
  ProcessingCache.entries: 0 → 200 → 500 → 1000
  Retained size of ProcessingCache: 0 → 80MB → 220MB → 600MB

Quote: "ProcessingCache.entries grows monotonically: 0 → 1000 across batches"

## Confidence
High. Snapshot diff cleanly shows a single object retaining proportional
to docs processed.

## Proposed fix
Make ProcessingCache scope-bound to a single batch; clear after each
batch. Or use an LRU with max-size cap.
```

**Phase 4 fix:** Implementer adds `cache.clear()` at the end of each batch + a guardrail max-size of 200 entries. ~12 lines changed.

**Phase 5 verify:** Re-run the workload.

`measurement-after.md`:
```markdown
## After
- Workload: same 1000 docs
- RSS at t=0:    180 MB
- RSS at t=200:  220 MB
- RSS at t=500:  220 MB
- RSS at t=1000: 220 MB (stable; no growth)
```

Metric moved as expected.

**Phase 6 guardrail:** Add a `processing-cache.test.ts` test that processes 100 docs and asserts `cache.size <= 200` at end. Recommend a Datadog monitor: `worker_rss > 500MB`.

**Phase 7 report:** Notes that the module-level singleton pattern was used in 2 other places; flagged for follow-up audit.

---

## Example 3 — slow page load (browser)

**Prompt:** `/adk-code:code-perf "the dashboard takes 8s to load; we want LCP < 2.5s" --budget lcp=2500ms`

**Phase 0:** Slug `perf-dashboard-lcp`. Repo `~/code/acme/dashboard`. Metric: Lighthouse LCP. Budget: 2500ms.

**Phase 1:** Clean. Branch `perf/dashboard-lcp`. Tests green.

**Phase 2 baseline:** Lighthouse run on `https://staging.acme.com/dashboard`.

`measurement-baseline.md`:
```markdown
## Baseline
- Tool: Lighthouse (mobile profile, slow 4G throttling)
- LCP: 5.2s (target: 2500ms)
- TTI: 6.8s
- TBT: 1.8s
- Largest contentful element: <img class="hero-image">
- Bundle: 1.2MB JS (uncompressed); 380KB gzipped
```

**Phase 3 identify:** Chrome DevTools perf trace. Long task #1: 1.2s parsing+executing `vendor.js` (a large bundle of dependencies). Long task #2: 0.8s fetching the hero image (no preconnect; large file).

`bottleneck.md`:
```markdown
## Hypothesis (multi-cause)
1. The vendor.js bundle is 1.2MB; parse+exec is 1.2s on the test profile.
2. The hero-image fetch is delayed because the request is fired late
   (no preconnect to the CDN; image element waits for CSS layout).

## Evidence
Chrome perf trace:
  - vendor.js: parse 480ms, eval 720ms (total 1200ms)
  - hero-image: requested at 2400ms, arrived at 4900ms

Quote: "vendor.js parse+eval: 1200ms blocking main thread"
Quote: "hero-image requested 2400ms; layout-blocked"

## Confidence
High for cause 1; medium for cause 2 (the hero image timing depends on
CDN latency variance).

## Proposed fix
1. Code-split: move dynamic-only deps (charts, date-pickers) out of
   vendor.js into lazy chunks.
2. Add <link rel="preconnect" href="https://cdn.acme.com">.
3. Use <link rel="preload" as="image"> for the hero.
```

**Phase 4 fix:** Implementer applies all three changes (the third is mechanical; the first is the bigger change). ~30 lines + 1 webpack config edit.

**Phase 5 verify:** Lighthouse re-run.

`measurement-after.md`:
```markdown
## After
- LCP: 2.1s (target met!)
- TTI: 3.2s
- TBT: 0.6s
- Bundle: vendor.js now 480KB; lazy chunks load on demand
```

Met budget.

**Phase 6 guardrail:** Add Lighthouse-CI threshold: `categories:performance: minScore 0.85` and `audits:largest-contentful-paint: maxNumericValue: 2500`.

**Phase 7 report:** Lists the 3 fixes + the LH-CI threshold added.

---

## Example 4 — slow CI build

**Prompt:** `/adk-code:code-perf "the CI build is taking 6 minutes; can we get it under 2?" --budget build=120s`

**Phase 0:** Slug `perf-ci-build`. Repo `~/code/acme/storefront`. Metric: build time. Budget: 120s.

**Phase 1:** Clean. Branch `perf/ci-build`. Tests green.

**Phase 2 baseline:** Time the build locally (3 runs).

`measurement-baseline.md`:
```markdown
## Baseline
- Tool: `time pnpm build` (3 runs averaged)
- Total: 5m 47s (avg)
- Step breakdown (from build --profile):
  - install dependencies: 1m 20s
  - typecheck: 1m 10s
  - bundle (webpack): 2m 50s
  - lint: 27s
```

**Phase 3 identify:** Bundle is the bottleneck (49% of total time).

Run webpack with `--profile`. Largest cost: ts-loader compiling 4000 TS files sequentially.

`bottleneck.md`:
```markdown
## Hypothesis
ts-loader compiles TypeScript synchronously; switching to esbuild-loader
(or SWC) typically gives 5-10x speedup for the same output.

## Evidence
webpack --profile shows:
  ts-loader: 2m 30s (88% of bundle time)

Quote: "ts-loader: 2m 30s of 2m 50s bundle time"

## Confidence
High. Switching loader is a documented optimization with 5-10x
literature.

## Proposed fix
Replace ts-loader with esbuild-loader (transpile-only mode). Keep tsc
in the typecheck step (already separate; no behavior change).
```

**Phase 4 fix:** Implementer swaps ts-loader for esbuild-loader in `webpack.config.js`. ~5 lines + 1 devDep change.

**Phase 5 verify:** Re-time (3 runs).

`measurement-after.md`:
```markdown
## After
- Total: 1m 48s (avg) — was 5m 47s
- Step breakdown:
  - install dependencies: 1m 20s (unchanged)
  - typecheck: 1m 10s (unchanged; still uses tsc)
  - bundle (webpack): 18s (was 2m 50s)
  - lint: 27s (unchanged)
```

Met budget (1m 48s < 2m).

**Phase 6 guardrail:** Add a CI step: fail the build if total wall time > 180s (1.5x budget for noise tolerance). Recommend a CI dashboard tracking build-time over time.

**Phase 7 report:** Lists the loader swap + the CI gate. Residual risk: "esbuild-loader doesn't typecheck (transpile-only); the existing typecheck step still does. Confirm in CI that typecheck failures still gate merging."
