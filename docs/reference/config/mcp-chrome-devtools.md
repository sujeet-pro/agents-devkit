---
title: 'mcp-chrome-devtools'
description: 'Anthropic''s Chrome DevTools MCP — preferred browser backend for validate-browser. Drives a real Chrome via the DevTools protocol; no env vars required.'
artifact_kind: mcp
---

# mcp-chrome-devtools

Anthropic's Chrome DevTools MCP for Claude Code — **preferred** browser backend for
[`validate-browser`](../skill-validate-browser.md) and `browser-testing-with-devtools`.
Drives a real Chrome via the DevTools protocol; exposes DOM inspection, console logs,
network traces, performance profiling, screenshot, and Lighthouse-style audits. No env vars
required (uses the local Chrome install).

## Usage

`.mcp.json` is loaded automatically by Claude Code when the `adk` plugin is enabled. Each
`${ENV_VAR}` placeholder is resolved from your shell env at session start. To inspect or
override entries, edit `.mcp.json` and reload the plugin (`/reload-plugins`).

## Configuration

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": [
      "-y",
      "@anthropic/chrome-devtools-mcp@latest"
    ],
    "description": "Anthropic's Chrome DevTools MCP for Claude Code — PREFERRED backend for validate-browser and browser-testing-with-devtools. Drives a real Chrome via the DevTools protocol; exposes DOM inspection, console logs, network traces, performance profiling, screenshot, and Lighthouse-style audits. No env vars required (uses local Chrome install). Always pinned to @latest so the local Chrome tooling stays current."
  }
}
```

> [!NOTE]
> The package is pinned to `@latest` so the local Chrome tooling stays current with each
> session start.

## Required environment variables

None — this server runs with no env vars.

## Source

`.mcp.json` (entry: `chrome-devtools`).
