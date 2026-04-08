---
title: Setup & Configuration
description: Install tools, configure MCP servers, and verify your ADK installation
order: 8
---

# Setup & Configuration

The `setup` skill installs CLI tools, configures MCP servers, and sets up hooks and configuration for ADK skills. It's **idempotent** — run it as many times as you want. It only installs what's missing and syncs tokens that have changed.

> **First time?** Complete the [Prerequisites](/guide/prerequisites/) guide first for API tokens and Homebrew setup.

## Scenarios

- [Full setup](#full-setup)
- [Install CLI tools only](#install-cli-tools-only)
- [Configure MCP servers only](#configure-mcp-servers-only)
- [Check status without changes](#check-status-without-changes)
- [Install a specific tool](#install-a-specific-tool)
- [Configure a specific MCP server](#configure-a-specific-mcp-server)
- [Set up hooks and config](#set-up-hooks-and-config)

---

## Full Setup

Install everything — CLI tools, MCP servers, hooks, and config:

```text
/adk:setup
/adk:setup --type all
```

This checks for and installs:

| Category | Tools |
|----------|-------|
| **CLI tools** | git, python3, node, npm, jq, curl, gh, graphviz, uv, diagramkit, pagesmith |
| **MCP servers** | GitHub, Bitbucket, Confluence, Google Drive (using tokens from `~/.zshenv`) |
| **Config** | Default agent configuration, skill routing prompt in `CLAUDE.md` |

---

## Install CLI Tools Only

```text
/adk:setup --type tools
```

This installs missing CLI tools via Homebrew (macOS) or equivalent package managers.

---

## Configure MCP Servers Only

```text
/adk:setup --type mcps
```

Reads API tokens from `~/.zshenv` and configures MCP servers for GitHub, Bitbucket, Confluence, and Google Drive.

---

## Check Status Without Changes

See what's installed and what's missing without making any changes:

```text
/adk:setup --check-only
```

---

## Install a Specific Tool

```text
/adk:setup --tool gh              # Install/verify GitHub CLI
/adk:setup --tool diagramkit      # Install/verify diagramkit
/adk:setup --tool pagesmith       # Install/verify pagesmith
```

---

## Configure a Specific MCP Server

```text
/adk:setup --server github        # Configure GitHub MCP
/adk:setup --server confluence    # Configure Confluence MCP
/adk:setup --server bitbucket     # Configure Bitbucket MCP
```

---

## Set Up Hooks and Config

```text
/adk:setup --type hooks           # Set up git hooks
/adk:setup --type config          # Set up default configuration
```

### Skip update check

When running setup, skip checking for ADK updates:

```text
/adk:setup --skip-update
```

---

## Required API Tokens

Setup reads tokens from `~/.zshenv`. Set these environment variables before running setup:

| Token | Variable | Required For |
|-------|----------|-------------|
| GitHub | `GITHUB_TOKEN` | GitHub MCP, `gh` CLI |
| Bitbucket | `BITBUCKET_TOKEN` | Bitbucket MCP |
| Confluence | `CONFLUENCE_TOKEN` + `CONFLUENCE_URL` | Confluence MCP |

See [Prerequisites — API Tokens](/guide/prerequisites/#step-2-api-tokens) for generation instructions.

---

## Which Parameters to Use?

| Scenario | Parameters |
|----------|-----------|
| First-time full setup | `--type all` or no args |
| Verify installation | `--check-only` |
| Add a single tool | `--tool <name>` |
| Configure one MCP server | `--server <name>` |
| CLI tools only | `--type tools` |
| MCP servers only | `--type mcps` |
| Skip update check | `--skip-update` |

## Related Skills

- **[Prerequisites guide](/guide/prerequisites/)** — required tokens and Homebrew setup
- **[`preflight-check`](/reference/skills/preflight-check/)** — per-task tool validation (auto-invoked)
