---
title: 'Marketplace Manifest'
description: 'adk (Agent Development Kit) — a Principal-Engineer-shaped Claude Code marketplace. Five focused plugins (adk-core, adk-code, adk-review, adk-docs, adk-investigate) covering 37 single-action skills for code writing, code review, documentation, and production investigations across Datadog, Mixpanel, Statsig, Snowflake, GitHub, Confluence, Google Drive, Slack. Every skill follows the same --auto / -i / --fix mode contract and the same Phase 0–3 workflow (prompt-expand → preflight → execute → validate-and-report). Ships 3 custom MCPs (GitHub via Docker, Datadog hosted, Statsig hosted); consumes claude.ai workspace connectors for Atlassian, Google Drive, Gmail, Google Calendar, Slack, Mixpanel, Snowflake. Per-user meta-info lives in ~/.config/adk/*.md.'
source: '.claude-plugin/marketplace.json'
---
# Marketplace Manifest

adk (Agent Development Kit) — a Principal-Engineer-shaped Claude Code marketplace. Five focused plugins (adk-core, adk-code, adk-review, adk-docs, adk-investigate) covering 37 single-action skills for code writing, code review, documentation, and production investigations across Datadog, Mixpanel, Statsig, Snowflake, GitHub, Confluence, Google Drive, Slack. Every skill follows the same --auto / -i / --fix mode contract and the same Phase 0–3 workflow (prompt-expand → preflight → execute → validate-and-report). Ships 3 custom MCPs (GitHub via Docker, Datadog hosted, Statsig hosted); consumes claude.ai workspace connectors for Atlassian, Google Drive, Gmail, Google Calendar, Slack, Mixpanel, Snowflake. Per-user meta-info lives in ~/.config/adk/*.md.

## Source

`.claude-plugin/marketplace.json`

## Plugins

- [`adk-core`](./plugins/adk-core.md) - adk universal baseline: prompt routing (auto), setup of ~/.config/adk/*.md, meta-info reader, mode contract, .temp/ layout, the universal Bash safety hook, and the canonical interaction contract. Required by every other adk plugin.
- [`adk-code`](./plugins/adk-code.md) - adk code-authoring plugin: write features, fix bugs (with reproducer + regression test first), refactor without behavior change, migrate frameworks, write/expand tests, diagnose perf, design APIs, harden security. Eight single-verb skills following the universal --auto / -i mode contract.
- [`adk-review`](./plugins/adk-review.md) - adk code-review plugin: review someone else's PR, review your local changes vs a baseline, address existing PR feedback, capture session handoff, and run quick / whole-repo audits. Six skills supporting --auto / -i / --fix. Ships GitHub MCP (Docker, read-only by default) with `gh` CLI as the equally-supported fallback.
- [`adk-docs`](./plugins/adk-docs.md) - adk documentation plugin: write/review prose docs (README, runbook, ADR, migration guide), draft PR descriptions and commit messages, append changelog entries, author Mermaid diagrams, publish to Confluence (via the workspace Atlassian connector) or Google Drive (via the workspace Google Drive connector). Eight skills.
- [`adk-investigate`](./plugins/adk-investigate.md) - adk investigation plugin: query Datadog (logs/metrics/traces/monitors), Mixpanel (funnels/cohorts/usage), Statsig (experiments/gates/audit logs), Snowflake (read-only non-PII), recent GitHub deploy timeline, and Slack incident discussions. Composite skills: investigate-incident (multi-source triage), investigate-experiment (Statsig + Mixpanel cross-check), investigate-rca (full root-cause). Ships custom MCPs for Datadog (hosted) and Statsig (hosted); consumes workspace connectors for Mixpanel, Snowflake, Slack, Atlassian.
