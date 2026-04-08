---
name: plan
description: "adk - [full] [plan] Use when brainstorming, approving, executing, or tracking implementation plans with explicit human checkpoints before execution"
user-invocable: true
argument-hint: "<task> [--mode brainstorm|write|execute|track] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: complex-build
---

# Planning

Unified planning skill for:

- shaping an idea into a concrete direction
- turning the chosen direction into an executable plan
- executing only approved plans
- tracking progress against a plan

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
| `--mode` | `brainstorm`, `write`, `execute`, `track` | auto-detect | Force a specific planning mode |
| `--spec` | `<path>` | none | Load a specification file as input |
| `--plan` | `<path>` | none | Load an existing plan file as input |
| `--format` | `<format>` | markdown | Output format for tracking |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode brainstorm`**: collaborative idea shaping; expands intent, researches options, challenges assumptions, and ends with an approved direction
- **`--mode write`**: turns the approved direction into a concrete implementation plan with files, sequencing, and verification
- **`--mode execute`**: executes an already approved plan; do not start if the plan is missing or still unapproved
- **`--mode track`**: summarizes plan progress, blockers, and likely next moves

### Examples

```text
/adk:plan brainstorm a notification system for the app
/adk:plan --mode write implement user authentication based on the spec
/adk:plan --mode execute .temp/plans/auth-plan.md
/adk:plan --mode track
/adk:plan --plan .temp/plans/auth-plan.md --mode track
```

## Hard Gates

1. `brainstorm` must not jump straight into implementation.
2. `write` must not start execution on its own.
3. `execute` requires an approved plan.
4. For Medium and Large work, the user sees the approach and the plan before code changes begin.

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

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

## Common Phases

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

## Output Format

- **short**: one-line status
- **standard**: summary, decisions, plan status, next step
- **detailed**: standard output plus rationale, options considered, and artifact paths

## Adjacent Skills

- `/adk:spec` — formal requirements before planning
- `/adk:dev-build` — implementation after planning
- `/adk:code-review-pr` — review after development
- `/adk:handoff` — pause or resume long planning sessions
