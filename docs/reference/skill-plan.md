---
title: "plan"
description: Brainstorm, write, execute, and track implementation plans with explicit human checkpoints
skill_name: plan
category: task
workflow_tier: full
user_invocable: true
---

# plan

Unified planning skill for shaping ideas into concrete directions, turning directions into executable plans, executing approved plans, and tracking progress. Supports four modes that follow a natural lifecycle: brainstorm → write → execute → track. Enforces hard gates between modes to prevent premature implementation.

## When to Use

- Brainstorm and shape a rough idea into a concrete direction
- Write a detailed implementation plan from requirements or a spec
- Execute an already-approved plan with tracked progress
- Check status, blockers, and next steps for an in-progress plan
- Collaborate on approach selection before committing to implementation

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | free-text description | required | The task or idea to plan around |
| `--mode` | `brainstorm` \| `write` \| `execute` \| `track` | auto-detect | Force a specific planning mode |
| `--spec` | file path | none | Load a specification file as input. Implies `write` mode |
| `--plan` | file path | none | Load an existing plan file as input. Implies `execute` or `track` mode |
| `--format` | format string | `markdown` | Output format for tracking |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`--mode brainstorm`** | Collaborative idea shaping; expands intent, researches options, challenges assumptions, ends with an approved direction |
| **`--mode write`** | Turns the approved direction into a concrete implementation plan with files, sequencing, and verification |
| **`--mode execute`** | Executes an already approved plan; refuses to start if the plan is missing or unapproved |
| **`--mode track`** | Summarizes plan progress, blockers, and likely next moves |
| **`--spec` provided** | Prefers `write` mode (spec implies known requirements ready for planning) |
| **`--plan` provided** | Prefers `execute` or `track` mode |
| **Rough idea, "what if"** | Auto-detects `brainstorm` mode |
| **"status" or "progress"** | Auto-detects `track` mode |

## Hard Gates

1. `brainstorm` must not jump straight into implementation
2. `write` must not start execution on its own
3. `execute` requires an approved plan
4. For Medium and Large work, the user sees the approach and the plan before code changes begin

## Key Behaviors

- **Lifecycle enforcement**: modes follow a strict progression — brainstorm → write → execute → track
- **Human-in-the-loop**: approach and plan require user approval before execution (unless `--auto`)
- **Principal Engineer check**: for Medium and Large work, challenges with 5 PE questions before committing
- **Plan review**: uses `adk-plan-reviewer` agent to validate plans before user approval
- **Progress tracking**: uses `adk-progress-tracker` agent for live recovery guidance during large executions
- **Intent analysis**: uses `adk-intent-analyst` agent when prompts are complex or underspecified

## Workflow

Follows the 6-phase workflow. Phase applicability varies by mode.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | all modes | Restate goal, surface assumptions, identify skills/tools, estimate complexity, PE check for medium+ |
| 1. Research & Options | brainstorm, write | Inspect existing code/docs/constraints, gather external guidance, produce 2-3 viable options |
| 2. Approach Selection | brainstorm, write | User chooses, mixes, or simplifies; one question at a time; no proceeding until direction is explicit |
| 3. Planning | all modes | brainstorm: produce approved direction; write: produce executable plan; execute: validate plan exists; track: read plan state |
| 4. Execute | execute only | Implementation work happens only in execute mode |
| 5. Validate & Learn | all modes | Plan quality check, validation, concise summary of what the user should understand next |

## Stage Selection

| Signal | Mode | Stage File |
|--------|------|------------|
| rough idea, "brainstorm", "explore", "what if", vague request | brainstorm | `stages/brainstorm.md` |
| spec exists, requirements known, "write a plan", "plan for" | write | `stages/write.md` |
| plan file exists, "execute", "implement the plan", "carry this out" | execute | `stages/execute.md` |
| "track", "status", "progress", "dashboard", "what's left" | track | `stages/track.md` |

### Auto-Detect Rules

1. If `--plan` is present, prefer `execute` or `track`
2. If `--spec` is present, prefer `write`
3. If the request is exploratory, prefer `brainstorm`
4. If there is no plan yet and the user wants implementation, prefer `write` before `execute`

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

- **short**: one-line status
- **standard**: summary, decisions, plan status, next step
- **detailed**: standard output plus rationale, options considered, and artifact paths

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:spec` | Formal requirements before planning |
| `/adk:dev-build` | Implementation after planning |
| `/adk:code-review-pr` | Review after development |
| `/adk:handoff` | Pause or resume long planning sessions |

## Examples

```
/adk:plan brainstorm a notification system for the app
/adk:plan --mode write implement user authentication based on the spec
/adk:plan --mode execute .temp/plans/auth-plan.md
/adk:plan --mode track
/adk:plan --plan .temp/plans/auth-plan.md --mode track
```
