# Measurement tools — pick one per metric

| Metric | Preferred tool | Command / approach | Notes |
| --- | --- | --- | --- |
| **Core Web Vitals (synthetic)** | Lighthouse (CLI or DevTools) | `npx lighthouse <url> --preset=desktop --output=json --output-path=lh.json` | Run via `chrome-devtools` MCP for in-loop measurement. |
| **Core Web Vitals (real users)** | `web-vitals` JS library + your RUM | `import { onLCP, onINP, onCLS } from 'web-vitals'` | Only credible signal for real-world perf. |
| **JS bundle size** | bundlesize / `vite-bundle-visualizer` / `webpack-bundle-analyzer` | `npx bundlesize --config bundlesize.config.json`; `npx vite-bundle-visualizer` | Use one tool repo-wide; gzip-compressed numbers only. |
| **JS runtime / long tasks / flamegraph** | Chrome DevTools Performance panel | Via `chrome-devtools` MCP `browser_profile_start` / `_stop` | Profile data lands in `~/.cursor/browser-logs/`. |
| **Render performance** | React Profiler / Vue Devtools / Svelte inspector | Component-tree profiles | Look for unnecessary re-renders, large component trees. |
| **HTTP / network waterfall** | DevTools Network panel; HAR export | `chrome-devtools` MCP screenshot+HAR | Look for blocking requests, render-blocking CSS, missing `preload`. |
| **API endpoint latency (synthetic)** | autocannon / k6 / wrk | `npx autocannon -c 10 -d 30 https://localhost:3000/api/x` | Local-only is suspect; reproduce on staging. |
| **API endpoint latency (real users)** | Datadog APM / Sentry Performance / OpenTelemetry | Query trace store via the `datadog` MCP | Use p95 / p99, not avg. |
| **DB query latency** | `EXPLAIN ANALYZE` (Postgres) / `EXPLAIN FORMAT=JSON` (MySQL) / `db.collection.explain('executionStats')` (Mongo) | Run against prod-shape data | Avoid sequential scans on large tables; check index hit ratio. |
| **DB query plan over time** | pg_stat_statements / Datadog Database Monitoring | SQL snapshot + RUM | Find queries that regressed, not just the slowest. |
| **Memory leak (browser)** | DevTools Memory panel — heap snapshot diff | Take 3 snapshots: idle → after action → idle | Look for retained DOM nodes, detached listeners, growing closures. |
| **Memory leak (node)** | clinic.js / `--inspect` + heap snapshot | `npx clinic doctor -- node app.js` | Compare snapshots after sustained load. |
| **Build time** | repo build CLI with `--profile` | `vite build --profile`, `tsc --diagnostics`, `webpack --json` | Look for slow loaders / plugins. |
| **CI time** | `gh run view --log` per job | Compare CI log timestamps job-by-job | Slow gate is usually one specific step. |

## Run discipline

- ≥ 3 runs, report median (and p95 if measurable).
- Same machine / same network / same time-of-day for fair before/after.
- For browser metrics, USE Lighthouse Mobile preset unless your audience is desktop-only — desktop numbers lie about real users.
- For backend metrics, USE the production-shape dataset — synthetic 100-row tables lie.

## chrome-devtools MCP integration

The `chrome-devtools` MCP server (already in `.mcp.json`, pinned to `@anthropic/chrome-devtools-mcp@latest`) is the **preferred** way to drive these measurements in-agent. Available calls relevant to this skill:

- `browser_take_screenshot` — visual confirmation of the surface under test.
- `browser_profile_start` / `browser_profile_stop` — CPU profile + summary.
- Network/console capture for waterfall analysis.

Always pair with `@adk:validate-browser` (a.k.a. `adk-validate-browser`) `--mode visual-check` for screenshot proof.
