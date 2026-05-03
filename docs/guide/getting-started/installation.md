---
title: Installation
description: Install the adk Claude marketplace and enable the plugins in Claude Code.
order: 1
---

# Installation

`adk` is distributed as a Claude Code plugin marketplace. The marketplace
manifest lives at `.claude-plugin/marketplace.json` and exposes five plugins:
`adk-core`, `adk-code`, `adk-review`, `adk-docs`, and `adk-investigate`.

## Requirements

- Claude Code with plugin support.
- `gh`, `jq`, `fd`, `rg`, `node`, and Docker if you use the GitHub MCP.
- Env vars for shipped MCPs when needed: `GITHUB_PAT`, `DD_API_KEY`,
  `DD_APP_KEY`, and `STATSIG_CONSOLE_API_KEY`.
- Workspace connectors enabled for Atlassian, Google Drive, Gmail, Google
  Calendar, Slack, Mixpanel, and Snowflake if you plan to use dependent skills.

## Path A — Local Clone

Use this when you want to inspect or edit the marketplace locally.

```bash
git clone git@github.com:sujeet-pro/agents-devkit.git ~/code/claude-marketplace
```

Inside Claude Code:

```text
/plugin marketplace add ~/code/claude-marketplace
```

To refresh later:

```bash
cd ~/code/claude-marketplace
git pull
```

```text
/plugin marketplace update adk
/reload-plugins
```

## Path B — GitHub Marketplace Source

Use this when you want Claude Code to manage the marketplace cache directly.

```text
/plugin marketplace add sujeet-pro/agents-devkit
```

SSH and explicit HTTPS work too:

```text
/plugin marketplace add git@github.com:sujeet-pro/agents-devkit.git
/plugin marketplace add https://github.com/sujeet-pro/agents-devkit.git
```

For private forks or non-interactive environments, authenticate first with
`gh auth login` or export `GITHUB_TOKEN` / `GH_TOKEN`.

## Install Plugins

Install the full set for the complete Principal Engineer workflow:

```text
/plugin install adk-core@adk
/plugin install adk-code@adk
/plugin install adk-review@adk
/plugin install adk-docs@adk
/plugin install adk-investigate@adk
/reload-plugins
```

`adk-core` is a dependency of every other plugin, so Claude Code can install it
automatically when you install another `adk-*` plugin.

## Bootstrap Configuration

Run setup once after installing:

```text
/adk-core:setup
```

Setup scaffolds `~/.config/adk/*.md`, checks CLI dependencies, and reports
missing env vars referenced by plugin-local `.mcp.json` files.

For one topic:

```text
/adk-core:setup --target datadog
```

## Verify

```text
/adk-core:setup --auto
```

This runs the health checks and reports missing workspace connectors, shipped
MCPs, or env vars. Repository contributors should also run:

```bash
npm run validate
npm run docs:build
```

## Uninstall

```text
/plugin uninstall adk-code@adk
/plugin uninstall adk-review@adk
/plugin uninstall adk-docs@adk
/plugin uninstall adk-investigate@adk
/plugin uninstall adk-core@adk
/plugin marketplace remove adk
```

## Next

- [Getting Started](./README.md)
- [Claude Code and Desktop](../usage/desktop-and-cli.md)
- [SETUP.md](../../../SETUP.md)
