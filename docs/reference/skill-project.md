---
title: 'project'
description: 'Use when initializing projects, managing milestones, or capturing ideas'
skill_name: project
category: task
workflow_tier: full
user_invocable: true
---

# project

Use `project` when initializing projects, managing milestones, or capturing ideas. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`project` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter     | Values                          | Default     | Description                                                                                                                                    |
| ------------- | ------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `--mode`      | `init`, `milestone`, `idea`     | auto-detect | Force a specific project mode                                                                                                                  |
| `--action`    | varies by mode                  | none        | Sub-action within a mode (e.g., `create`, `track`, `audit`, `complete`, `gaps` for milestone; `capture`, `review`, `promote`, `list` for idea) |
| `--type`      | `<project-type>`                | none        | In init mode, narrow research to a specific project type                                                                                       |
| `--milestone` | `<milestone-id>`                | none        | In milestone mode, target a specific milestone                                                                                                 |
| `--idea`      | `<description>`                 | none        | In idea mode, the idea text to capture                                                                                                         |
| `--verbosity` | `short`, `standard`, `detailed` | `standard`  | Output detail level                                                                                                                            |
| `--help`      | flag                            | off         | Show this help section                                                                                                                         |

### Parameter Notes

- `--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.


| Skill                     | Load When                                     | Inline Fallback                                                                                                                                                 |
| ------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication`      | always                                        | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context.                                              |
| `/adk:preflight-check`    | before work                                   | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP.                                                         |
| `/adk:output-format`      | when producing output                         | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question.                                                |
| `/adk:principal-engineer` | complexity >= medium                          | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months?                                                                           |
| `/adk:agentic-teams`      | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning.                               |
| `/adk:interaction`        | NOT --auto                                    | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard.                                               |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

### Common Phases

This skill uses the Standard Task workflow: confirm → research → execute → validate.

### 1. Confirm

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### 2. Research

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### 3. Execute

Follow the stage file's execution instructions.

### 4. Validate

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- `**--mode init**`: Uses Standard Task workflow for bootstrapping a new project. Interactive discovery, parallel research, requirements extraction, constitution, and roadmap generation.
- `**--mode milestone**`: Uses Standard Task workflow for creating, tracking, auditing, and archiving development milestones. Supports `--action create|track|audit|complete|gaps`.
- `**--mode idea**`: Uses Quick Action workflow (confirm → execute → verify) for this mode. Captures ideas to a backlog parking lot, reviews/triages accumulated ideas, or promotes ideas to specs/plans.

### Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from the task description:


| Signal                                                                      | Mode      | Stage File            |
| --------------------------------------------------------------------------- | --------- | --------------------- |
| New project, bootstrap, scaffold, setup, initialize, kickoff                | init      | `stages/init.md`      |
| Milestones, roadmap, progress, tracking, audit, archive, definition of done | milestone | `stages/milestone.md` |
| Ideas, backlog, parking lot, capture, promote, defer, triage                | idea      | `stages/idea.md`      |


### Disambiguation

When the intent is ambiguous, present the options:

```text
Which project action?

[1] Initialize a new project (--mode init)
    Bootstrap from idea through discovery, research, and roadmap.

[2] Manage milestones (--mode milestone)
    Create, track, audit, or archive roadmap milestones.

[3] Capture an idea (--mode idea)
    Park an idea for later, review the backlog, or promote items.
```

After selecting the mode, load the corresponding stage file and follow its instructions.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Status line only (e.g., "Project initialized at .temp/project-init/")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus research notes, decision rationale, and all child agent outputs

## Related Skills

### Adjacent Skills

- `/adk:spec --mode write` -- detailed feature specifications from roadmap phases
- `/adk:plan --mode write` -- execution planning per roadmap phase
- `/adk:code-review-pr` -- code review after development
- `/adk:dev-build` -- feature implementation from project plans

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:project
/adk:project bootstrap a new CLI tool for managing dotfiles
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:project --mode init a SaaS dashboard for analytics
/adk:project --mode milestone --action create v1.0 release
/adk:project --mode milestone --action track
/adk:project --mode milestone --action audit v1.0
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:project --verbosity detailed
```
