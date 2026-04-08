---
title: "team"
description: Multi-model comparison and specialized agent team dispatch
skill_name: team
category: task
workflow_tier: full
---

# team

Dispatches work across multiple models (for comparison/consensus) or coordinates specialized agent teams with distinct roles.

## When to Use

- Compare outputs across different AI models
- Run consensus-based decisions
- Coordinate a team of specialized agents

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `multi`, `team` | auto-detect | Operation mode |
| `--models` | model list | — | Models to use (for multi mode) |
| `--strategy` | `merge`, `vote`, `best-of` | `merge` | How to combine multi-model outputs |
| `--timeout` | seconds | — | Max time per agent |
| `--roles` | comma-separated | — | Agent roles (for team mode) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Modes

| Mode | Purpose | Strategy |
|------|---------|----------|
| `multi` | Same task, multiple models | `merge` (combine), `vote` (majority), `best-of` (pick best) |
| `team` | Different roles, one task | Parallel specialists with merged output |

## Workflow

Abbreviated — phases 2–5 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Detect mode, confirm task |
| 1. Research | Identify appropriate models/roles |
| 4. Execute | Launch parallel agents, collect outputs |
| 5. Validate | Merge/vote/select results |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams`, `interaction`.

## Examples

```text
/adk:team --mode multi --strategy merge "review this authentication implementation"
/adk:team --mode multi --strategy vote "which caching strategy is best?"
/adk:team --mode multi --strategy best-of "write unit tests for payment module"
/adk:team --mode team --roles "security-reviewer,performance-analyst" review API design
```
