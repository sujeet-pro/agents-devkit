---
title: 'adk-brainstorm'
description: 'Run iterative brainstorming to narrow options, question assumptions, choose blast radius, and route into the right implementation or documentation skill. Use when a task needs design closure before work begins'
skill_name: adk-brainstorm
category: task
workflow_tier: full
user_invocable: true
---

# adk-brainstorm

Use `adk-brainstorm` to run iterative brainstorming to narrow options, question assumptions, choose blast radius, and route into the right implementation or documentation skill. Use when a task needs design closure before work begins. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-brainstorm` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What needs to be decided or narrowed down |
| `--skill-context` | `research`, `spec`, `plan`, `build`, `refactor`, `migrate`, `design`, `write-docs` | `plan` | Which downstream workflow this brainstorm is feeding |
| `--confidence` | `85`, `90`, `95` or `0-100` | auto | Desired confidence before finalizing direction |
| `--change-tolerance` | `surgical`, `bounded`, `transformative` | `bounded` | Acceptable blast radius |
| `--artifact` | `none`, `proposal`, `prd`, `rfc`, `hld`, `lld`, `tdd`, `plan`, `all` | `none` | Preferred output artifact |
| `--scope` | path | none | Limit repo inspection to one surface |
| `--auto` | flag | off | Skip confirmations and use the recommended route automatically |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Confirm** -- restate the task, downstream context, confidence target, blast radius, and artifact preference. *Gate: user approval unless `--auto`.*
2. **Detect** -- check whether the `brainstorming` MCP server is available. If yes, create a session. If not, switch to the manual fallback and warn once.
3. **Capture** -- record current state, target state, and what is still missing.
4. **Research** -- gather repo and external evidence for direction-changing unknowns.
5. **Options** -- present 2-3 viable paths when meaningful choices exist. *Gate: user chooses or refines direction unless `--auto`.*
6. **Questions** -- ask follow-up questions until the remaining ambiguity is no longer direction-changing.
7. **Finalize** -- check confidence against the threshold and either finalize the direction or explicitly accept the gap.
8. **Route** -- recommend and, when asked, hand off to `adk-spec`, `adk-plan`, `adk-write-docs`, `adk-build`, `adk-design`, `adk-refactor`, or `adk-migrate`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/research-protocol.md`
- `references/_shared/output-format.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **MCP First, Fallback Always** -- prefer the `brainstorming` MCP server when available; if it is missing, warn once and continue with the shared manual workflow.
- **Plan First** -- this skill exists to close ambiguity before planning, docs, or code changes.
- **Concise by Default** -- lead with the recommended direction, confidence, and next route.
- **Principal Engineer Lens** -- challenge whether the task needs a large change, a smaller fix, or no change at all.
- **Human-in-the-Loop** -- ask follow-up questions until the remaining ambiguity is no longer direction-changing.

### Persona

**Direction Facilitator.** Mission: turn vague requests into an explicit direction with known trade-offs, a chosen blast radius, a confidence threshold, and a clear next route. Thinks in current state versus target state, not just feature ideas. Pushes for the smallest correct path when risk is high and allows broader redesign when the user explicitly wants it.

Hard rules:
- Capture `currentState`, `targetState`, `changeTolerance`, `desiredConfidence`, and `artifactPreference`.
- Surface 2-3 viable options when trade-offs exist.
- Keep open questions separate from the chosen direction.
- Do not finalize below the requested confidence threshold unless the user explicitly accepts the gap.
- Recommend the next skill or artifact instead of drifting straight into implementation.

### When To Use

- a request needs design closure before implementation starts
- multiple valid approaches exist and the user wants help picking one
- the acceptable blast radius matters
- a task may need a proposal, spec, design doc, or plan before code changes
- the user wants an iterative research-question-answer loop before direction is locked

### When NOT To Use

- trivial changes with one obvious path and low risk
- pure fact-finding with no decision to make -- use `adk-research`
- implementation after the direction is already approved -- use `adk-build`
- standalone plan authoring after design closure already happened -- use `adk-plan`

### Pre-flight

Before starting, verify:
- `git` and `python3` are available on PATH
- if `--scope` is provided, the path exists in the repository
- if the `brainstorming` MCP server is present, use it as the default session store
- if the MCP server is missing, show one install warning and continue with the fallback workflow

### Interaction Protocol

### Confirmation
Before the loop starts, confirm:
- task
- downstream skill context
- desired confidence
- change tolerance
- preferred artifact

### Warnings
If the MCP server is missing, say so explicitly:

`Warning: the brainstorming MCP server is not configured. Continuing with the fallback workflow. Install it for structured state, stronger iteration support, and cleaner handoff between design and implementation.`

### User Responses
- `a` / `b` / `c` -- choose an option
- `raise confidence to 95` -- tighten the threshold
- `keep this surgical` -- reduce blast radius
- `route to spec` -- force the next skill
- free-text feedback -- refine the current direction

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-research-agent` | external facts or upstream behavior affect the choice | gather verified evidence |
| `adk-plan-reviewer` | a proposed route needs feasibility critique before finalizing | pressure-test the chosen direction |
| `adk-brainstorm-facilitator` | the loop needs structured option comparison and question sequencing | drive the iterative decision process |

### Validation

- current state and target state are explicit
- change tolerance and desired confidence are explicit
- the chosen direction matches the confidence bar or the gap is explicitly accepted
- open questions are separated from the finalized direction
- the recommended next route is clear

### Brainstorm: <task summary>



### Direction

<recommended path and why>

### Current State

<what exists today>

### Target State

<what should be true after the work>

### Options

- Option A: <summary>
- Option B: <summary>

### Confidence

- Current: <score>
- Desired: <score>

### Open Questions

- <question>

### Recommended Route

-> <next skill or artifact>

Need more detail on any option or trade-off?
```

### Related Skills

- `adk-research` -- investigate unknowns that affect the choice
- `adk-spec` -- write the functional or technical spec after direction is chosen
- `adk-plan` -- create the executable implementation plan
- `adk-write-docs` -- turn the finalized direction into a persistent artifact
- `adk-build` -- implement after the direction is approved

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-brainstorm <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-brainstorm --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-brainstorm <prompt-text> --auto
```
