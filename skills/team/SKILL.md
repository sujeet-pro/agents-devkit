---
name: team
description: "adk - [full] [team] Use when dispatching multi-model tasks or coordinating agent teams"
user-invocable: true
argument-hint: "<task> [--mode multi|team] [--models ...] [--roles ...] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: complex-build
---

# Team

Run tasks through multiple models for comparison/consensus, or dispatch a team of specialized agents working in parallel. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family complex-build` | always | Complex Build workflow: confirm → research → select approach → plan → execute → validate. Full human-in-the-loop for architectural decisions. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `multi`, `team` | auto-detect | Force a specific agent orchestration mode |
| `--models` | comma-separated model names | `opus,sonnet` | In multi mode, which models to run the task through |
| `--strategy` | `merge`, `vote`, `best-of` | `merge` | In multi mode, how to combine results |
| `--timeout` | `<seconds>` | none | Maximum time to wait for child agents |
| `--roles` | comma-separated role names | none | In team mode, custom roles for agents |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode multi`**: Uses Quick Action workflow. Runs the same task through multiple models in parallel and merges results with a consensus pass.
- **`--mode team`**: Uses Quick Action workflow. Dispatches specialized agents with distinct roles to work on independent sub-tasks in parallel.

### Examples

```
/adk:team compare how opus and sonnet handle this refactoring task
/adk:team --mode multi --models opus,sonnet,haiku review this authentication flow
/adk:team --mode multi --strategy vote which approach is better for caching
/adk:team --mode team fix all 6 failing tests across 3 files
/adk:team --mode team --roles "api-designer,db-modeler,test-writer" design the user service
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:

| Signal | Mode | Stage File |
|---|---|---|
| Compare models, consensus, multi-model, `--models` flag | multi | `stages/multi.md` |
| Team, roles, parallel agents, delegation, `--roles` flag, independent tasks | team | `stages/team.md` |

### Disambiguation

When the intent is ambiguous, ask:

```text
Which agent orchestration mode?

[M] Multi-model -- run the same task through multiple models for comparison/consensus
[T] Team -- dispatch specialized agents with distinct roles for parallel work
```

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

This skill uses the Complex Build workflow: confirm → research → select approach → plan → execute → validate.

### 1. Confirm

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### 2. Research

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### 3. Select Approach

Both multi and team modes usually skip this phase after intent confirmation unless the user needs to choose a strategy.

### 4. Plan

Both multi and team modes usually skip this phase after approval unless coordination needs an explicit task split.

### 5. Execute

Follow the stage file's execution instructions.

### 6. Validate

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "3 agents dispatched, all completed, results merged")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus full child agent outputs, disagreement analysis, and confidence scoring

## Adjacent Skills

- `/adk:dev-build` -- feature implementation that may use agent teams internally
- `/adk:code-review-pr` -- code review that may use multi-model comparison
- `/adk:project` -- project initialization uses parallel research agents
