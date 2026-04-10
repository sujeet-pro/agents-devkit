---
title: Configuration Reference
description: Plugin configuration, hooks, MCP servers, naming, and plugin structure
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

`mcp-config.json` configures MCP server connections for the ADK plugin. Some skills use MCP servers for source-native operations. Most skills work without any MCP.

| MCP Server | Used By | Transport |
| ---------- | ------- | --------- |
| GitHub | code-review-pr, code-review-fix, publish | HTTP (`https://api.githubcopilot.com/mcp/`) |
| Bitbucket | code-review-pr, code-review-fix | detect-from-input |
| Confluence | docs-review, publish, docs-write | detect-from-input |
| Google Drive | docs-review, docs-write | detect-from-input |

Additional MCP servers can be configured via `/adk:setup`.

For manual configuration, each agent stores MCP config in a different location:

| Agent | User-Scope Config | Project-Scope Config |
|-------|-------------------|----------------------|
| Claude Code | `~/.claude.json` | `.mcp.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` | — |
| OpenAI Codex | `~/.codex/config.toml` | `.codex/config.toml` |
| Cursor | `~/.cursor/mcp.json` | `.cursor/mcp.json` |

See the [Prerequisites — Manual MCP Configuration](/guide/prerequisites/#manual-mcp-configuration) guide for full setup instructions per agent.

## Hooks

`hooks/hooks.json` configures lifecycle hooks that run automatically:

| Event | Matcher | Type | Purpose |
|-------|---------|------|---------|
| `PostToolUse` | `Edit\|Write` | prompt | Validates SKILL.md frontmatter conventions |
| `Stop` | — | prompt | Checks task completion before ending |
| `SessionStart` | `compact` | command | Re-injects ADK context after compaction |

## Naming Convention

| Install Method | Invocation Pattern | Example |
| -------------- | ------------------ | ------- |
| Claude Plugin | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh | `/<skill-name>` | `/code-review-pr` |
| Local plugin-dir | `/adk:<skill-name>` | `/adk:code-review-pr` |

The `name` field in each skill's frontmatter is set to `<skill-name>`. When installed as a Claude plugin, the plugin namespace `adk:` is used and the folder name determines the command. When installed via skills.sh, the `name` field is used directly, giving `/<skill-name>`.

## Skill Frontmatter

Each skill's `SKILL.md` uses YAML frontmatter:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | `<skill-name>` for dual-install support |
| `description` | Yes | Starts with `adk -` followed by bracket tags |
| `user-invocable` | No | `true` (default) or `false` for helper skills |
| `argument-hint` | No | Parameter hint for autocomplete |
| `allowed-tools` | No | Tools the skill can use without asking |
| `workflow-tier` | Yes | `full`, `abbreviated`, `helper`, or `orchestrator` |
| `dependencies` | No | Required commands, npm packages, MCP servers |

## Plugin Structure

```
agents-devkit/                        52 skills · 18 agents · ~42K lines
├── .claude-plugin/
│   └── plugin.json                   Plugin manifest (name: adk)
├── mcp-config.json                   MCP server configurations
├── hooks/hooks.json                  Hook configurations
├── settings.json                     Default settings (routes to /adk:use)
├── agents/                           18 shared agent definitions
├── settings/                         MCP setup guides
├── templates/skill/                  Canonical templates and propagation
│   ├── common/                       Cross-skill files (help-format, project-guidelines)
│   └── scripts/                      Preflight and propagation scripts
├── skills/                           52 skills (only relevant ones load per task)
│   ├── use/                          Routing — default orchestrator
│   ├── code-review/                  Routing — review type detection
│   ├── docs/                         Routing — documentation task routing
│   ├── dev/                          Routing — development task routing
│   ├── diagram/                      Routing — diagram engine detection
│   │
│   ├── workflow/                     Guideline — 6-phase workflow (lazy-loaded)
│   ├── communication/                Guideline — concise-by-default output rules
│   ├── coding/                       Guideline — 16 coding guideline files (lazy-loaded by stack)
│   ├── docs-guidelines/              Guideline — 24 doc guideline files (lazy-loaded by type)
│   ├── (+ 12 more guideline skills)
│   │
│   ├── github/                       Connector — GitHub via gh CLI
│   ├── bitbucket/                    Connector — Bitbucket via API
│   ├── confluence/                   Connector — Confluence via API
│   ├── jira/                         Connector — Jira via API
│   │
│   ├── code-review-pr/              Task — PR review (11 conditional stages)
│   ├── dev-build/                    Task — implement/debug/TDD (7 conditional stages)
│   ├── docs-write/                   Task — formal docs (16 conditional stages)
│   ├── team/                         Task — multi-model agent dispatch
│   ├── (+ 26 more task skills)
├── manifest.json                     Upstream source tracking
└── docs/                             Documentation site (@pagesmith/docs)
```

## Upstream Dependencies

`manifest.json` tracks upstream sources:

| Source | Type | Skills |
|--------|------|--------|
| diagramkit | copy | diagram-mermaid, diagram-excalidraw, diagram-graphviz, diagram-drawio |
| superpowers | ref | develop, plan, review-pr |
| pagesmith | ref | write, docs-repo, docs-review, docs-crud, markdown |

Use `/adk:deps-tracker` to check for updates and sync changes.
