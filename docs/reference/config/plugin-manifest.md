---
title: 'plugin manifest'
description: 'Claude Code plugin manifest for the adk plugin.'
artifact_kind: config
---

# plugin manifest

Claude Code plugin manifest at `.claude-plugin/plugin.json`. The presence of this file makes the entire repo loadable as the `adk` plugin via `claude --plugin-dir <path>` or installable from the marketplace at `.claude-plugin/marketplace.json`.

## Current contents

```json
{
  "$schema": "https://docs.claude.com/schemas/plugin.json",
  "name": "adk",
  "version": "1.1.0",
  "description": "Agent Development Kit (ADK) - a Claude Code plugin with 50+ composable, self-contained skills covering the full developer loop: discovery, brainstorm, requirements, scoping, planning, design, frontend, build, review, browser-based validation, docs, audits, publishing, CI/CD, and observability. Ships specialized subagents, lifecycle hooks, a registry of MCP servers, and background monitors. Every skill is highly interactive by default with --auto for unattended runs and --mode review|fix where applicable.",
  "author": {
    "name": "Sujeet Kumar Jaiswal",
    "url": "https://github.com/sujeet-pro"
  },
  "homepage": "https://github.com/sujeet-pro/agents-devkit",
  "repository": "https://github.com/sujeet-pro/agents-devkit",
  "license": "MIT",
  "keywords": [
    "agents",
    "skills",
    "claude-code",
    "claude-plugin",
    "ai",
    "mcp",
    "developer-tools",
    "code-review",
    "ci-cd",
    "browser-validation"
  ]
}
```

## Source

`.claude-plugin/plugin.json`.

Marketplace entry lives alongside it at `.claude-plugin/marketplace.json` and exposes the plugin under two source IDs (`adk` from GitHub, `adk-npm` from the npm registry).
