---
name: spec
description: "adk - [full] [spec] Use when analyzing specs, writing specifications, generating checklists, or writing constitutions"
user-invocable: true
argument-hint: "<topic> [--mode analyze|write|checklist|constitution] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: standard-task
---

# Specification

Unified specification skill: writes feature specs, analyzes cross-artifact consistency, generates requirements quality checklists, and creates project constitutions. Auto-detects the right mode from context, or accepts an explicit `--mode`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
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
| `--mode` | `analyze`, `write`, `checklist`, `constitution` | auto-detect | Force a specific specification mode |
| `--spec` | `<path>` | none | Path to existing spec. Without `--mode`: implies analyze. With `--mode write`: uses the spec as input context for the new spec. With `--mode checklist`: validates the given spec. |
| `--depth` | `quick`, `standard`, `thorough` | `standard` | Analysis/checklist depth level |
| `--action` | `create`, `update`, `audit` | auto-detect | Constitution action type |
| `--scope` | `<path>` | none | Limit analysis to specific sections or files |
| `--format` | `markdown`, `google-doc`, `confluence` | `markdown` | Output format for constitution |
| `--interactive` | `interactive`, `auto-approve` | `interactive` | Review mode for interactive sections |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`--mode analyze`**: Read-only cross-artifact consistency analysis. Detects issues across specs, plans, tasks, and implementation. Runs child agents in parallel for completeness, consistency, constitution compliance, and gap detection.
- **`--mode write`**: Interactive feature specification creation. Captures requirements through clarification questions, launches domain experts plus `/adk:research` and `/adk:code-review-pr` child agents, produces spec with user stories, acceptance criteria, and edge cases.
- **`--mode checklist`**: Requirements quality validation. Generates "unit tests for English" that check completeness, clarity, and consistency. Produces traceable checklist with severity ratings and quality score.
- **`--mode constitution`**: Project governance document creation, update, or audit via `/adk:audit`. Creates versioned non-negotiable principles and quality gates that all downstream work must comply with.

### Examples

```
/adk:spec write a feature spec for user notifications
/adk:spec --mode analyze .temp/specs/notifications/
/adk:spec --mode checklist .temp/specs/notifications/spec.md
/adk:spec --mode constitution
/adk:spec --mode constitution --action update
/adk:spec --mode constitution --action audit
/adk:spec --spec .temp/specs/auth/spec.md
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Stage Selection

If `--mode` is explicitly provided, load the matching stage file directly. Otherwise, auto-detect the mode from context:

| Signal | Mode | Stage File |
|---|---|---|
| "analyze", "validate", "check consistency", "verify", references existing spec via `--spec` | analyze | `stages/analyze.md` |
| "write spec", "define requirements", "draft specification", "feature spec", default for new topics | write | `stages/write.md` |
| "checklist", "quality check", "validate requirements", "unit tests for English" | checklist | `stages/checklist.md` |
| "constitution", "governance", "principles", "quality gates", "non-negotiable" | constitution | `stages/constitution.md` |

### Ambiguous Input

When invoked as `/adk:spec` with no qualifying action:

1. If the user references an **existing** spec or document -> analyze mode
2. Otherwise -> write mode

After selecting the mode, load the corresponding stage file and follow its instructions.

## Common Phases

This skill uses the Standard Task workflow: confirm → research → execute → validate.

### 1. Confirm

Follow the stage file's intent confirmation guidance. Always run this phase before taking action.

### 2. Research

Follow the stage file's exploration guidance. Every mode uses this phase, though simpler modes may keep it brief.

### 3. Execute

Follow the stage file's execution instructions.

### 4. Validate

Follow the stage file's validation criteria. End with a concise summary of what changed, what was verified, and what the user should know.

## Output Format

Use the output format defined in the loaded stage file. Adapt verbosity based on `--verbosity`:

- **short**: Summary line only (e.g., "Spec written to .temp/specs/notifications/spec.md")
- **standard**: Full structured output from the stage file's Output Format section
- **detailed**: Standard output plus all child agent findings, decision rationale, and traceability matrices

## Adjacent Skills

- `/adk:plan` -- create implementation plans from specifications
- `/adk:dev-build` -- implement code from plans
- `/adk:code-review-pr` -- code review against specifications
