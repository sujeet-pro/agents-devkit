---
title: 'mcp-cursor-ide-browser'
description: 'Cursor IDE''s bundled browser MCP — 2nd-priority backend for validate-browser when running inside Cursor (auto-injected).'
artifact_kind: mcp
---

# mcp-cursor-ide-browser

Cursor IDE's bundled browser MCP — 2nd-priority backend for validate-browser when running inside Cursor (auto-injected). No env vars required.

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

## Source

`.mcp.json` (entry: `cursor-ide-browser`).
