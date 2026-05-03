# `investigate-datadog` — MCP tools catalog

The Datadog hosted MCP exposes ~40 tools across 8 toolsets. This skill uses a focused subset for prod investigations. Read-only by App-key scope (`mcp_read`).

## Toolsets enabled

`.mcp.json` requests these toolsets via the `?toolsets=...` URL query:

```
core, dashboards, error-tracking, product-analytics, security, workflows, apm, llmobs
```

## Tool surface used by this skill

### Logs

| Tool | Use-of | Notes |
| --- | --- | --- |
| `get_logs` | List logs matching a query | Returns top N raw lines with timestamps + DD UI link. Use sparingly; aggregate first. |
| `aggregate_logs` | Group-by aggregation | Primary tool for "how many errors of each class". Group-by `error.message`, `http.status_code`, `host`, `usr.email`. |

### Metrics

| Tool | Use-of | Notes |
| --- | --- | --- |
| `get_metrics` | Query metric over a window | Use `percentile(99, ...)` for p99; `as_count()` / `as_rate()` for counts/rates. |
| `list_metrics` | Discover available metrics | Used when the operator says "what metrics do I have for `<service>`?". |

### APM / Traces

| Tool | Use-of | Notes |
| --- | --- | --- |
| `list_spans` | List spans matching a query | Sort by duration desc to find slowest; filter by `status:error` for errored. |
| `get_trace` | Drill into a single trace by id | Returns the full span tree. Useful for "trace for request id X". |

### Monitors

| Tool | Use-of | Notes |
| --- | --- | --- |
| `get_monitors` | List monitors with filter | Filter by `state` and `tag`. Returns last-triggered, severity, group state. |

### Dashboards

| Tool | Use-of | Notes |
| --- | --- | --- |
| `list_dashboards` | Find a dashboard | Filter by `tag` or by name (substring match). |
| `get_dashboard` | Fetch a dashboard's tile config | Returns tiles + their underlying queries; we then run each query separately. |

### Error Tracking

| Tool | Use-of | Notes |
| --- | --- | --- |
| `error_tracking_list` | Top error groups for a service | Group of related stacktraces; gives "first seen / last seen / affected users". |
| `error_tracking_get` | One error group's detail | Stacktrace, frequency over time, affected users. |

### Incidents (read-only here; mutations blocked)

| Tool | Use-of | Notes |
| --- | --- | --- |
| `list_incidents` | List Datadog Incident Management incidents | Used by `/adk-investigate:investigate-incident` to surface in-progress incidents. |
| `get_incident` | Detail of one incident | Includes timeline + linked monitors. |

## Tools EXPLICITLY NOT used (would require `mcp_write`)

The skill must NEVER call these. The App key in adk's default config doesn't have the scope, but this list is the rule:

- `create_monitor`, `update_monitor`, `delete_monitor`, `mute_monitor`, `unmute_monitor`
- `create_dashboard`, `update_dashboard`, `delete_dashboard`
- `create_incident`, `update_incident`, `resolve_incident`
- `create_event`, `delete_event`
- Any tool with name starting `notebook_*` (these can persist user state)
- Any tool in the `security` toolset that creates / modifies a finding

## Rate limits

- 50 req/10s burst.
- 5,000 daily tool calls.
- 50,000 monthly tool calls.

Phase 2 caps queries at 5 per skill invocation to leave headroom for downstream skills (`investigate-incident` may run 6–10 in one session).

## Cold-start latency

The Datadog hosted MCP has variable first-call latency per session (200ms – 3s). The skill warms a no-op `list_dashboards` call in Phase 1 preflight to mask this.

## Site-specific URLs

| Site | URL prefix |
| --- | --- |
| US1 (default) | `https://app.datadoghq.com` |
| EU | `https://app.datadoghq.eu` |
| US3 | `https://us3.datadoghq.com` |
| US5 | `https://us5.datadoghq.com` |
| AP1 | `https://ap1.datadoghq.com` |
| AP2 | `https://ap2.datadoghq.com` |

The `~/.config/adk/datadog.md.site` field controls which prefix is used in DD UI links.
