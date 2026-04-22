---
title: 'Config'
description: 'Plugin manifest, hooks, MCP servers, monitors, and bin scripts shipped with the adk plugin.'
---

# Config

Every configuration surface and CLI script shipped with the `adk` plugin gets one page here.

## Sections

- **Plugin** — `plugin-manifest`, `settings`, `pagesmith-config`
- **Hooks** — `hooks` (PreToolUse, PostToolUse, Stop, SessionStart)
- **Bin** — CLI scripts in `bin/`
- **MCP** — bundled MCP server registry from `.mcp.json`
- **Monitors** — long-running watchers from `monitors/monitors.json`

## Source

Mixed: `.claude-plugin/plugin.json`, `hooks/hooks.json`, `.mcp.json`, `monitors/monitors.json`, `bin/*`, `pagesmith.config.json5`, `settings.json`.
