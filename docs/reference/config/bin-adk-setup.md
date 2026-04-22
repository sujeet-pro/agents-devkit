---
title: 'adk-setup'
description: 'adk-setup'
artifact_kind: bin
---

# adk-setup

adk-setup

Macros for the `setup` skill. Verifies and installs required CLI tools via Homebrew,
checks env vars referenced by .mcp.json against ~/.zshenv, then delegates MCP install
to bin/adk-mcp-install.

macOS only.

Usage:
  bin/adk-setup                # interactive
  bin/adk-setup --auto         # install missing without asking; no MCP step
  bin/adk-setup --target cli   # only CLI tools; skip MCP
  bin/adk-setup --target mcp   # only MCP step; skip CLI
  bin/adk-setup --target all   # both (default)

## Usage

```bash
node bin/adk-setup
```

From an installed plugin the script is in `PATH`:

```bash
adk-setup
```

## Source

`bin/adk-setup` — Node.js CLI script.
