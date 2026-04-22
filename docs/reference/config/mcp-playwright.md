---
title: 'mcp-playwright'
description: 'Playwright MCP — 3rd-priority fallback for validate-browser.'
artifact_kind: mcp
---

# mcp-playwright

Playwright MCP — 3rd-priority fallback for validate-browser. Use when neither chrome-devtools nor cursor-ide-browser is available.

## Usage

Install via `bin/adk-mcp-install`:

```bash
node bin/adk-mcp-install              # interactive picker
node bin/adk-mcp-install --auto       # enable every server with env vars present
```

The installer reads `.mcp.json`, resolves `${ENV_VAR}` placeholders from `~/.zshenv`, and registers the server with `claude mcp add`.

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

## Source

`.mcp.json` (entry: `playwright`).
