---
title: 'adk-review'
description: 'adk code-review plugin: review someone else''s PR, review your local changes vs a baseline, address existing PR feedback, capture session handoff, and run quick / whole-repo audits. Ships GitHub MCP (Docker, read-only by default) with `gh` CLI as the equally-supported fallback. All review skills support --auto / -i / --fix.'
plugin: 'adk-review'
source: 'plugins/adk-review/.claude-plugin/plugin.json'
group: 'Plugins'
order: 2500
---
# adk-review

adk code-review plugin: review someone else's PR, review your local changes vs a baseline, address existing PR feedback, capture session handoff, and run quick / whole-repo audits. Ships GitHub MCP (Docker, read-only by default) with `gh` CLI as the equally-supported fallback. All review skills support --auto / -i / --fix.

## Source

`plugins/adk-review/.claude-plugin/plugin.json`

## Dependencies

- `adk-core` ^2.0.0

## Skills

- [`audit-pr`](../skills/adk-review-audit-pr.md)
- [`audit-repo`](../skills/adk-review-audit-repo.md)
- [`review-code-changes`](../skills/adk-review-review-code-changes.md)
- [`review-feedback`](../skills/adk-review-review-feedback.md)
- [`review-handoff`](../skills/adk-review-review-handoff.md)
- [`review-pr`](../skills/adk-review-review-pr.md)

## Agents

- [`code-reviewer`](../agents/adk-review-code-reviewer.md)
- [`security-reviewer`](../agents/adk-review-security-reviewer.md)

## Helper Binaries

No helper binaries.
