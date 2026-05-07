# adk-investigate

> Production investigations across Datadog, Mixpanel, Statsig, Snowflake, recent GitHub deploy timeline, and Slack incident discussions. The Principal-Engineer's daily reality, packaged as eight read-only skills.

## What it ships

| Component | What |
| --- | --- |
| **Skills (8)** | `investigate-datadog`, `investigate-mixpanel`, `investigate-statsig`, `investigate-snowflake`, `investigate-deploy`, `investigate-incident`, `investigate-experiment`, `investigate-rca` |
| **Agents (1)** | `incident-investigator` (used by `investigate-incident` and `investigate-rca`) |
| **MCPs shipped (2)** | `datadog` (hosted, header-auth), `statsig` (hosted, header-auth) |
| **Workspace connectors consumed (5)** | Atlassian (Rovo), Mixpanel, Snowflake (Quince's QDP_SNOWFLAKE_MCP_SERVER), Slack, Google Drive |

All skills are **read-only**. None has a `--fix` flag. Investigation produces evidence; the *fix* is a separate skill (`/adk-code:code-bugfix`) that the operator (or `/adk-core:auto`) invokes after.

## Skills

### `investigate-datadog` — query Datadog: logs, metrics, traces, monitors, dashboards

Three modes-of-use: `investigate` (free-form question → targeted query + summary), `dashboard-summary` (digest of a saved dashboard), `alert-triage` (review monitors in Alert/Warn/No-Data state). Pins the time window and environment on every query; resolves repo→service shorthand from `~/.config/adk/datadog.md.service_aliases`; always includes DD UI links.

```text
/adk-investigate:investigate-datadog "errors in checkout last 1h"
/adk-investigate:investigate-datadog "summarize the Production Overview dashboard" --use dashboard-summary
/adk-investigate:investigate-datadog "which monitors are firing?" --use alert-triage --env prod
```

### `investigate-mixpanel` — query Mixpanel: funnels, cohorts, usage

Three modes-of-use: `usage-summary` (top events / DAU / WAU / retention), `funnel` (conversion through a sequence), `cohort` (user segmentation + comparison). Always pins a window and compares to a baseline; never treats low-traffic samples as conclusive; resolves event names from `~/.config/adk/mixpanel.md.common_events`.

```text
/adk-investigate:investigate-mixpanel "funnel signup → checkout last 7d"
/adk-investigate:investigate-mixpanel "DAU last week" --use usage-summary
/adk-investigate:investigate-mixpanel "retention of power_users cohort" --use cohort
```

### `investigate-statsig` — pulse, gates, audit log

Five modes-of-use: `pulse`, `gates-list`, `gates-detail`, `audit-log` (gold for "what broke prod"), `metrics-catalog`. States sample size + p-value on every pulse claim; checks guardrails before recommending ship; pulls audit log for ±2h around symptom timestamp during RCA. Read-only via `omni_read_only` scope.

```text
/adk-investigate:investigate-statsig "checkout_funnel_v3" --use pulse
/adk-investigate:investigate-statsig "what changed in last hour?" --use audit-log
/adk-investigate:investigate-statsig "checkout_redesign" --use gates-detail
```

### `investigate-snowflake` — read-only, non-PII queries

Read-only Snowflake reads via the workspace QDP_SNOWFLAKE_MCP_SERVER. Refuses any column matching the PII block list in `~/.config/adk/snowflake.md.pii_columns`. Limits results to ≤100 rows by default. Always shows SQL before executing.

```text
/adk-investigate:investigate-snowflake "count of orders today"
/adk-investigate:investigate-snowflake "active SKUs by category last 24h"
```

### `investigate-deploy` — recent deploys timeline

Surfaces deploy workflow runs in window: status, duration, triggering commit, author, workflow URL. Uses `gh run list` (CLI, no MCP). Always includes SHA + author + workflow URL; never claims "deploy caused incident" without a 2-source correlation.

```text
/adk-investigate:investigate-deploy acme/checkout-api --window 2h
/adk-investigate:investigate-deploy --window 30m
```

### `investigate-incident` — multi-source triage

Composite skill: combines Datadog (logs + metrics + traces + monitor history), recent deploy timeline (`investigate-deploy`), and (optionally) a Slack channel scrape. Produces an incident summary with a likely root-cause hypothesis (with confidence) and prioritized next actions (rollback > flag-off > restart > investigate-which-PR > escalate). Requires at least 2 sources before naming a root cause; never auto-rolls-back.

```text
/adk-investigate:investigate-incident "checkout 500s since 13:00" --service checkout --window 2h
/adk-investigate:investigate-incident "alert from 10m ago" -i
```

### `investigate-experiment` — three-source verdict

Cross-checks a Statsig experiment's pulse against Mixpanel reality and Datadog guardrails (error rate, p99). All three sources must agree on direction before recommending ship. Never recommends ship on a guardrail miss.

```text
/adk-investigate:investigate-experiment "checkout_funnel_v3"
/adk-investigate:investigate-experiment "pdp_image_carousel" --window 14d
```

### `investigate-rca` — full root-cause analysis composite

Runs `investigate-incident` end-to-end, then `investigate-statsig --use audit-log` for ±2h around symptom, then `git blame` on suspected file(s) to identify the implicated PR + author + reviewer. Optionally calls `investigate-mixpanel` for user-impact magnitude. Aggregates into a blameless RCA doc (Summary, Timeline, Detection, Mitigation, Root cause, Contributing factors, Action items per 5W frame, References). Never names individuals as root cause.

```text
/adk-investigate:investigate-rca "checkout outage 2026-05-02 13:00 UTC"
/adk-investigate:investigate-rca "search latency spike yesterday" --window 4h
```

## How skills compose with `/adk-core:auto`

The dispatcher in `/adk-core:auto` routes to investigate skills based on prompt patterns:

| User says | `auto` routes to |
| --- | --- |
| "errors in <service>" / "p99 on <endpoint>" / "alerts firing" / "summarize <dashboard>" | `investigate-datadog` |
| "funnel <a> → <b>" / "DAU last week" / "cohort retention" | `investigate-mixpanel` |
| "pulse for X" / "what changed in Statsig last hour" | `investigate-statsig` |
| "count of <thing>" / "active <thing>" / "<thing> aggregated by <other>" | `investigate-snowflake` |
| "what deployed recently" / "deploys in last 2h" | `investigate-deploy` |
| "why is X broken?" / "investigate alert from 10m ago" / "users see 500s" | `investigate-incident` |
| "should we ship the X experiment?" / "is the Y test winning?" | `investigate-experiment` |
| "RCA for the X incident" / "post-mortem prep for Y" | `investigate-rca` |

The composite skills already chain other investigate skills internally:

- `investigate-incident` calls Datadog directly + chains `investigate-deploy` + (optional) Slack scrape via the workspace connector.
- `investigate-rca` calls `investigate-incident` end-to-end, then `investigate-statsig --use audit-log`, then `git blame`.
- `investigate-experiment` calls Statsig + Mixpanel + Datadog in parallel for the same window.

Composite chains beyond this plugin (managed by `/adk-core:auto`):

| Composite goal | Chain |
| --- | --- |
| "investigate X bug and fix it" | `investigate-incident` → `/adk-code:code-bugfix` → `/adk-review:review-code-changes` |
| "ship the X experiment" | `investigate-experiment` → (if green) `/adk-code:code-write` (gate flip) → `/adk-review:review-code-changes` |
| "fix CI on this PR" | `investigate-deploy` → `/adk-code:code-bugfix` → `/adk-review:review-code-changes` |
| "post-mortem for X outage" | `investigate-rca` → `/adk-docs:docs-publish-confluence` |

## MCPs shipped

### `datadog` — hosted Datadog MCP

```jsonc
{
  "type": "http",
  "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=core,dashboards,error-tracking,product-analytics,security,workflows,apm,llmobs",
  "headers": {
    "DD_API_KEY": "${DATADOG_API_KEY}",
    "DD_APPLICATION_KEY": "${DATADOG_APP_KEY}"
  }
}
```

- **Auth env vars:** `DATADOG_API_KEY` + `DATADOG_APP_KEY` (canonical). Legacy `DD_API_KEY` / `DD_APP_KEY` are also accepted — alias them in your shell rc: `export DATADOG_API_KEY="$DD_API_KEY"; export DATADOG_APP_KEY="$DD_APP_KEY"`.
- **Scope:** App key needs `mcp_read` (and `mcp_write` only if writing). adk skills only read.
- **Site override:** `DD_MCP_URL` env var for non-US1 (`datadoghq.eu`, `us3.datadoghq.com`, `us5.datadoghq.com`, `ap1.datadoghq.com`, `ap2.datadoghq.com`).
- **Tool surface used:** `get_logs`, `aggregate_logs`, `list_spans`, `get_trace`, `get_metrics`, `list_metrics`, `get_monitors`, `list_dashboards`, `error_tracking_*`, `list_incidents`, `get_incident`.

### `statsig` — hosted Statsig MCP

```jsonc
{
  "type": "http",
  "url": "https://api.statsig.com/v1/mcp",
  "headers": {
    "statsig-api-key": "${STATSIG_CONSOLE_API_KEY}"
  }
}
```

- **Scope:** Console API key, scope `omni_read_only` by default. `omni_write` only for skills that toggle gates / start experiments — adk-investigate never does.
- **Tool surface used:** `Get_Audit_Logs`, `Get_List_of_Gates`, `Get_Gate_Details_by_ID`, `Get_Gate_Results`, `Get_List_of_Experiments`, `Get_Experiment_Details_by_ID`, `Get_Experiment_Results`, `List_Metrics`.

See [`plan/02-mcp-servers.md`](../../plan/02-mcp-servers.md) §2.2 (Datadog) and §2.3 (Statsig) for full configuration, verifier curl commands, and rate limits.

## Workspace connectors consumed

These are already enabled on the operator's claude.ai workspace; `adk-investigate` does NOT re-ship them. The skills detect them via `claude mcp list` in Phase 1 preflight.

| Connector | Used by |
| --- | --- |
| **Atlassian (Rovo)** | `investigate-incident`, `investigate-rca` (pull linked Jira/Confluence context, postmortem templates) |
| **Slack** | `investigate-incident`, `investigate-rca` (scrape `#incidents` / `#deploys` / `#oncall` for thread context) |
| **Mixpanel** | `investigate-mixpanel`, `investigate-experiment` (24-tool surface: `Run-Query`, `Get-Report`, `Get-Events`, `Get-Property-*`, `Get-Lexicon-URL`) |
| **Snowflake (Quince's QDP_SNOWFLAKE_MCP_SERVER)** | `investigate-snowflake` (read-only with PII guardrails) |
| **Google Drive** | `investigate-rca` (pull existing post-mortem templates, prior RCA references) |

If a workspace connector is unavailable, the relevant skill stops with a clear missing-thing message in Phase 1 preflight; it never auto-installs.

## Meta-info topics consumed

All defined in `~/.config/adk/`. See [`plan/01-meta-info.md`](../../plan/01-meta-info.md) for full schemas.

| Topic | Consumed by |
| --- | --- |
| `info.md` | every skill (operator name, default editor) |
| `repos.md` | every skill (repo → folder + `datadog_service` mapping) |
| `datadog.md` | `investigate-datadog`, `investigate-incident`, `investigate-experiment`, `investigate-rca` |
| `mixpanel.md` | `investigate-mixpanel`, `investigate-experiment`, optional `investigate-rca` user-impact pass |
| `statsig.md` | `investigate-statsig`, `investigate-experiment`, `investigate-rca` |
| `snowflake.md` | `investigate-snowflake` |
| `slack.md` | `investigate-incident`, `investigate-rca` |
| `github.md` | `investigate-deploy`, `investigate-incident`, `investigate-rca` |

## Installation

```text
/plugin install adk-investigate@adk
/reload-plugins
/adk-core:setup --target datadog
/adk-core:setup --target statsig
/adk-core:setup --target snowflake   # if Snowflake workspace connector enabled
/adk-core:setup --target slack
```

Required env vars (in `~/.zshenv` or shell rc — never in `~/.config/adk/*.md`):

```bash
export DATADOG_API_KEY=...             # Datadog API key (legacy DD_API_KEY also accepted via shell alias)
export DATADOG_APP_KEY=...             # Datadog Application key (mcp_read scope; legacy DD_APP_KEY also accepted)
export DD_SITE=datadoghq.com           # or datadoghq.eu, us3.datadoghq.com, etc.
export STATSIG_CONSOLE_API_KEY=...     # Statsig Console API key (omni_read_only)
```

Confirm with:

```text
/adk-core:info --check
adk-mcp-health
```

## Repo layout

```
adk-investigate/
├── .claude-plugin/plugin.json
├── README.md                                # this file
├── .mcp.json                                # datadog + statsig hosted MCPs
├── agents/
│   └── incident-investigator.md             # multi-source correlator persona
└── skills/
    ├── investigate-datadog/{SKILL.md, references/*.md}
    ├── investigate-mixpanel/{SKILL.md, references/*.md}
    ├── investigate-statsig/{SKILL.md, references/*.md}
    ├── investigate-snowflake/{SKILL.md, references/*.md}
    ├── investigate-deploy/{SKILL.md, references/*.md}
    ├── investigate-incident/{SKILL.md, references/*.md}
    ├── investigate-experiment/{SKILL.md, references/*.md}
    └── investigate-rca/{SKILL.md, references/*.md}
```
