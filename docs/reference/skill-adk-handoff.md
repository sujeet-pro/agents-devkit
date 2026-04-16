---
title: 'adk-handoff'
description: 'Create structured session handoff documents for long-running tasks. Use when pausing work, switching contexts, or handing off to another developer or session'
skill_name: adk-handoff
category: task
workflow_tier: full
user_invocable: true
---

# adk-handoff

Use `adk-handoff` to create structured session handoff documents for long-running tasks. Use when pausing work, switching contexts, or handing off to another developer or session. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-handoff` belongs to the `task` layer and is declared at the `full` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--action` | `create`, `resume`, `status` | `create` | Which handoff operation to perform |
| `--task` | free text | inferred from context | Description of the task being handed off |
| `--output` | path | `.handoff/handoff-YYYY-MM-DD-HHMM.md` | Where to write the handoff document |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill and stop |

### Parameter Notes

- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Capture | Snapshot current session state: git state, modified files, conversation decisions | -- |
| 2. Structure | Organize into handoff template: task, current state, decisions, remaining work, blockers, key files, git state, environment | -- |
| 3. Package | Assemble the handoff document with all necessary references | **Review**: user confirms completeness |
| 4. Deliver | Save handoff file to output path; summarize for the user | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Handoff**: .handoff/handoff-2026-04-14-1030.md
**Task**: Implementing OAuth2 flow for the API gateway
**Progress**: 60% (3/5 phases complete)
**Blockers**: 1 (waiting on secrets manager access)
**Next**: implement token refresh logic in auth/refresh.ts
```

Lead with file path and progress. Offer full document preview on request.

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/handoff-template.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- the handoff document is previewed for review before finalizing; the user confirms completeness.
- **Plan First** -- capture state systematically: task, decisions, remaining work, blockers, git state.
- **Brainstorm State Preservation** -- if a direction is still unresolved, capture current state, target state, confidence, blast radius, and open questions in the handoff.
- **Concise by Default** -- the handoff document is self-contained but compact; each section is actionable, not narrative.
- **Self-Sufficient** -- works with git and python3 only; no external services required.
- **Principal Engineer Lens** -- capture decisions with rationale so the next session does not revisit settled questions.

### Persona

See `references/persona.md` for full definition.

**Session Continuity Specialist.** Meticulous context preservationist who treats every session pause as a potential information cliff. Captures decisions, rationale, progress, and blockers in a structured document that any session or person can resume without information loss.

### When To Use

- pausing a long-running task mid-stream
- switching to a higher-priority item and need to resume later
- handing off in-progress work to a teammate
- resuming after a break or new session
- documenting session progress for async collaboration

### When NOT To Use

- project documentation -- use `adk-write-docs`
- commit messages -- use `adk-commit`
- planning new work from scratch -- use `adk-plan`
- retrospectives or post-mortems

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` is in PATH (captures branch state, uncommitted changes, recent commits)
2. Verify `python3` is in PATH (runs preflight and helper scripts)
3. On macOS, missing commands produce `brew install` hints
4. If any required command is missing, stop with an actionable error

### Interaction Protocol

- **Confirm action and task**: before executing, confirm the action (`create`, `resume`, `status`) and task description
- **Preview before saving**: present the handoff document summary for user review before writing
- **Surface blockers prominently**: blockers and open questions appear at the top of the remaining work section
- **Resume with verification**: when resuming, verify git state matches the recorded state and surface any mismatches
- **Suggest next action**: after creating a handoff, recommend the immediate next step for resumption

### Parallel Agents

Not applicable -- handoff is a single-agent operation focused on capturing the current session state.

### Validation

- Git state captured matches reality (branch, uncommitted changes, staged files)
- All modified files are listed in the handoff document
- Remaining work items are actionable (not vague)
- Blockers are specific enough to act on
- The document can stand alone without the original conversation

### Anti-Patterns / Red Flags

- Vague remaining-work items ("finish the feature") instead of actionable steps
- Missing decision rationale (next session will re-debate settled questions)
- Not capturing git state (branch, uncommitted changes get lost)
- Handoff documents that cannot stand alone without the original conversation
- Skipping blocker documentation (next session hits the same wall)

### Related Skills

- `adk-plan` -- create a plan before starting new work
- `adk-commit` -- commit changes before or after handoff
- `adk-build` -- resume implementation using handoff context

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-handoff
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-handoff --auto
```
