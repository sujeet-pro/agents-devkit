---
title: 'plan'
description: 'Use when brainstorming, approving, executing, or tracking implementation plans with explicit human checkpoints before execution'
skill_name: plan
category: task
workflow_tier: full
user_invocable: true
---

# plan

Use `plan` to brainstorming, approving, executing, or tracking implementation plans with explicit human checkpoints before execution. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`plan` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `brainstorm`, `write`, `execute`, `track` | auto-detect | Force a specific planning mode |
| `--spec` | `<path>` | none | Load a specification file as input |
| `--plan` | `<path>` | none | Load an existing plan file as input |
| `--format` | `<format>` | markdown | Output format for tracking |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Parameter Notes

- `--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

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

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

### Common Phases

This skill uses the Complex Build workflow: confirm → research → select approach → plan → execute → validate.

### 1. Confirm

Always run this phase.

- restate the goal
- surface assumptions and ambiguities
- identify needed skills, tools, and MCPs
- estimate complexity
- run a PE check for Medium and Large work
- use `adk-intent-analyst` when the prompt is complex or underspecified

### 2. Research

Used by `brainstorm` and `write`.

- inspect existing code, docs, and constraints
- gather external guidance when needed
- produce 2-3 viable options

### 3. Select Approach

Used by `brainstorm` and `write`.

- let the user choose, mix, or simplify
- prefer one question at a time
- do not proceed until the direction is explicit

### 4. Plan

- `brainstorm`: produce an approved design direction and hand off to `write`
- `write`: produce the executable plan, review it with `adk-plan-reviewer` when needed, and get approval
- `execute`: validate that an approved plan exists and is still current
- `track`: read the plan and current progress state

### 5. Execute

Only `execute` performs implementation work.

### 6. Validate

All modes end with:

- plan quality check
- validation of completed work or current status
- a concise note explaining what the user should understand next
- for active execution or tracking, use `adk-progress-tracker` when the work is large enough to need live recovery guidance

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **`--mode brainstorm`**: collaborative idea shaping; expands intent, researches options, challenges assumptions, and ends with an approved direction
- **`--mode write`**: turns the approved direction into a concrete implementation plan with files, sequencing, and verification
- **`--mode execute`**: executes an already approved plan; do not start if the plan is missing or still unapproved
- **`--mode track`**: summarizes plan progress, blockers, and likely next moves

### Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect:

| Signal | Mode | Stage File |
|---|---|---|
| rough idea, “brainstorm”, “explore”, “what if”, vague request | brainstorm | `stages/brainstorm.md` |
| spec exists, requirements are known, “write a plan”, “plan for” | write | `stages/write.md` |
| plan file exists, “execute”, “implement the plan”, “carry this out” | execute | `stages/execute.md` |
| “track”, “status”, “progress”, “dashboard”, “what’s left” | track | `stages/track.md` |

### Auto-Detect Rules

1. If `--plan` is present, prefer `execute` or `track`.
2. If `--spec` is present, prefer `write`.
3. If the request is exploratory, prefer `brainstorm`.
4. If there is no plan yet and the user wants implementation, prefer `write` before `execute`.

The lifecycle is: `brainstorm -> write -> execute -> track`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

- **short**: one-line status
- **standard**: summary, decisions, plan status, next step
- **detailed**: standard output plus rationale, options considered, and artifact paths

## Related Skills

### Adjacent Skills

- `/adk:spec` — formal requirements before planning
- `/adk:dev-build` — implementation after planning
- `/adk:code-review-pr` — review after development
- `/adk:handoff` — pause or resume long planning sessions

## Additional Reference

### Hard Gates

1. `brainstorm` must not jump straight into implementation.
2. `write` must not start execution on its own.
3. `execute` requires an approved plan.
4. For Medium and Large work, the user sees the approach and the plan before code changes begin.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:plan
/adk:plan brainstorm a notification system for the app
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:plan --mode write implement user authentication based on the spec
/adk:plan --mode execute .temp/plans/auth-plan.md
/adk:plan --mode track
/adk:plan --plan .temp/plans/auth-plan.md --mode track
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:plan --verbosity detailed
```
