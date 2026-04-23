---
name: build-perf
description: |
  Diagnose and fix a performance regression or hit a stated performance budget — measure first, identify the bottleneck with evidence, apply the smallest correct fix, verify the win, and add a guardrail (perf test, CI budget, monitor) so it does not regress. Different from `@adk:audit-site` (a.k.a. `adk-audit-site`) which produces a full multi-axis report on a deployed site, and from `@adk:build-feature` (a.k.a. `adk-build-feature`) which implements behavior. Use when the deliverable is a measurable performance improvement (Core Web Vitals, p95 latency, bundle size, render time, query time, memory). Do not use for general code cleanup that "feels faster" without measurement (use `@adk:build-refactor` (a.k.a. `adk-build-refactor`)) or for capacity planning (out of scope).
metadata:
  category: build
  kind: task
  layer: 4
  modes: [auto]
---

# build-perf — measure-first performance optimization

Standalone task skill under the `@adk:build` (a.k.a. `adk-build`) category router. Enforces measure-before-optimize discipline and adds a guardrail so the win sticks.

## When to use

- A user-reported "the page is slow / the API is slow / the build is slow".
- A regression flagged by Lighthouse / web-vitals / Datadog / a perf test.
- A stated budget that is currently failing (e.g. LCP > 2.5s, JS bundle > 200 KB gzip, p95 > 200ms).
- A pre-launch perf check before shipping a new feature.

## When NOT to use

- "I'd like the code to feel cleaner" with no measurement → `@adk:build-refactor` (a.k.a. `adk-build-refactor`).
- A full multi-axis health report on a deployed site → `@adk:audit-site` (a.k.a. `adk-audit-site`).
- Adding new behavior with performance as a *constraint*, not the deliverable → `@adk:build-feature` (a.k.a. `adk-build-feature`) and pull this skill's checklist in as a reference.
- Database / infra capacity planning → out of scope.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<surface>` | yes | Page URL, endpoint, query, build phase, cold-start path. |
| `<metric + budget>` | yes | The metric being optimized AND the target value. "Make it faster" without a number is rejected. |
| `<env>` | optional | Local / staging / prod. Affects which tools are usable. |
| `--auto` | optional | Skip approval gates (still validates). |

## Workflow

1. **Confirm intent** — restate the surface, the metric, and the target. Approval gate unless `--auto`. If no number is given, REJECT and ask for a budget (use `references/perf-budgets.md` for defaults).
2. **Baseline measurement** — measure CURRENT value of the metric with the appropriate tool (see `references/measurement-tools.md`). Capture the raw artifact (Lighthouse JSON, web-vitals payload, flamegraph, EXPLAIN ANALYZE output, build profile). Store under `.temp/task-<slug>/perf/baseline/`.
3. **Identify the bottleneck with evidence** — the bottleneck is the SINGLE biggest contributor to the metric. Name it. Cite the line in the artifact that proves it. If you cannot point to evidence, you have not identified it yet — measure more.
4. **Plan the fix** — pick from `references/optimization-patterns.md` (the relevant one — image, JS, CSS, font, network, DB, render, memo). Reject "scattershot" fixes that touch many things. Approval gate unless `--auto`.
5. **Implement** — smallest correct change. No drive-by refactors.
6. **Re-measure** — re-run the same tool the same way. Capture the new artifact under `.temp/task-<slug>/perf/after/`. The win must be **measurable and reported as a delta** (`baseline → after`), not as a vibe.
7. **Add a guardrail** — pick one:
   - A perf test (`vitest --benchmark`, k6, autocannon, Playwright trace).
   - A CI budget (Lighthouse CI, bundlesize, custom assert).
   - A monitor (Datadog SLO, web-vitals RUM, Sentry perf).
   - If none is applicable, document that and accept regression risk explicitly in the report.
8. **Validate** — repo-native typecheck + lint + tests still green.
9. **Report** — metric / baseline / target / after / delta; bottleneck identified; fix summary; guardrail added; residual perf risk.

## Hard rules

- **Measure first, every time.** No optimization without a baseline number.
- **One bottleneck at a time.** Do not interleave fixes; you cannot attribute the win.
- **Re-measure with the same tool.** Different tools give different numbers; only same-tool deltas are credible.
- **The win must beat noise.** Run the measurement at least 3× and report median or p50/p95. A 5% improvement in noisy data is not a win.
- **A guardrail or it didn't happen.** Performance wins regress unless something tests for them.
- **Never claim "feels faster".** Either it's measured or it isn't done.

## Anti-patterns

- "I'll just memoize everything" — premature memoization adds complexity without measurement.
- Bundle splitting based on intuition — open the bundle visualizer first.
- Adding `useMemo` to fix LCP — usually the wrong layer.
- Caching the result of a slow query without fixing the query — masks the regression.
- Optimizing the cold path while the hot path is the bottleneck.
- Comparing dev-mode bundle size to prod — meaningless.
- Comparing localhost latency to production — meaningless.
- Removing helpful logs to "make it faster" — measure first; logs are rarely the bottleneck.

## Examples

```
adk-build-perf "Get LCP on /products under 2.5s on Moto G mobile" --surface https://staging.example.com/products
```

```
adk-build-perf "Get GET /api/orders p95 under 200ms" --surface src/routes/orders.ts
```

```
adk-build-perf "Cut the main JS bundle from 412 KB to under 200 KB gzip" --surface dist/main.*.js
```

## Clarifying questions (default-ask)

1. **What is the metric and the exact target value?** — _How to pick:_ Use the budgets in `references/perf-budgets.md` if the user has none. Reject "make it faster".
2. **What environment is the baseline measured in?** — _How to pick:_ Closest-to-production wins. Local is OK only when prod / staging is unreachable AND the bottleneck is clearly local-reproducible.
3. **What tool will be used for both baseline and after measurement?** — _How to pick:_ Pick one from `references/measurement-tools.md` matching the metric; never compare across tools.

## Default vs detailed output

**Default report:** Metric / baseline / target / after / delta + bottleneck name + fix summary + guardrail added + residual risk.

**Detailed report (on request or `--verbose`):** Add the raw artifact paths, the rejected hypotheses, and the per-trace flamegraph or query plan deltas.

**Artifact:** `perf-fix-bundle` — Code change + before/after measurement artifacts + guardrail (test/budget/monitor) committed.

**Artifact path:** `.temp/task-<slug>/perf/baseline/`, `.temp/task-<slug>/perf/after/`, `.temp/notes/perf-<slug>-bottleneck.md` (evidence + decision log). Code lands in the repo proper.
