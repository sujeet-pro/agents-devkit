# `investigate-incident` — multi-source protocol

Hard rule: **at least two independent signals must agree before naming a root cause.** Single-source diagnosis is forbidden. This file codifies the rules.

## Required sources

For every incident triage:

1. **Datadog** — at least one of (logs, metrics, traces, monitors). Required.
2. **Recent deploys** — `/adk-investigate:investigate-deploy` for every repo mapped to the service. Required.

Optional but strongly recommended:

3. **Slack** — scrape the incident channel if `slack-workspace` MCP is reachable.
4. **Statsig audit log** — `/adk-investigate:investigate-statsig --use audit-log` for ±2h around symptom. (Run by `investigate-rca`; investigate-incident leaves this as a follow-up unless the team's Slack chatter explicitly mentions a gate change.)

If both required sources fail, the skill stops with a "two sources unreachable" error. Do NOT produce a single-source report.

## Correlation rules

A "signal" is something concrete pointing at a candidate cause. The skill checks these rules in order:

### Rule 1 — Deploy + log signal

- A near-symptom deploy (within ±30min of the symptom timestamp) AND a new error class first seen in the same window.
- **Strength:** strong. The most common pattern.
- **Confidence ceiling:** medium-high if diff overlap confirms; high if Slack pre-knowledge agrees.

### Rule 2 — Monitor cluster

- ≥4 monitors from one service all triggered within ±5 minutes of the symptom.
- **Strength:** medium. Implies a single root cause but doesn't yet name it.
- **Pair with:** Rule 1 (deploy correlation) or Rule 3 (host isolation) for confidence.

### Rule 3 — Host / pod isolation

- Errors only on a subset of hosts / pods (not service-wide).
- **Strength:** medium. Implies a bad node, a partial rollout, a hot-spot tenant.
- **Pair with:** the deploy timeline (was a partial rollout in progress?) or infra signals (host CPU/memory anomalies).

### Rule 4 — Slack pre-knowledge

- The team in `#incidents` has already named a candidate.
- **Strength:** strong as a directional signal; weak as a final answer.
- **Pair with:** verify the team's claim against DD or deploy evidence. Don't blindly adopt.

### Rule 5 — Statsig audit entry near symptom (RCA tool)

- A gate / experiment / config edit within ±5 minutes of the symptom.
- **Strength:** strong if the edit's object matches the affected service.
- **Pair with:** the gate's exposure data. Did the flip actually expose users to the new path?

## Decision rule

```
signals_agreeing = count(rules with non-trivial agreement)

if signals_agreeing >= 3:
    confidence = "high"
elif signals_agreeing == 2:
    confidence = "medium"
elif signals_agreeing == 1:
    label = "leading candidate" (NOT "root cause")
    confidence = "low"
else:
    hypothesis = "no leading hypothesis"
    confidence = "n/a"
```

## What counts as "independent"

- DD logs and DD metrics from the **same query** are NOT independent (both come from the same instrumentation).
- DD logs (error class) and Deploy timeline (PR diff overlap) ARE independent.
- DD metrics (latency spike) and Slack pre-knowledge (Bob said "deploy v3") ARE independent.
- Statsig audit log (gate flip) and DD metrics (error rate) ARE independent.

The intuition: independent signals come from different observation pathways. A redundant signal (two views of the same data) doesn't add confidence.

## Refusal cases

- **Both required sources unreachable.** Stop; surface the connection issue. Do not produce a report.
- **No signals correlate.** Produce a report with hypothesis = "no leading hypothesis"; suggest follow-up probes (status pages, Statsig audit, infra dashboards). Do NOT invent a hypothesis to fill the section.
- **Only one signal correlates.** Produce a report with hypothesis labeled "leading candidate" (not "root cause"). Confidence = `low`. Suggest the next probe to upgrade to a 2nd signal.

## Hand-off rules

- If hypothesis confidence = `medium` or `high`, the report's `Next actions` includes a concrete remediation (per `next-action-priorities.md`).
- If hypothesis confidence = `low` ("leading candidate"), the report's `Next actions` includes the probe to upgrade confidence (e.g. "fetch the PR diff", "scrape Slack", "pull Statsig audit") BEFORE the remediation.
- If hypothesis = "no leading hypothesis", the report's `Next actions` is the list of probes only — no remediation.

## Cross-skill rule

`/adk-investigate:investigate-rca` is the same protocol but with one extra required source: Statsig audit log for ±2h. The RCA composite is "investigate-incident plus".
