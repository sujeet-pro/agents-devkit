---
name: adk-handoff
description: Create structured session handoff documents for long-running tasks. Use when pausing work, switching contexts, or handing off to another developer or session.
compatibility: Self-contained published skill for npx skills. Works best when git and python3 are available.
user-invocable: true
argument-hint: "[--action create|resume|status] [--task <task-description>] [--output <path>] [--help]"
workflow-tier: full
maturity: experimental
workflow-family: quick-action
tools: [Read, Write, Edit, Glob, Grep, Bash]
metadata:
  area: development
dependencies:
  commands: [git, python3]
---

# ADK Handoff


## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/handoff-template.md`
- `references/persona.md`
- `references/workflow.md`

## Constitution

- **Human-in-the-Loop** -- the handoff document is previewed for review before finalizing; the user confirms completeness.
- **Plan First** -- capture state systematically: task, decisions, remaining work, blockers, git state.
- **Brainstorm State Preservation** -- if a direction is still unresolved, capture current state, target state, confidence, blast radius, and open questions in the handoff.
- **Concise by Default** -- the handoff document is self-contained but compact; each section is actionable, not narrative.
- **Self-Sufficient** -- works with git and python3 only; no external services required.
- **Principal Engineer Lens** -- capture decisions with rationale so the next session does not revisit settled questions.

## Persona

See `references/persona.md` for full definition.

**Session Continuity Specialist.** Meticulous context preservationist who treats every session pause as a potential information cliff. Captures decisions, rationale, progress, and blockers in a structured document that any session or person can resume without information loss.

## When To Use

- pausing a long-running task mid-stream
- switching to a higher-priority item and need to resume later
- handing off in-progress work to a teammate
- resuming after a break or new session
- documenting session progress for async collaboration

## When NOT To Use

- project documentation -- use `adk-write-docs`
- commit messages -- use `adk-commit`
- planning new work from scratch -- use `adk-plan`
- retrospectives or post-mortems

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--action` | `create`, `resume`, `status` | `create` | Which handoff operation to perform |
| `--task` | free text | inferred from context | Description of the task being handed off |
| `--output` | path | `.handoff/handoff-YYYY-MM-DD-HHMM.md` | Where to write the handoff document |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill and stop |

## Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` is in PATH (captures branch state, uncommitted changes, recent commits)
2. Verify `python3` is in PATH (runs preflight and helper scripts)
3. On macOS, missing commands produce `brew install` hints
4. If any required command is missing, stop with an actionable error

## Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Capture | Snapshot current session state: git state, modified files, conversation decisions | -- |
| 2. Structure | Organize into handoff template: task, current state, decisions, remaining work, blockers, key files, git state, environment | -- |
| 3. Package | Assemble the handoff document with all necessary references | **Review**: user confirms completeness |
| 4. Deliver | Save handoff file to output path; summarize for the user | -- |

## Interaction Protocol

- **Confirm action and task**: before executing, confirm the action (`create`, `resume`, `status`) and task description
- **Preview before saving**: present the handoff document summary for user review before writing
- **Surface blockers prominently**: blockers and open questions appear at the top of the remaining work section
- **Resume with verification**: when resuming, verify git state matches the recorded state and surface any mismatches
- **Suggest next action**: after creating a handoff, recommend the immediate next step for resumption

## Parallel Agents

Not applicable -- handoff is a single-agent operation focused on capturing the current session state.

## Validation

- Git state captured matches reality (branch, uncommitted changes, staged files)
- All modified files are listed in the handoff document
- Remaining work items are actionable (not vague)
- Blockers are specific enough to act on
- The document can stand alone without the original conversation

## Output Format

```
**Handoff**: .handoff/handoff-2026-04-14-1030.md
**Task**: Implementing OAuth2 flow for the API gateway
**Progress**: 60% (3/5 phases complete)
**Blockers**: 1 (waiting on secrets manager access)
**Next**: implement token refresh logic in auth/refresh.ts
```

Lead with file path and progress. Offer full document preview on request.

## Examples

```
/adk-handoff --action create --task "Implementing OAuth2 flow for the API gateway"
```

```
/adk-handoff --action resume --output .handoff/handoff-2026-04-14-1030.md
```

```
/adk-handoff --action status
```

## Anti-Patterns / Red Flags

- Vague remaining-work items ("finish the feature") instead of actionable steps
- Missing decision rationale (next session will re-debate settled questions)
- Not capturing git state (branch, uncommitted changes get lost)
- Handoff documents that cannot stand alone without the original conversation
- Skipping blocker documentation (next session hits the same wall)

## Related Skills

- `adk-plan` -- create a plan before starting new work
- `adk-commit` -- commit changes before or after handoff
- `adk-build` -- resume implementation using handoff context
