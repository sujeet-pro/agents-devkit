---
title: "deps-tracker"
description: Track upstream dependencies and sync updates for ADK skills
skill_name: deps-tracker
category: task
workflow_tier: full
---

# deps-tracker

Tracks upstream dependencies (diagramkit, pagesmith, superpowers) and syncs updates when referenced tools or libraries change.

## When to Use

- Check which ADK skills have upstream dependencies
- Sync skills after an upstream dependency updates
- Add or remove dependency tracking

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `status`, `sync`, `add`, `remove`, `check`, `docs-check` | (required) | Operation |
| `--source` | source identifier | — | Dependency source |
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Actions

| Action | Purpose | Modifies Files? |
|--------|---------|-----------------|
| `status` | Show dependency status | No |
| `check` | Check for upstream changes | No |
| `docs-check` | Check doc references are current | No |
| `sync` | Update skills to match upstream | Yes |
| `add` | Register a new dependency | Yes |
| `remove` | Unregister a dependency | Yes |

## Workflow

Full 6-phase for `sync`. Read-only actions skip the execute pipeline.

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`.

## Examples

```text
/adk:deps-tracker status
/adk:deps-tracker check
/adk:deps-tracker sync --auto
/adk:deps-tracker add --source diagramkit
/adk:deps-tracker docs-check
```
