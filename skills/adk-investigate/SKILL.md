---
name: adk-investigate
description: |
  Investigate, debug, why-is-X-slow/broken/down, what-changed, RCA, root-cause, post-mortem. Multi-source data investigator. Read-only. Triggers on: symptom + service ("checkout broken", "users see 500s" — incident sub-flow, most common), Datadog incident/monitor/dashboard/log URL (anchored), Slack alert permalink (auto-extracts service + symptom-time), Statsig URL (experiment or audit-log sub-flow), Mixpanel question (product-analytics), Snowflake/Looker question (data verification), `--use rca` for full root-cause analysis (combines incident + statsig audit-log ±2h + git-blame + optional mixpanel user-impact). Always pins an explicit time window — no "recent" / "lately". Correlates ≥2 independent signals before naming a root cause. States confidence on every claim (low/medium/high). Recommends lowest-blast-radius next action (rollback > flag-off > restart > investigate-which-PR > escalate). Never modifies a monitor / dashboard / gate / experiment. Refuses PII queries against columns in `connectors/<source>.md` frontmatter `pii_columns`. Loads adk-agent-investigator + observability guideline always.
allowed-tools: [Read, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<symptom-or-url> [--use incident|rca|experiment|datadog|mixpanel|statsig|snowflake|looker] [--window <duration>] [--service <name>] [--detailed] [--deep]"
metadata:
  category: investigate
  kind: task
  layer: 1
  paths: []
  model: sonnet
  effort: medium
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: [adk-mcp-datadog]
  needs_mcp_optional: [adk-mcp-statsig, adk-mcp-mixpanel, adk-mcp-slack, adk-mcp-snowflake, adk-mcp-looker, adk-mcp-github, adk-mcp-rag]
  needs_meta_info: [workspaces, repos, data_sources]
  forks_emitted: [window, time-resolution, cross-source-required, confidence-threshold, blast-radius-ordering, model-depth]
---

# adk-investigate — multi-source investigator

Read-only. Two-source minimum. State confidence honestly. Pin every window.

**Global skill** — runs from anywhere; artifacts go to `~/.agents-devkit/investigations/<task>/` (per `shared/paths.md`). Does not require a cwd repo.

`--detailed` widens source gathering inside the pinned window. `--deep` selects the stronger model profile per `shared/model-depth.md`; auto-select it for RCAs, multi-service incidents, security signals, ambiguous symptoms, or conflicting source evidence.

## References (loaded as needed)

| Aspect | File |
|---|---|
| Input dispatch (which sub-flow) | `references/dispatch.md` |
| Workflow (Phase 0–4) | `references/workflow.md` |
| Fork IDs | `references/forks.md` |
| Hard rules + refusals | `references/rules.md` |
| Sub-flow detail | `references/<sub-flow>.md` — authored on first real use |

## Cross-skill dependencies

- Personas: `shared/personas/{investigator,context-gatherer}.md`
- Model depth: `shared/model-depth.md`
- Guidelines: `shared/guidelines/{observability,security,performance}.md`
- Code index (lower-confidence second signal): `shared/guidelines/code-index.md` — when a symptom mentions a service / endpoint / feature, `from scripts.lib.code_index.query import open_index, similar` returns candidate code paths to anchor the trace correlation. Always treat as a secondary signal next to DD / Slack / Statsig.
- Constitution: `shared/constitution.md`
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`
