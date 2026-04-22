---
title: 'mcp-chrome-devtools'
description: 'Anthropic''s Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser.'
artifact_kind: mcp
---

# mcp-chrome-devtools

Anthropic's Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser. Drives a real Chrome via the DevTools protocol. No env vars required (uses local Chrome install).

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

## Source

`.mcp.json` (entry: `chrome-devtools`).
