---
title: "setup"
description: Install and configure CLI tools, MCP servers, and hooks for ADK
skill_name: setup
category: task
workflow_tier: abbreviated
---

# setup

Installs CLI tools, configures MCP servers, sets up hooks, and manages default agent configuration. Idempotent — safe to run repeatedly.

## When to Use

- First-time ADK setup
- Add a new tool or MCP server
- Verify installation status
- Update configuration after token changes

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `tools`, `mcps`, `hooks`, `config`, `all` | `all` | What to set up |
| `--check-only` | flag | off | Report status without making changes |
| `--tool` | tool name | — | Install/check a specific tool |
| `--server` | server name | — | Configure a specific MCP server |
| `--skip-update` | flag | off | Skip ADK update check |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

Abbreviated — phases 2–3 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Detect setup scope |
| 1. Research | Check current tool/MCP status |
| 4. Execute | Install missing tools, configure servers |
| 5. Validate | Verify all installations succeeded |

## Shared Skills

`workflow`, `communication`.

## Examples

```text
/adk:setup
/adk:setup --type tools
/adk:setup --type mcps
/adk:setup --tool gh
/adk:setup --server confluence
/adk:setup --check-only
```
