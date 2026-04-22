---
title: 'mcp-cursor-ide-browser'
description: 'Cursor IDE''s bundled browser MCP — 2nd-priority backend for validate-browser when running inside Cursor (auto-injected). No env vars required.'
artifact_kind: mcp
---

# mcp-cursor-ide-browser

Cursor IDE's bundled browser MCP — 2nd-priority backend for validate-browser when running inside Cursor (auto-injected). No env vars required.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "cursor-ide-browser": {
    "command": "npx",
    "args": [
      "-y",
      "@cursor/ide-browser-mcp"
    ],
    "description": "Cursor IDE's bundled browser MCP — 2nd-priority backend for validate-browser when running inside Cursor (auto-injected). No env vars required."
  }
}
```

## Required environment variables

None — this server runs with no env vars.

## Source

`.mcp.json` (entry: `cursor-ide-browser`).
