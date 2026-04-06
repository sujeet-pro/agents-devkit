---
title: Configuration Reference
description: Plugin configuration, hooks, MCP servers, and settings
order: 3
---

# Configuration Reference

ADK is configured through several files at the plugin root.

## Plugin Manifest

`.claude-plugin/plugin.json` defines the plugin identity:

```json
{
  "name": "adk",
  "description": "Agent Development Kit...",
  "version": "2.0.0",
  "author": { "name": "...", "email": "..." },
  "homepage": "https://github.com/sujeet-pro/agents-devkit",
  "license": "MIT"
}
```

The `name` field (`adk`) becomes the namespace prefix for all skills: `/adk:skill-name`.

## Settings

`settings.json` sets the default agent:

```json
{
  "agent": "use"
}
```

This activates the `/adk:use` orchestrator as the default agent, so all prompts are automatically routed through the skill identification pipeline.

## MCP Servers

`.mcp.json` configures MCP server connections:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

Additional MCP servers can be configured via `/adk:setup`:

| Server | Purpose | Transport |
|--------|---------|-----------|
| GitHub | PR operations, issue tracking | HTTP |
| Bitbucket | PR operations | stdio |
| Confluence | Document review and publishing | stdio |
| Google Drive | Document review and publishing | stdio |

## Hooks

`hooks/hooks.json` configures lifecycle hooks:

| Event | Matcher | Type | Purpose |
|-------|---------|------|---------|
| `PostToolUse` | `Edit\|Write` | prompt | Validates SKILL.md frontmatter conventions |
| `Stop` | — | prompt | Checks task completion |
| `SessionStart` | `compact` | command | Re-injects ADK context after compaction |

## Skill Frontmatter

Each skill's `SKILL.md` uses YAML frontmatter:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill name without `adk-` prefix |
| `description` | Yes | Starts with `adk -` followed by bracket tags |
| `user-invocable` | No | `true` (default) or `false` for helper skills |
| `argument-hint` | No | Parameter hint for autocomplete |
| `allowed-tools` | No | Tools the skill can use without asking |
| `workflow-tier` | Yes | `full`, `abbreviated`, `helper`, or `orchestrator` |
| `dependencies` | No | Required commands, npm packages, MCP servers |

## Upstream Dependencies

`manifest.json` tracks upstream sources:

| Source | Type | Skills |
|--------|------|--------|
| diagramkit | copy | diagram-mermaid, diagram-excalidraw, diagram-graphviz, diagram-drawio |
| superpowers | ref | develop, plan, review-pr |
| pagesmith | ref | write, docs-repo, docs-review, docs-crud, markdown |

Use `/adk:deps-tracker` to check for updates and sync changes.
