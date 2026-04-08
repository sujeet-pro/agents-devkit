---
title: "interactivity"
description: "Agent-first interaction orchestration for option selection, data capture, edits, and human approval"
skill_name: interactivity
category: task
workflow_tier: full
user_invocable: true
---

# interactivity

Centralized interaction orchestration skill for structured user interaction — choosing approaches, collecting constrained inputs, editing generated data, and approving findings. All interaction happens inline in the agent conversation. When no arguments are provided, the skill enters interactive mode and asks the user for each required parameter.

## Purpose

- Centralize all human-in-the-loop interaction patterns into one skill
- Keep interaction agent-first and discussion-heavy
- Ensure user-provided answers are revalidated before execution

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<goal>` | string | — | What the interaction should accomplish |
| `--mode` | `auto` \| `options` \| `collect` \| `edit` \| `review` | `auto` | Interaction flow type |
| `--form` | path | none | Path to a form definition file |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--auto` | flag | — | Skip confirmations, use recommended defaults |
| `--help` | flag | — | Show parameter reference and exit |

## Key Behaviors

### Interactive Parameter Collection

When no arguments or insufficient arguments are provided, the agent asks the user for each missing parameter. For every question, the agent presents numbered options with the recommended choice first (marked `[recommended]`), based on analysis of the prompt context.

### Interaction Modes

| Mode | Purpose | Output |
|------|---------|--------|
| `auto` | Infer best interaction flow from context | Approved plan + resolved answers |
| `options` | Present alternatives and capture choice/mix | Selected option set |
| `collect` | Gather missing required inputs | Normalized answer set |
| `edit` | User revises generated content or config | Edited artifact + delta |
| `review` | Triage findings/items (accept/reject/edit/skip) | Decision ledger |

### Inline Interaction Protocol

For each interaction round:

1. Show concise context and options
2. Ask for explicit user decision
3. Parse and normalize answer
4. Confirm interpreted answer
5. Revalidate for completeness/consistency
6. Continue or ask focused follow-up

Supports compact action grammar: `pick: 2`, `pick: 1,3`, `mix: 1 + 3 (instructions)`, `edit: <changes>`, `approve`, `cancel`.

### Output Contract

Every interaction produces:

1. Normalized answer object
2. Validation status
3. Unresolved questions (if any)
4. Approved decisions and constraints to carry into execution

## What It Provides

- Operational interaction workflow that goes beyond the protocol definitions in `/adk:interaction`
- Multiple interaction modes for different use cases (options, collection, editing, review)
- Agent-first inline conversation for all interaction
- Revalidation step before execution to catch contradictions

## Invoked By

| Skill | Relationship |
|-------|-------------|
| `use` | Routes tasks here when structured interaction is needed |
| `plan` | Uses decisions captured here for approved execution plans |
| `interaction` | Lightweight protocol reference; `interactivity` is the operational workflow skill |

## Examples

```
/adk:interactivity "choose deployment strategy" --mode options
/adk:interactivity "collect migration parameters" --mode collect
/adk:interactivity "review 25 audit findings" --mode review
/adk:interactivity --help
```
