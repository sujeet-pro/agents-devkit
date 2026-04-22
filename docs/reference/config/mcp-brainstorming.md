---
title: 'mcp-brainstorming'
description: 'Optional brainstorming session store. plan-brainstorm prefers it when present, falls back to manual workflow.'
artifact_kind: mcp
---

# mcp-brainstorming

Optional brainstorming session store. plan-brainstorm prefers it when present, falls back to manual workflow.

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each `${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "brainstorming": {
    "command": "npx",
    "args": [
      "-y",
      "@buildermethods/brainstorming-mcp"
    ],
    "description": "Optional brainstorming session store. plan-brainstorm prefers it when present, falls back to manual workflow."
  }
}
```

## Required environment variables

None — this server runs with no env vars.

## Source

`.mcp.json` (entry: `brainstorming`).
