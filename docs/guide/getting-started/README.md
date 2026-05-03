---
title: Getting Started
description: Install the adk marketplace and run the first setup pass.
order: 2
---

# Getting Started

Start with the general [Philosophy](../philosophy.md) when you want the why
behind the workflow. Use [Installation](./installation.md) for the full Claude
marketplace install, update, and uninstall paths.

## Fast Path In Claude Code

Register the marketplace and install the plugins you need:

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk-core@adk
/plugin install adk-code@adk
/plugin install adk-review@adk
/plugin install adk-docs@adk
/plugin install adk-investigate@adk
/reload-plugins
```

Then run setup:

```text
/adk-core:setup
```

`adk-core:setup` checks CLI dependencies, meta-info files under `~/.config/adk/`, and environment variables referenced by shipped MCP configs.

## Claude Desktop

Claude Desktop does not load a plugin's `.mcp.json` file. Install the same plugins, then configure any required custom connector or workspace connector in Desktop before running a skill that needs it.

The skills will stop in Phase 1 if a required connector is missing and will tell you what to configure. You can skip a check when you know that capability is not needed for the selected mode, such as a dry-run review that drafts findings but does not post comments.

## Validate Locally

For repository contributors:

```bash
npm install
npm run validate
npm run docs:build
```

## Next

- [Installation](./installation.md)
- [Claude Code and Desktop](../usage/desktop-and-cli.md)
- [Reference](../../reference/)
