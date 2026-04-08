---
title: "team"
description: Multi-model comparison and specialized agent team dispatch for parallel work
skill_name: team
category: task
workflow_tier: full
user_invocable: true
---

# team

Run tasks through multiple models for comparison/consensus, or dispatch a team of specialized agents working in parallel. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## When to Use

- Compare how different models handle the same task
- Get consensus from multiple models on an approach or review
- Dispatch specialized agents with distinct roles to work in parallel
- Run independent sub-tasks across multiple agents simultaneously
- Coordinate multi-model peer review

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | free-text description | required | The task to run through models or agents |
| `--mode` | `multi` \| `team` | auto-detect | Force a specific agent orchestration mode |
| `--models` | comma-separated model names | `opus,sonnet` | In multi mode, which models to run the task through |
| `--strategy` | `merge` \| `vote` \| `best-of` | `merge` | In multi mode, how to combine results |
| `--timeout` | seconds | none | Maximum time to wait for child agents |
| `--roles` | comma-separated role names | none | In team mode, custom roles for agents |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`--mode multi`** | Abbreviated workflow. Runs the same task through multiple models in parallel and merges results with a consensus pass. Phases 2-3 skipped |
| **`--mode team`** | Abbreviated workflow. Dispatches specialized agents with distinct roles to work on independent sub-tasks in parallel. Phases 2-3 skipped |
| **`--models` flag present** | Auto-selects multi mode |
| **`--roles` flag present** | Auto-selects team mode |
| **`--strategy vote`** | In multi mode, agents vote on the best approach rather than merging |
| **`--strategy best-of`** | In multi mode, the best individual result is selected |

## Key Behaviors

- **Smart mode detection**: `--models` flag triggers multi mode, `--roles` flag triggers team mode, ambiguous prompts ask the user
- **Parallel execution**: all agents run concurrently regardless of mode
- **Consensus merging**: multi mode deduplicates findings, resolves contradictions, and assigns confidence scores
- **Role specialization**: team mode agents receive distinct role-specific instructions
- **Disambiguation prompt**: when intent is unclear, presents a clear choice between multi and team modes

## Workflow

Both modes use an abbreviated workflow (phases 0-1 for setup, then direct execution and validation).

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, detect mode, identify models/roles needed |
| 1. Research & Options | yes | Brief exploration; simpler modes keep this minimal |
| 2. Approach Selection | usually skipped | Only if user needs to choose a strategy |
| 3. Planning | usually skipped | Only if coordination needs explicit task split |
| 4. Execute | yes | Launch agents in parallel, collect results |
| 5. Validate & Learn | yes | Merge/compare results, summarize findings |

## Stage Selection

| Signal | Mode | Stage File |
|--------|------|------------|
| compare models, consensus, multi-model, `--models` flag | multi | `stages/multi.md` |
| team, roles, parallel agents, delegation, `--roles` flag, independent tasks | team | `stages/team.md` |

### Disambiguation

When the intent is ambiguous, the skill asks:

```text
Which agent orchestration mode?

[M] Multi-model — run the same task through multiple models for comparison/consensus
[T] Team — dispatch specialized agents with distinct roles for parallel work
```

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect dependencies, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown. Verbosity adapts to `--verbosity`:

- **short**: status line only (e.g., "3 agents dispatched, all completed, results merged")
- **standard**: full structured output from the stage file's Output Format section
- **detailed**: standard output plus full child agent outputs, disagreement analysis, and confidence scoring

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:dev-build` | Feature implementation that may use agent teams internally |
| `/adk:code-review-pr` | Code review that may use multi-model comparison |
| `/adk:project` | Project initialization that uses parallel research agents |

## Examples

```
/adk:team compare how opus and sonnet handle this refactoring task
/adk:team --mode multi --models opus,sonnet,haiku review this authentication flow
/adk:team --mode multi --strategy vote which approach is better for caching
/adk:team --mode team fix all 6 failing tests across 3 files
/adk:team --mode team --roles "api-designer,db-modeler,test-writer" design the user service
```
