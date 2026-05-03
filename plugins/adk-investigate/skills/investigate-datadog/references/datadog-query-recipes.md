# `investigate-datadog` — query recipes

Common questions → exact query + MCP tool. Use these verbatim when the user's question matches.

## Logs

| Question | Tool | Query |
| --- | --- | --- |
| "errors in `<service>`" | `aggregate_logs` group-by `error.message` | `service:<svc> env:<env> status:error` |
| "5xx in `<service>`" | `aggregate_logs` group-by `http.status_code` | `service:<svc> env:<env> @http.status_code:[500 TO 599]` |
| "exceptions in `<service>`" | `aggregate_logs` group-by `error.type` | `service:<svc> env:<env> @error.kind:Exception` |
| "logs for request id `<id>`" | `get_logs` | `service:<svc> env:<env> @http.request_id:<id>` |
| "logs for user `<email>`" | `get_logs` | `service:<svc> env:<env> @usr.email:<email>` |
| "panics in `<service>`" | `get_logs` | `service:<svc> env:<env> message:"panic"` |
| "OOMs in `<service>`" | `get_logs` | `service:<svc> env:<env> "OutOfMemory" OR "OOMKilled"` |
| "slow queries in `<service>`" | `aggregate_logs` group-by `db.statement` | `service:<svc> env:<env> @db.duration:>1000` |

## Metrics

| Question | Tool | Query |
| --- | --- | --- |
| "p50 latency on `<service>`" | `get_metrics` | `percentile(50, trace.servlet.request.duration{service:<svc>,env:<env>})` |
| "p99 latency on `<service>`" | `get_metrics` | `percentile(99, trace.servlet.request.duration{service:<svc>,env:<env>})` |
| "p99 latency on `<endpoint>`" | `get_metrics` | `percentile(99, trace.servlet.request.duration{service:<svc>,env:<env>,resource_name:<route>})` |
| "error rate on `<service>`" | `get_metrics` | `sum:trace.servlet.request.errors{service:<svc>,env:<env>}.as_count() / sum:trace.servlet.request.hits{service:<svc>,env:<env>}.as_count()` |
| "throughput on `<service>`" | `get_metrics` | `sum:trace.servlet.request.hits{service:<svc>,env:<env>}.as_rate()` |
| "CPU on `<service>`" | `get_metrics` | `avg:system.cpu.user{service:<svc>,env:<env>}` |
| "memory on `<service>`" | `get_metrics` | `avg:system.mem.used{service:<svc>,env:<env>}` |
| "DB pool utilization" | `get_metrics` | `avg:hikari.connections.active{service:<svc>,env:<env>} / avg:hikari.connections.max{service:<svc>,env:<env>}` |
| "Kafka consumer lag" | `get_metrics` | `max:kafka.consumer.lag{topic:<topic>,consumer_group:<group>}` |
| "JVM GC time" | `get_metrics` | `sum:jvm.gc.parnew.time{service:<svc>,env:<env>}.as_rate()` |

## Traces

| Question | Tool | Query |
| --- | --- | --- |
| "top errored spans on `<service>`" | `list_spans` | `service:<svc> env:<env> status:error` (sort by duration desc) |
| "slowest spans on `<service>`" | `list_spans` | `service:<svc> env:<env>` (sort by `@duration` desc) |
| "trace for `<trace-id>`" | `get_trace` | trace_id=`<id>` |
| "spans where `<span-name>` failed" | `list_spans` | `service:<svc> env:<env> operation_name:<span-name> status:error` |

## Monitors

| Question | Tool | Query |
| --- | --- | --- |
| "all firing monitors" | `get_monitors` | `--state Alert,Warn,No\ Data` |
| "firing monitors for `<service>`" | `get_monitors` | `--state Alert,Warn --tag service:<svc>` |
| "monitors for team `<team>`" | `get_monitors` | `--tag team:<team>` |
| "monitors triggered in last `<X>`" | `get_monitors` | filter by `last_triggered_ts >= now - <X>` |

## Dashboards

| Question | Tool | Query |
| --- | --- | --- |
| "list dashboards for `<service>`" | `list_dashboards` | filter by `tag:service:<svc>` (if dashboards are tagged) |
| "summarize dashboard `<name>`" | `list_dashboards` + per-tile fetch | resolve `<name>` via `datadog.md.common_dashboards`; for each tile, run its underlying query |

## Error Tracking

| Question | Tool | Query |
| --- | --- | --- |
| "top error groups on `<service>`" | `error_tracking_list` | `service:<svc> env:<env>` |
| "users affected by `<error-id>`" | `error_tracking_get` | `<error-id>` |
| "first / last seen for `<error-id>`" | `error_tracking_get` | `<error-id>` |

## Common composite shapes (used by `investigate-incident`)

| Goal | Sequence |
| --- | --- |
| "Quick triage of a service" | (1) `aggregate_logs` errors group-by class. (2) `get_metrics` p99 + error rate. (3) `list_spans` top errored. (4) `get_monitors --tag service:<svc>`. |
| "Compare prod to staging" | Same query against `env:prod` and `env:staging` side by side. Stop and ask before running cross-env. |
| "What changed at `<time>`" | Events stream `sources:my_apps` + cross-ref `gh run list`. |

## Notes

- Default time window is `last 1h` from `~/.config/adk/datadog.md.default_window`.
- Default env is `prod` from `~/.config/adk/datadog.md.default_env`.
- Service shorthand is resolved via `datadog.md.service_aliases`.
- All `as_count()` / `as_rate()` should be applied at the end so DD computes correctly per-window.
- For p99 / p95 / p50, use `percentile()` over `avg()` — averages hide tail latency.
