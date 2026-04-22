---
title: 'adk-mcp-install'
description: 'adk-mcp-install'
artifact_kind: bin
---

# adk-mcp-install

adk-mcp-install

Read .mcp.json (the bundled MCP server registry), resolve ${ENV_VAR}
placeholders from ~/.zshenv, prompt the user for which servers to enable,
and run `claude mcp add ...` per accepted server.

Usage:
  bin/adk-mcp-install            # interactive picker
  bin/adk-mcp-install --auto     # enable every server whose env vars are present
  bin/adk-mcp-install --list     # just print which servers are registrable
  bin/adk-mcp-install --dry-run  # show commands that would run

## Usage

```bash
node bin/adk-mcp-install
```

From an installed plugin the script is in `PATH`:

```bash
adk-mcp-install
```

## Source

`bin/adk-mcp-install` — Node.js CLI script.
