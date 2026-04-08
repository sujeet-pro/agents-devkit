---
title: "use"
description: Default DevKit entry point — expands intent, identifies skills, confirms plan, executes
skill_name: use
category: orchestrator
workflow_tier: orchestrator
---

# use

The default entry point for ADK. Routes any prompt through intent expansion, skill identification, plan confirmation, and execution.

## When to Use

Use `/adk:use` when you're not sure which skill to invoke. It analyzes your request, identifies the right skills, and confirms a plan before executing.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<task>` | free text | (required) | Description of what you want to do |
| `--auto` | flag | off | Skip all confirmations, execute the full workflow |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters and usage |

## Workflow

Uses the full 6-phase workflow with complexity-adaptive skipping:

| Phase | Action |
|-------|--------|
| 0. Intent Expansion | Restate goal, surface assumptions, estimate complexity |
| 1. Research | Check installed skills, match to request |
| 2. Approach Selection | Present skill pipeline, user picks or adjusts |
| 3. Planning | Break into tasks, assign to skills |
| 4. Execute | Run the selected skills |
| 5. Validate | Verify results, self-review |

### Complexity Routing

| Complexity | Phases Run | Example |
|------------|-----------|---------|
| Trivial | 0 → 4 | "what's the git status?" |
| Small | 0 → 1 → 4 → 5 | "rename this variable" |
| Medium | 0 → 1 → 2 → 4 → 5 | "review this PR" |
| Large | All 6 phases | "implement auth with OAuth2" |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams` (medium+), `interaction` (unless `--auto`).

## Examples

```text
/adk:use review this PR for security issues
/adk:use implement user authentication
/adk:use --auto create a diagram of the system architecture
/adk:use write documentation for the API
```
