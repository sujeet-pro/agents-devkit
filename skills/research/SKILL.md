---
name: adk-research
description: "adk - [full] [research] Use when you need to research a software engineering topic — searches official sources, implementations, and community patterns, then produces structured markdown with citations"
user-invocable: true
argument-hint: "<topic> [--deep] [--save path] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Research

Load `references/research-methodology.md` for research quality standards. For parallel child agents, follow `/adk:agentic-teams` (also listed under Shared Skills below).

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

---

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/adk-<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<topic>` | free-text description | (required) | The topic to research |
| `--deep` | flag | off | Enable in-depth search with 4 agents instead of 2 |
| `--save` | file path | (inline output) | Save research output to a file |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Behavior Variations

- **Standard search** (default): 2 child agents (primary-source + implementation researcher), fast turnaround
- **`--deep`**: 4 child agents (primary-source, implementation, risk analyst, synthesis), thorough investigation
- **`--save <path>`**: writes output to the specified file instead of returning inline
- **`--verbosity short`**: key findings and sources list only
- **`--verbosity detailed`**: full subtopic analysis with confidence ratings, risks, and code examples

### Examples

```
/adk:research "Next.js App Router migration patterns"
/adk:research "gRPC vs REST for microservices" --deep
/adk:research "React Server Components" --save ./docs/rsc-research.md
/adk:research "Kubernetes autoscaling strategies" --deep --verbosity detailed
/adk:research "SQLite WAL mode" --verbosity short
```

---

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Define research scope, identify primary sources; Focused research on chosen approach, proposal at .temp/proposal/ |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes; Iterate on proposal with user feedback |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Launch research child agents in parallel |
| 5. Validate & Learn | yes | Verify citations, cross-reference findings, check for gaps |

## Output Format

All output is markdown by default. Structure varies by deliverable type — see the skill-specific execution sections above for the exact format.

## Depth

By default, run a **standard search** (2 agents, fast). When the user asks for deep/detailed/exhaustive research, or uses `--deep`, run an **in-depth search** (4 agents, thorough).

## Standard Search (default)

Launch 2 child agents in parallel:

1. **Primary-source researcher** (`research-agent`): searches official docs, specs, RFCs, and maintainer guidance. Produces findings with citations and publication dates.
2. **Implementation researcher** (`research-agent`): searches real repositories, migration notes, practical examples, and community patterns. Produces implementation snippets with source links.

After both complete, merge findings: deduplicate, resolve contradictions, assign confidence ratings.

## In-Depth Search (`--deep`)

Launch 4 child agents in parallel:

1. **Primary-source researcher** (`research-agent`): same as standard.
2. **Implementation researcher** (`research-agent`): same as standard, but broader — also covers Stack Overflow, GitHub issues, and migration case studies.
3. **Risk analyst**: identifies edge cases, tradeoffs, version compatibility issues, breaking changes, and open questions. Produces a risk brief with severity ratings.
4. **Synthesis agent** (`consensus-agent`): merges findings from all agents, resolves contradictions, assigns confidence ratings per claim, and produces a unified document.

## Research Rules

- Prefer specs, official docs, maintainers, and source code over blog posts or tutorials.
- Use open-source or free tools first; call out paid requirements explicitly.
- Include publication dates or version numbers for time-sensitive claims.
- Distinguish clearly between facts, opinions, and inferred best practices.
- Every claim must include a citation or source reference.

## Output

Structured markdown — designed to be consumed by other skills or read directly:

```markdown
## Research: <topic>

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

## Adjacent Skills

- `/adk:plan` — turn research into an executable plan
- `/adk:spec` — formalize requirements informed by research
- `/adk:docs-write` — publish research as durable documentation
- `/adk:dev-build` — implement after research concludes
