# Performance checklist — site audit

Optional reference loaded by `audit-site` when the audit covers performance (default). Each item maps to a measurable signal; the budgets are the defaults from `@adk:build-perf` (a.k.a. `adk-build-perf`).

## Core Web Vitals (real-user, p75 mobile)

- [ ] **LCP** ≤ 2.5 s
- [ ] **INP** ≤ 200 ms
- [ ] **CLS** ≤ 0.1
- [ ] **FCP** ≤ 1.8 s
- [ ] **TTFB** ≤ 800 ms

## TTFB / network

- [ ] HTML response < 800 ms p75 mobile.
- [ ] HTTP/2 or HTTP/3 enabled at the edge.
- [ ] gzip / brotli compression on text assets.
- [ ] CDN caching configured for static assets (long max-age + immutable).
- [ ] HTML cacheable where possible (or revalidated cheaply).

## JavaScript

- [ ] Main JS bundle < 200 KB gzip per route.
- [ ] Code-split per route (no admin code shipped to logged-out users).
- [ ] Tree-shaken (no `import * as X`; no full-library imports of `lodash` / `moment`).
- [ ] Third-party scripts deferred (`defer` / `async`) and minimized.
- [ ] No `document.write`.
- [ ] No long tasks > 50 ms on initial render or critical interactions.
- [ ] Use of `scheduler.yield()` / `postTask` / `requestIdleCallback` for non-urgent work where applicable.
- [ ] bfcache-eligible: no `unload` listener; no `Cache-Control: no-store` on HTML.

## CSS

- [ ] Main CSS < 50 KB gzip.
- [ ] Critical CSS inlined; rest deferred.
- [ ] No render-blocking CSS in `<head>` unless critical.
- [ ] `content-visibility: auto` on large below-the-fold sections where applicable.
- [ ] Animations use `transform` / `opacity` (GPU-friendly), not `top` / `left` / `width`.

## Images / media

- [ ] Above-the-fold image < 200 KB; AVIF / WebP with fallback.
- [ ] `srcset` + `sizes` for responsive images.
- [ ] Explicit `width` and `height` (or `aspect-ratio`) — kills CLS.
- [ ] `loading="lazy"` on below-the-fold images.
- [ ] LCP image: `fetchpriority="high"` and `<link rel="preload" as="image">`.
- [ ] No oversized images served (origin asset > displayed size).

## Fonts

- [ ] < 100 KB per family.
- [ ] Self-hosted or CDN with `<link rel="preconnect">`.
- [ ] `font-display: swap` (or `optional` for absolute LCP).
- [ ] Subset to characters actually used.
- [ ] WOFF2 only (no TTF / OTF / WOFF1).

## Backend (if API endpoints are part of the surface)

- [ ] API p50 < 100 ms, p95 < 200 ms, p99 < 500 ms.
- [ ] No N+1 queries on hit paths.
- [ ] Pagination on list endpoints (cursor or page).
- [ ] Cache layer where applicable (HTTP, CDN, in-process, Redis) — at most ONE that gives the win.
- [ ] Connection pool sized appropriately.

## Measurement commands

```bash
# Lighthouse — synthetic CWV
npx lighthouse https://example.com --preset=desktop --output=json --output-path=lh-desktop.json
npx lighthouse https://example.com --preset=mobile  --output=json --output-path=lh-mobile.json

# Bundle size
npx vite-bundle-visualizer
npx bundlesize --config bundlesize.config.json
npx webpack-bundle-analyzer dist/stats.json

# CI gates
npx lhci autorun

# Real user monitoring (drop into HTML)
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';
onLCP(report); onINP(report); onCLS(report); onFCP(report); onTTFB(report);
```

For agent-driven measurement, prefer the `chrome-devtools` MCP (pinned to `@anthropic/chrome-devtools-mcp@latest` in `.mcp.json`):

- `browser_take_screenshot` for visual confirmation.
- `browser_profile_start` / `_stop` for CPU profiles.
- Network panel via the MCP for waterfall analysis.

## Common anti-patterns

- Comparing dev-mode bundle size to prod numbers — different.
- Comparing localhost latency to prod numbers — different.
- Single-run Lighthouse score — noisy; run ≥ 3 and report median.
- Optimizing the cold path while the hot path regresses — measure WHICH path is hot.
- Adding cache to mask a slow query — fix the query.
- Memoizing everything in React — over-memoization adds work.
