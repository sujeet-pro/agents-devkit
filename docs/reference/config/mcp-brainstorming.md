---
title: 'mcp-brainstorming'
description: 'Optional brainstorming session store.'
artifact_kind: mcp
---

# mcp-brainstorming

Optional brainstorming session store. plan-brainstorm prefers it when present, falls back to manual workflow.

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

## Source

`.mcp.json` (entry: `brainstorming`).
