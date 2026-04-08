---
title: "project"
description: Initialize projects, manage milestones, and capture ideas
skill_name: project
category: task
workflow_tier: full
---

# project

Initializes projects, manages milestones, and maintains an idea backlog.

## When to Use

- Scaffold a new project with documentation and config
- Create and track project milestones
- Quick-capture ideas for later

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `init`, `milestone`, `idea` | auto-detect | Project mode |
| `--action` | mode-specific | — | Sub-action (e.g., `create`, `list`, `update`) |
| `--type` | `api`, `library`, `cli`, etc. | — | Project type (for init) |
| `--milestone` | milestone name | — | Target milestone |
| `--idea` | idea text | — | Idea description |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

Full 6-phase for `init` and `milestone`. Abbreviated for `idea`.

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`.

## Examples

```text
/adk:project --mode init
/adk:project --mode init --type api
/adk:project --mode milestone --action create "v1.0 Release"
/adk:project --mode milestone --action list
/adk:project --mode idea "add dark mode support"
```
