---
title: Setup & Configuration
description: Install tools, configure MCP servers, and verify your ADK installation
order: 8
---

# Setup & Configuration

Use `setup` when the important job is making the DevKit environment healthy: tools installed, MCP servers configured, hooks in place, and default routing set correctly.

> **Quick start:** `/adk:setup` performs the full setup path and is safe to re-run because the skill is idempotent.

## Scenarios

- [Run Full Setup](#run-full-setup)
- [Check Status Without Changing Anything](#check-status-without-changing-anything)
- [Install One Class Of Dependency](#install-one-class-of-dependency)
- [Target One Tool Or MCP Server](#target-one-tool-or-mcp-server)
- [Know Which Tokens Matter](#know-which-tokens-matter)

---

## Run Full Setup

Run the full setup when you want tools, MCPs, hooks, and routing defaults handled together.

```text
/adk:setup
/adk:setup --type tools
/adk:setup --type mcps
/adk:setup --type hooks
/adk:setup --type config
```

Use the type flag when you already know you only want one slice of the setup surface instead of the full pass.

---

## Check Status Without Changing Anything

Use check-only mode when you want an inventory first.

```text
/adk:setup --check-only
/adk:setup --skip-update
```

`--check-only` avoids changes entirely. `--skip-update` still installs missing items, but it will not upgrade anything that is already present.

---

## Install One Class Of Dependency

Sometimes the environment is mostly healthy and only one area needs work.

```text
/adk:setup --type tools
/adk:setup --type mcps
```

Tool setup is for CLI binaries like `gh`, `diagramkit`, and `pagesmith`. MCP setup is for platform connectivity such as GitHub, Bitbucket, Confluence, and Google Drive.

---

## Target One Tool Or MCP Server

When the issue is very specific, narrow the command to one target.

```text
/adk:setup --tool gh
/adk:setup --server github
/adk:setup --ide cursor
```

Use `--tool` for one CLI dependency, `--server` for one MCP definition, and `--ide` when the MCP configuration should be written for a specific AI client.

---

## Know Which Tokens Matter

The `setup` skill reads or syncs these environment variables from `~/.zshenv` when MCP configuration requires them:

| Integration | Variables |
|-------------|-----------|
| GitHub MCP | `GITHUB_PAT` |
| Bitbucket MCP | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence MCP | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive MCP | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

GitHub CLI authentication is still handled through `gh auth login`, but the GitHub MCP configuration path uses `GITHUB_PAT`.

---

## Which Parameters To Use?

| Scenario | Parameters |
|----------|-----------|
| Full setup | no flags, or `--type all` |
| Check health without changing anything | `--check-only` |
| Tools only | `--type tools` or `--tool <name>` |
| MCPs only | `--type mcps` or `--server <name>` |
| Target one IDE for MCP config | `--ide <name>` |
| Install missing but do not upgrade | `--skip-update` |

## Related Skills

- **[`preflight-check`](/reference/skill-preflight-check/)** for per-skill dependency validation at runtime.
- **[`project`](/reference/skill-project/)** when the next problem is bootstrapping project work rather than bootstrapping the environment.
