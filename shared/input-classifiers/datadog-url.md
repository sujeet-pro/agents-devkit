# input classifier: Datadog URL

## Patterns

| URL | Resource | MCP call |
|---|---|---|
| `app.datadoghq.com/incident/<id>` | Incident | `get_datadog_incident(id)` |
| `app.datadoghq.com/monitors/<id>` | Monitor | `search_datadog_monitors({id: ...})` |
| `app.datadoghq.com/dashboard/<slug>-<id>` | Dashboard | `get_datadog_dashboard(id)` |
| `app.datadoghq.com/logs?query=...` | Log query | `search_datadog_logs(query, window)` |
| `app.datadoghq.com/apm/services/<service>` | APM service | `search_datadog_services({name: ...})` |
| `app.datadoghq.com/apm/trace/<traceId>` | Trace | `get_datadog_trace(traceId)` |

Non-US1 sites: `datadoghq.eu`, `us3.datadoghq.com`, `us5.datadoghq.com`, `ap1.datadoghq.com`, `ap2.datadoghq.com`. Detect from URL, set `DD_SITE` if it differs from the env var.

## Extract into context.md (by resource)

### incident
```markdown
### [datadog-incident] <id> — <title>
url: <full URL>
severity: SEV-1 | SEV-2 | …
state: active | stable | resolved
created: <ts> | resolved: <ts>
commander: <user>
services affected: [...]
summary (first 80 words): <quote>
timeline events (last 5): <bullet — ts, source, summary>
```

### monitor
```markdown
### [datadog-monitor] <id> — <name>
url: <full URL>
state: Alert | Warn | OK | No Data | Muted
type: <metric / log / process / …>
service tag: <service>
query: <quote>
threshold: <crit/warn>
notify: [...]
last triggered: <ts>
```

### dashboard
```markdown
### [datadog-dashboard] <id> — <title>
url: <full URL>
last edited: <ts>
widget count: <N>
relevant widgets (top 5 by recency / by query match): <bullet>
```

## Hints

- `/adk-investigate`: the primary entry point. Anchor window to incident `created` / monitor `last_triggered` / user-supplied time.
- For dashboard inputs: the user usually wants a summary; produce `dashboard-summary` sub-flow.
- For monitor inputs: alert-triage sub-flow.
