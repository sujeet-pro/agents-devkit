---
name: analytics-mixpanel
description: |
  Query Mixpanel for product-analytics insights via the `mixpanel` MCP server (or REST fallback). Modes: `funnel` (conversion through a sequence of events), `cohort` (user segmentation), `usage-summary` (top events / DAU / WAU / retention). Use when the user asks about feature usage, conversion rates, user activity, or product engagement metrics. Do not use to modify Mixpanel projects or to query Datadog / system metrics (use `@adk:observability-datadog` (a.k.a. `adk-observability-datadog`)).
metadata:
  category: observability
  kind: task
  layer: 9
  modes: [auto]
  needs_mcp: [mixpanel]
---

# analytics-mixpanel — product analytics queries

## When to use

- "How many users used feature X last week?"
- "What's the funnel from signup → first export?"
- "Compare engagement between cohort A and cohort B."

## When NOT to use

- System / infra metrics → `@adk:observability-datadog`.
- Modify Mixpanel projects (out of scope).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<question>` | yes | Natural-language query |
| `<use-of>` | optional | `usage-summary` (default) / `funnel` / `cohort` |
| `<time>` | optional | Default `last 7d` |

## Workflow per use-of

### usage-summary
1. Identify scope: top N events, DAU/WAU/MAU, retention curve.
2. Run via mixpanel MCP `mixpanel.query_events`.
3. Summarize trends; flag week-over-week deltas.

### funnel
1. Parse the sequence: A → B → C.
2. Run `mixpanel.run_funnel` with the steps + time range.
3. Report: per-step conversion rate, drop-off, time-to-step.

### cohort
1. Define cohort: users with property X / who did event Y in window Z.
2. Run `mixpanel.run_cohort` and a comparison.
3. Report: size, engagement, retention vs comparison cohort.

## Output

`.temp/task-<slug>/analytics/mixpanel-<use-of>.md`.

## Anti-patterns

- Querying without a time range.
- Treating funnels with very low traffic as conclusive.
- Using Mixpanel as the source of truth for billing-relevant counts (use the production DB for that).

## References

Standard set + `references/mixpanel-query-recipes.md`.
