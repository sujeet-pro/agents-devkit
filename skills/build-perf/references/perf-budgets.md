# Performance budgets — defaults

Use these as the default target when the user does not state one. Document the choice in the report.

## Core Web Vitals (real-user, p75 mobile)

| Metric | Good | Needs Improvement | Poor |
| --- | --- | --- | --- |
| **LCP** (Largest Contentful Paint) | ≤ 2.5 s | ≤ 4.0 s | > 4.0 s |
| **INP** (Interaction to Next Paint) | ≤ 200 ms | ≤ 500 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | ≤ 800 ms | ≤ 1.8 s | > 1.8 s |
| **FCP** (First Contentful Paint) | ≤ 1.8 s | ≤ 3.0 s | > 3.0 s |
| **Long Task** | ≤ 50 ms | — | > 50 ms (always poor) |

## Frontend bundle / asset

| Asset | Default budget |
| --- | --- |
| Main JS bundle | < 200 KB gzip (per route, lazy-loaded routes excluded) |
| Main CSS bundle | < 50 KB gzip |
| Above-the-fold image | < 200 KB; use AVIF/WebP with fallback |
| Web font (per family) | < 100 KB; use `font-display: swap` |
| Total page weight | < 500 KB on initial render |
| HTTP requests on initial render | < 50 |
| Lighthouse Performance score | ≥ 90 (mobile) |

## Frontend runtime

| Metric | Default budget |
| --- | --- |
| Time to Interactive (4G mobile) | < 3.5 s |
| Total Blocking Time | < 200 ms |
| Long tasks per route | 0 (one-off > 50 ms allowed during navigation) |
| Layout shifts after first paint | 0 (use `aspect-ratio`, reserve space) |

## Backend / API

| Metric | Default budget |
| --- | --- |
| API p50 | < 100 ms |
| API p95 | < 200 ms |
| API p99 | < 500 ms |
| Cold start (serverless) | < 500 ms |
| DB query (single) | < 50 ms p95 |
| N+1 queries | 0 (always a regression) |

## Build / CI

| Metric | Default budget |
| --- | --- |
| Local incremental build | < 5 s |
| Cold full build | < 60 s for medium repo, < 5 min for large monorepo |
| CI pipeline (per PR) | < 10 min |
| Test suite (unit) | < 30 s |
| Test suite (integration) | < 5 min |

## Mobile / network conditions for synthetic tests

| Profile | Throttling |
| --- | --- |
| Default Lighthouse "Mobile" | Moto G Power, Slow 4G (1.6 Mbps down / 750 Kbps up / 150 ms RTT), 4× CPU slowdown |
| Default Lighthouse "Desktop" | Cable (5 Mbps down / 5 Mbps up / 28 ms RTT), no CPU slowdown |
| Real-world worst case | iPhone SE (older), 3G (400 Kbps down / 400 Kbps up / 400 ms RTT), 6× CPU slowdown |
