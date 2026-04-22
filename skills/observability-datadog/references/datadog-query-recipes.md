# `observability-datadog` — query recipes

## Logs (search)

```
datadog.search_logs({
  query: "service:checkout-api status:error",
  time: { from: "now-1h", to: "now" },
  limit: 100
})
```

Common queries:
- Errors: `service:<svc> status:error`
- 5xx: `service:<svc> @http.status_code:[500 TO 599]`
- Specific user: `service:<svc> @user.id:<id>`
- Specific endpoint: `service:<svc> @http.url:"/api/checkout"`

## Metrics (query)

```
datadog.query_metrics({
  query: "avg:trace.http.request.duration{service:checkout-api}.rollup(avg, 60)",
  from: "now-1h", to: "now"
})
```

Common patterns:
- p99 latency: `p99:trace.http.request.duration{service:<svc>}`
- Error rate: `sum:trace.http.request.errors{service:<svc>}.as_rate()`
- Throughput: `sum:trace.http.request.hits{service:<svc>}.as_rate()`

## Monitors

```
datadog.list_monitors({ tags: ["env:prod", "team:platform"], state: ["Alert","Warn"] })
```

## Traces / APM

```
datadog.query_traces({
  service: "checkout-api",
  operation: "POST /api/checkout",
  time: { from: "now-1h", to: "now" }
})
```

## Always include in output

- Full Datadog UI URL (so the user can drill in): `https://<DD_SITE>/logs?query=...&from_ts=...&to_ts=...`
- Time range used.
- Total result count.
- Top 5 patterns / hosts / services in the result.
