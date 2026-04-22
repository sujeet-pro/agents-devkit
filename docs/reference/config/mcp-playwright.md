---
title: 'mcp-playwright'
description: 'Playwright MCP — 3rd-priority fallback for validate-browser. Use when neither chrome-devtools nor cursor-ide-browser is available.'
artifact_kind: mcp
---

# mcp-playwright

Playwright MCP — 3rd-priority fallback for validate-browser. Use when neither chrome-devtools nor cursor-ide-browser is available.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "playwright": {
    "command": "npx",
    "args": [
      "-y",
      "@playwright/mcp"
    ],
    "description": "Playwright MCP — 3rd-priority fallback for validate-browser. Use when neither chrome-devtools nor cursor-ide-browser is available."
  }
}
```

## Required environment variables

None — this server runs with no env vars.

## Source

`.mcp.json` (entry: `playwright`).
