---
title: 'research'
description: 'Use when you need to research a software engineering topic — searches official sources, implementations, and community patterns, then produces structured markdown with citations'
skill_name: research
category: task
workflow_tier: full
user_invocable: true
---

# research

Use `research` to you need to research a software engineering topic — searches official sources, implementations, and community patterns, then produces structured markdown with citations. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`research` belongs to the `task` layer and is declared at the `full` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<topic>` | free-text description | (required) | The topic to research |
| `--deep` | flag | off | Enable in-depth search with 4 agents instead of 2 |
| `--save` | file path | (inline output) | Save research output to a file |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--save` makes the skill write a durable artifact instead of returning everything inline.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

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

---

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

### Research Rules

- Prefer specs, official docs, maintainers, and source code over blog posts or tutorials.
- Use open-source or free tools first; call out paid requirements explicitly.
- Include publication dates or version numbers for time-sensitive claims.
- Distinguish clearly between facts, opinions, and inferred best practices.
- Every claim must include a citation or source reference.

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Standard search** (default): 2 child agents (primary-source + implementation researcher), fast turnaround
- **`--deep`**: 4 child agents (primary-source, implementation, risk analyst, synthesis), thorough investigation
- **`--save <path>`**: writes output to the specified file instead of returning inline
- **`--verbosity short`**: key findings and sources list only
- **`--verbosity detailed`**: full subtopic analysis with confidence ratings, risks, and code examples

### Depth

By default, run a **standard search** (2 agents, fast). When the user asks for deep/detailed/exhaustive research, or uses `--deep`, run an **in-depth search** (4 agents, thorough).

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

All output is markdown by default. Structure varies by deliverable type — see the skill-specific execution sections above for the exact format.

### Output

Structured markdown — designed to be consumed by other skills or read directly:

```markdown

## Related Skills

### Adjacent Skills

- `/adk:plan` — turn research into an executable plan
- `/adk:spec` — formalize requirements informed by research
- `/adk:docs-write` — publish research as durable documentation
- `/adk:dev-build` — implement after research concludes

## Additional Reference

### Standard Search (default)

Launch 2 child agents in parallel:

1. **Primary-source researcher** (`adk-research-agent`): searches official docs, specs, RFCs, and maintainer guidance. Produces findings with citations and publication dates.
2. **Implementation researcher** (`adk-research-agent`): searches real repositories, migration notes, practical examples, and community patterns. Produces implementation snippets with source links.

After both complete, merge findings: deduplicate, resolve contradictions, assign confidence ratings.

### In-Depth Search (`--deep`)

Launch 4 child agents in parallel:

1. **Primary-source researcher** (`adk-research-agent`): same as standard.
2. **Implementation researcher** (`adk-research-agent`): same as standard, but broader — also covers Stack Overflow, GitHub issues, and migration case studies.
3. **Risk analyst**: identifies edge cases, tradeoffs, version compatibility issues, breaking changes, and open questions. Produces a risk brief with severity ratings.
4. **Synthesis agent** (`adk-consensus-agent`): merges findings from all agents, resolves contradictions, assigns confidence ratings per claim, and produces a unified document.

### Research: <topic>

### Key Findings
- <finding 1> [Source](url)
- <finding 2> [Source](url)

### <Subtopic 1>
<detailed findings with inline citations>

### <Subtopic N>
...

### Code Examples
<practical snippets when relevant>

### Risks & Tradeoffs
<edge cases, limitations, open questions — only in deep mode>

### Sources
1. [Source Title](url) — <what it covers>
2. ...

### Confidence
<per-section: high/medium/low based on source quality>
```

If `--save <path>` is provided, write output to that path. Otherwise return inline.

This output is designed to be consumed by other skills (`/adk:docs-write`, `/adk:spec --mode write`, etc.) as a structured text corpus.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:research <prompt-text>
/adk:research "Next.js App Router migration patterns"
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:research "gRPC vs REST for microservices" --deep
/adk:research "React Server Components" --save ./docs/rsc-research.md
/adk:research "Kubernetes autoscaling strategies" --deep --verbosity detailed
/adk:research "SQLite WAL mode" --verbosity short
```
