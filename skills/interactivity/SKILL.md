---
name: interactivity
description: "adk - [full] [interaction] Agent-first interaction orchestration for option selection, data capture, edits, and human approval"
user-invocable: true
argument-hint: "<goal> [--mode auto|options|collect|edit|review] [--form <path>] [--verbosity short|standard|detailed] [--auto] [--help]"
allowed-tools: [Read, Write, Edit, Bash, Agent]
workflow-tier: full
maturity: stable
workflow-family: quick-action
---

# Interactivity

Use this skill when a task needs structured user interaction (choosing approaches, collecting constrained inputs, editing generated data, approving findings) before execution.

All interaction happens inline in the agent conversation. When no arguments are provided, the skill enters interactive mode and asks the user for each required parameter — presenting options with a recommended first choice based on prompt analysis.

## Why This Skill Exists

- centralize all human-in-the-loop interaction patterns
- keep interaction agent-first and discussion-heavy
- ensure user-provided answers are revalidated before execution

## Interaction Primitives

Common interaction patterns used by this skill:

1. **single choice** (pick one option)
2. **multi choice** (pick many options)
3. **boolean confirm** (yes/no)
4. **short text input** (single-line)
5. **long text input** (multi-line rationale, constraints)
6. **editable generated draft** (approve, edit, reject cycle)
7. **ranked/prioritized selection** (order by importance)

## Modes

| Mode | Purpose | Typical output |
|---|---|---|
| `auto` | infer best interaction flow | approved plan + resolved answers |
| `options` | present alternatives and capture choice/mix | selected option set |
| `collect` | gather missing required inputs | normalized answer set |
| `edit` | user revises generated content or config | edited artifact + delta |
| `review` | triage findings/items (accept/reject/edit/skip) | decision ledger |

## Interactive Parameter Collection

When no arguments or insufficient arguments are provided, the agent asks the user for each missing parameter. For every question:

1. Analyze the prompt context and determine the most likely answer
2. Present numbered options with the recommended choice first (marked `[recommended]`)
3. Wait for user selection
4. Confirm interpreted answer before proceeding

Example flow when invoked without arguments:

```text
## Mode Selection

1. **auto** — infer best interaction flow [recommended]
2. **options** — present alternatives and capture choice
3. **collect** — gather missing required inputs
4. **edit** — user revises generated content
5. **review** — triage findings

> Pick a number, or describe what you need:
```

## Inline Interaction Protocol

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

## Validation

Before execution, validate all collected answers:

- required questions answered
- values satisfy allowed options/types
- no contradictory selections
- constraints are reflected in the resulting plan

If validation fails, report specific issues and ask for corrections inline.

## Output Contract

Always produce:

1. normalized answer object
2. validation status
3. unresolved questions (if any)
4. approved decisions and constraints to carry into execution

## Adjacent Skills

- `/adk:use` — routes tasks and invokes this skill when interactions are needed
- `/adk:plan` — uses decisions captured here for approved execution plans
- `/adk:interaction` — lightweight protocol reference; `interactivity` is the operational workflow skill
