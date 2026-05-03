# `investigate-statsig` — Statsig hosted MCP tools catalog

The Statsig hosted MCP exposes the Console API surface. This skill uses a focused subset for read-only investigations.

## Tool surface used by this skill

### Audit log — gold for "what broke prod"

| Tool | Use-of | Notes |
| --- | --- | --- |
| `Get_Audit_Logs` | List recent changes to gates / experiments / configs / metrics | Args: `--since`, `--until`. Filter by `object_type` if available. **Most-used tool during incidents.** |

### Experiments — pulse and detail

| Tool | Use-of | Notes |
| --- | --- | --- |
| `Get_List_of_Experiments` | Discover experiments | Filter by status (`active`, `ended`, `paused`) or owner. |
| `Get_Experiment_Details_by_ID` | Per-experiment config | Returns hypothesis, allocation, primary metric, guardrails. |
| `Get_Experiment_Results` | The pulse — primary metric delta, secondary metrics, guardrails, sample size, p-values | The "did the launch move the metric" tool. Used by `--use pulse` and `/adk-investigate:investigate-experiment`. |

### Gates — list and detail

| Tool | Use-of | Notes |
| --- | --- | --- |
| `Get_List_of_Gates` | List gates with filter | Filter by tag, owner, status, last-modified. |
| `Get_Gate_Details_by_ID` | One gate's targeting + rollout config | Returns rules, % rollout, owner, env. |
| `Get_Gate_Results` | One gate's exposures + check counts | By env / time. |

### Metrics — catalog

| Tool | Use-of | Notes |
| --- | --- | --- |
| `List_Metrics` | Discover metrics | Filter by type (event-based, derived). |
| `Get_Metric_Definition` | One metric's formal definition | Source events, computation, is-guardrail flag. |

## Tools EXPLICITLY NOT used (would require `omni_write`)

The skill must NEVER call these. The API key in adk's default config has `omni_read_only`, but this list is the rule:

- `Update_Gate`, `Create_Gate`, `Delete_Gate`, `Toggle_Gate`
- `Start_Experiment`, `Pause_Experiment`, `End_Experiment`, `Update_Experiment`
- `Update_Metric_Definition`, `Create_Metric`, `Delete_Metric`
- `Update_Config`, `Create_Config`, `Delete_Config`
- Anything in the user-management / API-key-management surface

If an operator needs these, they must use the Statsig console or a future
explicitly write-enabled Statsig workflow that opts into `omni_write`.

## Auth + scope

- Header: `statsig-api-key: ${STATSIG_CONSOLE_API_KEY}`.
- Console API key, scope `omni_read_only` (https://console.statsig.com/api_keys → type=Console → scope=omni_read_only).
- For browser-based OAuth, headers are omitted; not relevant for adk's CLI workflow.

## Cold-start latency

The Statsig hosted MCP is generally fast (<500ms) but Phase 1 preflight runs a no-op `Get_List_of_Gates --limit 1` to mask any cold-start.

## Rate limits

The Console API has standard rate limits (~100 req/min per key). Phase 2 caps at 5 substantive calls per skill invocation, leaving headroom for downstream skills.

## Common composite shapes (used by `investigate-experiment` and `investigate-rca`)

| Goal | Sequence |
| --- | --- |
| "Pulse + audit slice for one experiment" | (1) `Get_Experiment_Results`. (2) `Get_Audit_Logs --since experiment_start`, filtered to that experiment id. |
| "Audit ±2h around symptom" | `Get_Audit_Logs --since (T-2h) --until (T+2h)`. Used by `/adk-investigate:investigate-rca`. |
| "Stale-gate sweep" | `Get_List_of_Gates --tag <tag> --stale 30`. Useful for cleanup audits. |
