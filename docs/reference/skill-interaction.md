---
title: "interaction"
description: "Inline interaction protocols for intent confirmation, approach selection, plan approval, and review findings"
skill_name: interaction
category: guideline
workflow_tier: helper
user_invocable: false
---

# interaction

Inline interaction protocols that define how DevKit skills render structured prompts and process user replies. Since Claude Code's Bash tool does not provide an interactive TTY, all interactivity happens via the agent itself — rendering structured prompts and parsing compact user replies.

## Purpose

- Define reusable interaction patterns for human-in-the-loop workflows
- Standardize how skills confirm intent, present options, approve plans, and triage review findings
- Provide compact action grammars so users can respond efficiently
- Ensure consistent UX across all interactive DevKit skills

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-i` | flag | on | Inline interactivity — render interactions directly in the conversation |
| `--auto` | flag | off | Skip human confirmations and proceed with recommended defaults |

When neither flag is provided, default to `-i` (inline).

## Key Behaviors

### Five Interaction Protocols

#### 1. Intent Confirmation

Rendered during Phase 0 of the workflow. Presents the restated goal, reasoning, skills needed, tools/MCPs with availability, and complexity estimate.

User replies: `approve`, `edit: <changes>`, `simplify`, or `cancel`.

#### 2. Approach Selection

Rendered during Phase 1-2. Presents 2-3 numbered approaches with summary, risk level, effort estimate, pros, and cons. One approach is marked `[recommended]`.

User replies: `1`, `2`, `3`, `mix: <instructions>`, or `discuss`.

#### 3. Plan Approval

Rendered during Phase 3. Presents tasks grouped into parallel waves with effort estimates and affected files.

User replies: `approve`, `add: <task description>`, `remove: <number>`, or `cancel`. If the user modifies the plan, it re-renders and asks again.

#### 4. Review Findings

The most complex protocol. Renders a summary header with finding counts by severity, then each finding as a structured card with priority, title, file/line, principle, guideline, confidence score, issue explanation, and suggested fix.

User action grammar:
- `a-1,4,5` — accept findings 1, 4, 5
- `r-2,6` — reject findings 2, 6
- `e-3` — mark finding 3 for edit (triggers edit loop)
- `s-7` — skip/defer finding 7
- `a-all` — accept all remaining
- `details N` — show full body of finding N
- `done` — finalize (only if no pending items remain)

Edit loop: shows current finding body, asks for edit instructions, regenerates the finding, asks `accept` or `edit again`.

#### 5. Progress Dashboard

Display-only protocol for execution progress. Rendered inline at wave boundaries showing completion status per wave. No user interaction needed.

### Conditional Behavior

- When `--auto` is passed, all protocols are skipped — skills proceed with recommended defaults
- Review Findings only shows findings with confidence >= 80%
- Plan Approval re-renders after any user modification

## What It Provides

- Rendering templates for each of the five interaction protocols
- Compact action grammar that skills parse from user replies
- Edit loop workflow for iterating on individual review findings
- Post-review summary table (accepted/rejected/edited/skipped counts)
- Progress dashboard format for wave-based execution tracking

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | NOT `--auto` |
| `code-review-repo` | NOT `--auto` |
| `code-review-fix` | NOT `--auto` |
| `audit` | NOT `--auto` |
| `dev-build` | NOT `--auto` |
| `dev-refactor` | NOT `--auto` |
| `dev-migrate` | NOT `--auto` |
| `docs-write` | NOT `--auto` |
| `docs-review` | NOT `--auto` |
| `docs-repo` | NOT `--auto` |
| `docs-crud` | NOT `--auto` |
| `design` | NOT `--auto` |
| `plan` | NOT `--auto` |
| `spec` | NOT `--auto` |
| `research` | NOT `--auto` |
| `workflow` (Phases 0-3) | NOT `--auto` |
