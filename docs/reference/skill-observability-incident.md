---
title: 'observability-incident'
description: '|'
skill_name: observability-incident
category: router
---
# observability-incident — multi-source incident triage

## When to use

- A production incident is suspected or confirmed.
- An alert fired and the user wants the full picture before fixing.

## When NOT to use

- Single metric query → `@adk:observability-datadog`.
- Apply the code fix → `@adk:build-bugfix`.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<symptom>` | yes | What was observed: "users see 500", "dashboard tile shows 0", etc. |
| `<service>` | optional | Service / area suspected |
| `<window>` | optional | Default `last 2h` |
| `<slack-channel>` | optional | e.g. `#incidents` for thread scrape |

## Workflow

1. **Phase 1 validator.** datadog MCP, slack MCP (if scrape), `gh` CLI all reachable.
2. **Define the window.** Default last 2h. If user provided a moment, expand ±30min.
3. **Datadog passes (parallel):**
   - Logs: errors / warnings in target service in window.
   - Metrics: error rate, p99 latency, throughput; compare to last 24h baseline.
   - Traces: top N slow / errored traces; identify common spans.
   - Monitors: which fired in window; severity; tags.
4. **Deploy timeline (gh).** `gh run list --branch main --created '>2026-04-22T11:00'` and any production deploy workflow runs in window.
5. **(Optional) Slack scrape.** `slack` MCP: pull last N messages in target channel + any thread that mentions service / symptom keywords.
6. **Correlate:**
   - Did a deploy happen just before the symptom started? → likely cause: regression in that deploy.
   - Did multiple monitors fire from one service? → likely cause: that service's recent change.
   - Errors only on certain hosts / pods? → likely cause: bad node / partial rollout.
7. **Root-cause hypothesis.** State in one paragraph. Include confidence (low/med/high).
8. **Next actions.** Pick from: rollback (which deploy), feature-flag-off, investigate (which file in which PR), restart hosts, escalate to owner.
9. **Write `incident.md`.** Hand off to `@adk:build-bugfix` if a code fix is the next action.

## Output

`.temp/task-<slug>/incident.md`:
- Symptom + window
- Datadog evidence (with UI links)
- Deploy timeline
- Slack discussion summary (if scraped)
- Correlation analysis
- Root-cause hypothesis (confidence)
- Next actions (prioritized)

## Anti-patterns

- Single-source diagnosis. Always at least Datadog + deploy timeline.
- High-confidence root cause without correlation evidence.
- Recommending rollback without checking what's in the deploy.
- Forgetting to surface Slack discussion (the team often already knows what broke).

## References

Standard set + `references/correlation-recipes.md`, `references/incident-output-template.md`.
