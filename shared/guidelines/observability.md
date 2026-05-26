# guideline: observability

> Loaded when the task touches logging, metrics, traces, or alerting.

## The three signals

- **Metrics**: aggregate counts/rates/distributions. Cheap. Pre-aggregated. Cardinality-bounded.
- **Logs**: discrete events with context. Expensive. High-cardinality OK.
- **Traces**: causally-linked spans across services. Essential for distributed.

## Hard rules

1. **Every request gets a `request_id`** propagated end-to-end (header `X-Request-Id` or W3C `traceparent`).
2. **Logs never include**: passwords, API tokens, PII without explicit consent, request bodies (header-only or sampled).
3. **Metric cardinality < 100k** per metric name. Tag `user_id` and you've broken this immediately.
4. **Alerts are actionable or they're noise**. Every alert has a documented runbook step (`runbook_url` tag in DD).
5. **SLOs > SLAs > raw thresholds**. Define error budget; alert when budget is being burned, not when a single sample tripped.
6. **Use OpenTelemetry**. Don't roll your own format.

## What to log (at what level)

- **DEBUG**: internal state useful for development; off in prod.
- **INFO**: routine events worth knowing about (startup, config loaded, request handled). Most events.
- **WARN**: recoverable problems (degraded mode, retry attempted, fallback used).
- **ERROR**: unrecoverable in this code path; user-visible failure.
- **FATAL/PANIC**: process about to exit.

## Metric naming

- `<service>.<subsystem>.<metric>` — e.g., `checkout.payment.processed_total`.
- Counters end in `_total`; histograms in `_seconds` or `_bytes`; gauges in `_current`.
- Tags: bounded enum or bounded range. Never user-id, request-id, or free-text.

## Alert hygiene

- Each alert names: which service, what severity, who owns it (rotation tag), runbook link.
- Multi-window multi-burn-rate for SLO alerts (Google SRE workbook). 1h-fast + 6h-slow.
- Mute / silence rules documented in code, not click-ops in DD UI.

## Anti-patterns

- `log.error("something went wrong")` with no context. Include the variables that caused it.
- Logging the entire request object. Log the request_id and 2–3 key fields.
- Metric named `users_count` with `user_id` as a tag. That's a cardinality bomb.
- Alerting on "error rate > 0". Alert on burn rate against SLO.
- A runbook that just says "page <person>". Document the diagnostic step.

## Cite when reviewing

- Repo's existing logger / metrics lib.
- `repos.json5 `repos[*].datadog.{apm_service,rum_app}` for canonical tags.
- The service's SLO doc (link in repo or Confluence).
