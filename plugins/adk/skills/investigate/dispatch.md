# investigate — input dispatch + MCP map

Route by input shape → sub-flow → data sources. Every route still pins a window and stays read-only.

| Input shape | Sub-flow | Primary sources |
|---|---|---|
| Symptom + service (free text) | incident (most common) | Datadog + recent deploys (`gh`/`git`) + Slack |
| Datadog incident / monitor / dashboard / log URL | datadog | Datadog (start there), then deploys + Slack to correlate |
| Slack alert permalink | incident | extract service + fire-time from the alert, then incident sweep |
| Statsig gate / experiment URL | statsig / experiment | Statsig audit-log + results, correlate with the symptom window |
| Mixpanel / Snowflake / Looker question | that source | the named analytics source (read-only) |
| `--use rca` | rca (full root-cause) | incident sweep + Statsig audit-log (±2h) + git-blame (`gh`/`git`) + optional Mixpanel user-impact |

## MCP map (server names from `.mcp.json`)

| Source | MCP server | Use for |
|---|---|---|
| Datadog | `adk-datadog` | logs, metrics, traces, monitors, error-tracking, APM, security signals |
| Slack | `adk-slack` | incident chatter, prior occurrences, oncall threads |
| Statsig | `adk-statsig` | gate/experiment audit log + results (read-only) |
| Mixpanel | `adk-mixpanel` | event funnels, user-impact, experiment exposure |
| Snowflake | `adk-snowflake` | warehouse queries (read-only SELECT) |
| Looker | `adk-looker` | dashboards, looks, explores (read-only) |
| Atlassian | `adk-atlassian` | linked Jira incident tickets / Confluence runbooks |
| GitHub / git | `gh` CLI + `git` | recent merged PRs, deploy commits, `git blame` on suspect lines |

## Honest degradation

If a source's MCP is unreachable, mark `[<source>: skipped]` in the report and lower the confidence of any conclusion that would have relied on it. Never substitute a guess for a source you couldn't actually read.
