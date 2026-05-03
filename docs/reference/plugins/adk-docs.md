---
title: 'adk-docs'
description: 'adk documentation plugin: write/review prose docs (README, runbook, ADR, migration guide), draft PR descriptions and commit messages, append changelog entries, author Mermaid diagrams, publish to Confluence (via the workspace Atlassian connector) or Google Drive (via the workspace Google Drive connector). Read access to existing GDocs / Confluence pages uses workspace connectors; no MCP shipped.'
plugin: 'adk-docs'
source: 'plugins/adk-docs/.claude-plugin/plugin.json'
group: 'Plugins'
order: 3500
---
# adk-docs

adk documentation plugin: write/review prose docs (README, runbook, ADR, migration guide), draft PR descriptions and commit messages, append changelog entries, author Mermaid diagrams, publish to Confluence (via the workspace Atlassian connector) or Google Drive (via the workspace Google Drive connector). Read access to existing GDocs / Confluence pages uses workspace connectors; no MCP shipped.

## Source

`plugins/adk-docs/.claude-plugin/plugin.json`

## Dependencies

- `adk-core` ^2.0.0

## Skills

- [`docs-changelog`](../skills/adk-docs-docs-changelog.md)
- [`docs-commit-message`](../skills/adk-docs-docs-commit-message.md)
- [`docs-diagram`](../skills/adk-docs-docs-diagram.md)
- [`docs-pr-description`](../skills/adk-docs-docs-pr-description.md)
- [`docs-publish-confluence`](../skills/adk-docs-docs-publish-confluence.md)
- [`docs-publish-gdrive`](../skills/adk-docs-docs-publish-gdrive.md)
- [`docs-review`](../skills/adk-docs-docs-review.md)
- [`docs-write`](../skills/adk-docs-docs-write.md)

## Agents

- [`doc-reviewer`](../agents/adk-docs-doc-reviewer.md)
- [`doc-writer`](../agents/adk-docs-doc-writer.md)

## Helper Binaries

No helper binaries.
