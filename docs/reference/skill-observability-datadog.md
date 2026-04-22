---
title: 'observability-datadog'
description: '|'
skill_name: observability-datadog
category: router
---
# observability-datadog — Datadog query skill

## When to use

- "What does Datadog show for X?"
- "Are there errors in service Y?"
- "What's the p99 latency on /api/checkout?"
- "Which monitors are alerting?"

## When NOT to use

- Modify Datadog config (out of scope).
- Full incident triage workflow → `@adk:observability-incident`.
- Mixpanel / product analytics → `@adk:analytics-mixpanel`.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<question>` | yes | Natural-language query |
| `<use-of>` | optional | `investigate` (default) / `dashboard-summary` / `alert-triage` |
| `<time>` | optional | Default `last 1h`; supports `last 15m`, `last 24h`, `2026-04-22T13:00..14:00`, etc. |
| `<env>` | optional | Defaults to `prod`; can be `staging`, `dev`, `all` |
| `<service>` / `<dashboard-id>` / `<monitor-tag>` | optional | Per use-of |

## Workflow per use-of

### investigate
1. Parse the question. Extract: target (service / endpoint / log query / metric name).
2. Decide the right Datadog source: logs / metrics / APM traces / events.
3. Build the query.
4. Execute via datadog MCP (`datadog.search_logs`, `datadog.query_metrics`, `datadog.query_traces`, `datadog.list_monitors`).
5. Summarize: top trends, anomalies, quick links to Datadog UI.
6. Suggest follow-up queries.

### dashboard-summary
1. Resolve `<dashboard-id>` → fetch dashboard via MCP.
2. For each tile, fetch its current data.
3. Summarize: each tile in one line; highlight anomalies; link out.

### alert-triage
1. List monitors with `state in [Alert, Warn, No Data]`, optionally filtered by tag.
2. Per monitor: when triggered, severity, last evaluation, related deploys (look for deploy events around trigger time).
3. Group by likely root cause (same deploy / same service / same metric).
4. Recommend: silence (and reason), investigate (and which `investigate` query), escalate.

## Output

`.temp/task-<slug>/observability/datadog-<use-of>.md` per `references/output-format.md`.

## Mode

`auto` only. Read-only against Datadog.

## Anti-patterns

- Querying Datadog without a time range (returns too much; rate-limited).
- Pasting raw log lines without summarization.
- Inferring causation from correlation without checking deploys.
- Forgetting to include the Datadog UI link for the user to drill in.

## References

Standard set + `references/datadog-query-recipes.md` (per source-type query patterns).
