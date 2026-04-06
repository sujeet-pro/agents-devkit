---
name: adk-interactivity
description: "adk - [full] [interaction] Agent-first interaction orchestration for option selection, data capture, edits, and human approval with optional external TUI"
user-invocable: true
argument-hint: "<goal> [--mode auto|options|collect|edit|review] [--tui true|false] [--form <path>] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Read, Write, Edit, Bash, Agent]
workflow-tier: full
---

# Interactivity

Use this skill when a task needs structured user interaction (choosing approaches, collecting constrained inputs, editing generated data, approving findings) before execution.

Default behavior is agent-native inline interaction. Optional external TUI is supported only when the user explicitly sets `--tui true`.

## Why This Skill Exists

- centralize all human-in-the-loop interaction patterns
- keep interaction agent-first and discussion-heavy by default
- support a structured fallback flow for larger forms using JSON/YAML sessions
- ensure user-provided answers are revalidated before execution

## Research Summary (2024-2026)

Common interaction primitives used by engineering agents and CLI tools:

1. **single choice** (pick one option)
2. **multi choice** (pick many options)
3. **boolean confirm** (yes/no)
4. **short text input** (single-line)
5. **long text input** (multi-line rationale, constraints)
6. **editable generated draft** (approve, edit, reject cycle)
7. **ranked/prioritized selection** (order by importance)

Supporting references:
- Textual widget capabilities ([Input](https://textual.textualize.io/widgets/input/), [Select](https://textual.textualize.io/widgets/select), [Checkbox](https://textual.textualize.io/widgets/checkbox), [RadioButton](https://textual.textualize.io/widgets/radiobutton))
- Questionary prompt taxonomy ([repo](https://github.com/tmbo/questionary), [docs](https://questionary.readthedocs.io/en/stable/pages/quickstart.html))
- YAML wizard patterns ([pydantic-wizard](https://pypi.org/project/pydantic-wizard/))

## Modes

| Mode | Purpose | Typical output |
|---|---|---|
| `auto` | infer best interaction flow | approved plan + resolved answers |
| `options` | present alternatives and capture choice/mix | selected option set |
| `collect` | gather missing required inputs | normalized answer set |
| `edit` | user revises generated content or config | edited artifact + delta |
| `review` | triage findings/items (accept/reject/edit/skip) | decision ledger |

## Interaction Backend Selection

Use this order:

1. **Inline Agentic** (default): render structured prompts in conversation.
2. **External TUI** (`--tui true`): generate a session file and ask user to run the TUI command.

`--tui` defaults to `false`.

## Inline Agentic Protocol (Default)

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

## Optional TUI Flow (`--tui true`)

Use this only when the user explicitly opts in.

### Step 1: Write session file

Write a JSON or YAML session artifact, for example:

```yaml
session:
  id: interact-<timestamp>
  title: "Interaction Session"
  mode: options
  schema_version: 1
items:
  - id: approach
    type: single_choice
    prompt: "Choose implementation approach"
    options:
      - id: a
        label: "Fast path"
      - id: b
        label: "Balanced path"
      - id: c
        label: "Safe path"
  - id: constraints
    type: multi_choice
    prompt: "Select constraints"
    options:
      - id: backward_compat
        label: "Backward compatibility"
      - id: low_risk
        label: "Low risk"
      - id: shortest_time
        label: "Shortest timeline"
  - id: notes
    type: long_text
    prompt: "Anything else we must consider?"
results: []
status: pending
```

### Step 2: Ask user to run TUI command

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/tui/interactivity.py <session-file>
```

### Step 3: Read updated results

Read the updated session file and normalize `results`.

### Step 4: Revalidate

Before execution, revalidate:

- required questions answered
- values satisfy allowed options/types
- no contradictory selections
- constraints are reflected in the resulting plan

If validation fails, report specific issues and ask for corrections (inline or TUI re-run).

## When TUI Is Worth Using

Prefer TUI only for high-volume or form-heavy scenarios, such as:

- 15+ review findings requiring triage
- multi-section forms with many required fields
- stakeholder workshops with long option sets
- repeated batch approvals in one session

For normal engineering flows, inline interaction should remain the default.

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
