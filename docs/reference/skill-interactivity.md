---
title: 'interactivity'
description: 'Agent-first interaction orchestration for option selection, data capture, edits, and human approval'
skill_name: interactivity
category: task
workflow_tier: full
user_invocable: true
---

# interactivity

Use `interactivity` to agent-first interaction orchestration for option selection, data capture, edits, and human approval. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`interactivity` belongs to the `task` layer and is declared at the `full` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

No parameter table is currently defined in `SKILL.md` for this skill.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback |
|--------------|------------------------|------------------------------|------|-----------------|
| workflow | `/adk:workflow --family quick-action` | `/workflow --family quick-action` | always | Quick Action: confirm → execute → verify. `--auto` skips confirmations. |
| communication | `/adk:communication` | `/communication` | always | Lead with conclusion. No preamble. Concrete specifics. |

### Workflow

Invoke `/adk:workflow --family quick-action` for the workflow shape.

### 1. Confirm
Present current interactivity state and confirm what the user wants to change.

### 2. Execute
Apply the requested interactivity changes.

### 3. Verify
Confirm changes were applied successfully.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:use` — routes tasks and invokes this skill when interactions are needed
- `/adk:plan` — uses decisions captured here for approved execution plans
- `/adk:interaction` — lightweight protocol reference; `interactivity` is the operational workflow skill

## Additional Reference

### Why This Skill Exists

- centralize all human-in-the-loop interaction patterns
- keep interaction agent-first and discussion-heavy
- ensure user-provided answers are revalidated before execution

### Interaction Primitives

Common interaction patterns used by this skill:

1. **single choice** (pick one option)
2. **multi choice** (pick many options)
3. **boolean confirm** (yes/no)
4. **short text input** (single-line)
5. **long text input** (multi-line rationale, constraints)
6. **editable generated draft** (approve, edit, reject cycle)
7. **ranked/prioritized selection** (order by importance)

### Modes

| Mode | Purpose | Typical output |
|---|---|---|
| `auto` | infer best interaction flow | approved plan + resolved answers |
| `options` | present alternatives and capture choice/mix | selected option set |
| `collect` | gather missing required inputs | normalized answer set |
| `edit` | user revises generated content or config | edited artifact + delta |
| `review` | triage findings/items (accept/reject/edit/skip) | decision ledger |

### Interactive Parameter Collection

When no arguments or insufficient arguments are provided, the agent asks the user for each missing parameter. For every question:

1. Analyze the prompt context and determine the most likely answer
2. Present numbered options with the recommended choice first (marked `[recommended]`)
3. Wait for user selection
4. Confirm interpreted answer before proceeding

Example flow when invoked without arguments:

```text

### Mode Selection

1. **auto** — infer best interaction flow [recommended]
2. **options** — present alternatives and capture choice
3. **collect** — gather missing required inputs
4. **edit** — user revises generated content
5. **review** — triage findings

> Pick a number, or describe what you need:
```

### Inline Interaction Protocol

For each interaction round:

1. show concise context and options
2. ask for explicit user decision
3. parse and normalize answer
4. confirm interpreted answer
5. revalidate for completeness/consistency
6. continue or ask focused follow-up

Use compact action grammar where applicable:

```text
pick: 2
pick: 1,3
mix: 1 + 3 (use 1 for backend, 3 for rollout)
edit: change timeout to 30s and keep retries=3
approve
cancel
```

### Validation

Before execution, validate all collected answers:

- required questions answered
- values satisfy allowed options/types
- no contradictory selections
- constraints are reflected in the resulting plan

If validation fails, report specific issues and ask for corrections inline.

### Output Contract

Always produce:

1. normalized answer object
2. validation status
3. unresolved questions (if any)
4. approved decisions and constraints to carry into execution

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:interactivity
```
