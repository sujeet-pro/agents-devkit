---
title: 'adk-investigate'
description: 'adk investigation plugin: query Datadog (logs/metrics/traces/monitors), Mixpanel (funnels/cohorts/usage), Statsig (experiments/gates/audit logs), Snowflake (read-only non-PII), recent GitHub deploy timeline, and Slack incident discussions. Composite skills: investigate-incident (multi-source triage), investigate-experiment (Statsig + Mixpanel cross-check), investigate-rca (full root-cause). Ships custom MCPs for Datadog (hosted) and Statsig (hosted); consumes workspace connectors for Mixpanel, Snowflake, Slack, Atlassian.'
plugin: 'adk-investigate'
source: 'plugins/adk-investigate/.claude-plugin/plugin.json'
group: 'Plugins'
order: 4500
---
# adk-investigate

adk investigation plugin: query Datadog (logs/metrics/traces/monitors), Mixpanel (funnels/cohorts/usage), Statsig (experiments/gates/audit logs), Snowflake (read-only non-PII), recent GitHub deploy timeline, and Slack incident discussions. Composite skills: investigate-incident (multi-source triage), investigate-experiment (Statsig + Mixpanel cross-check), investigate-rca (full root-cause). Ships custom MCPs for Datadog (hosted) and Statsig (hosted); consumes workspace connectors for Mixpanel, Snowflake, Slack, Atlassian.

## Source

`plugins/adk-investigate/.claude-plugin/plugin.json`

## Dependencies

- `adk-core` ^2.0.0

## Skills

- [`investigate-datadog`](../skills/adk-investigate-investigate-datadog.md)
- [`investigate-deploy`](../skills/adk-investigate-investigate-deploy.md)
- [`investigate-experiment`](../skills/adk-investigate-investigate-experiment.md)
- [`investigate-incident`](../skills/adk-investigate-investigate-incident.md)
- [`investigate-mixpanel`](../skills/adk-investigate-investigate-mixpanel.md)
- [`investigate-rca`](../skills/adk-investigate-investigate-rca.md)
- [`investigate-snowflake`](../skills/adk-investigate-investigate-snowflake.md)
- [`investigate-statsig`](../skills/adk-investigate-investigate-statsig.md)

## Agents

- [`incident-investigator`](../agents/adk-investigate-incident-investigator.md)

## Helper Binaries

No helper binaries.
