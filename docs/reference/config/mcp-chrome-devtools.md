---
title: 'mcp-chrome-devtools'
description: 'Anthropic''s Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser. Drives a real Chrome via the DevTools protocol. No env vars required (uses local Chrome install).'
artifact_kind: mcp
---

# mcp-chrome-devtools

Anthropic's Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser. Drives a real Chrome via the DevTools protocol. No env vars required (uses local Chrome install).

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": [
      "-y",
      "@anthropic/chrome-devtools-mcp"
    ],
    "description": "Anthropic's Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser. Drives a real Chrome via the DevTools protocol. No env vars required (uses local Chrome install)."
  }
}
```

## Required environment variables

None — this server runs with no env vars.

## Source

`.mcp.json` (entry: `chrome-devtools`).
