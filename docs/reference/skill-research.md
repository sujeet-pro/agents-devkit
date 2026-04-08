---
title: "research"
description: Multi-agent research with citations from official sources, implementations, and community patterns
skill_name: research
category: task
workflow_tier: full
user_invocable: true
---

# research

Searches official sources, implementations, and community patterns using parallel child agents, then produces structured markdown with citations. Standard mode uses 2 agents for fast turnaround; deep mode uses 4 agents for thorough investigation with risk analysis and synthesis.

## When to Use

- Research a software engineering topic with cited sources
- Compare technologies, frameworks, or approaches
- Investigate migration paths or upgrade strategies
- Gather implementation patterns from real repositories
- Produce structured research output for downstream skills (specs, docs, plans)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<topic>` | free-text description | required | The topic to research |
| `--deep` | flag | off | Enable in-depth search with 4 agents instead of 2 |
| `--save` | file path | inline output | Save research output to a file instead of returning inline |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Standard search** (default) | 2 child agents (primary-source + implementation researcher), fast turnaround |
| **`--deep`** | 4 child agents (primary-source, implementation, risk analyst, synthesis), thorough investigation |
| **`--save <path>`** | Writes output to the specified file instead of returning inline |
| **`--verbosity short`** | Key findings and sources list only |
| **`--verbosity detailed`** | Full subtopic analysis with confidence ratings, risks, and code examples |

## Research Agents

### Standard Search (default — 2 agents)

1. **Primary-source researcher** (`adk-research-agent`): searches official docs, specs, RFCs, and maintainer guidance. Produces findings with citations and publication dates.
2. **Implementation researcher** (`adk-research-agent`): searches real repositories, migration notes, practical examples, and community patterns. Produces implementation snippets with source links.

After both complete, findings are merged: deduplicated, contradictions resolved, confidence ratings assigned.

### In-Depth Search (`--deep` — 4 agents)

1. **Primary-source researcher** (`adk-research-agent`): same as standard.
2. **Implementation researcher** (`adk-research-agent`): same as standard, but broader — also covers Stack Overflow, GitHub issues, and migration case studies.
3. **Risk analyst**: identifies edge cases, tradeoffs, version compatibility issues, breaking changes, and open questions. Produces a risk brief with severity ratings.
4. **Synthesis agent** (`adk-consensus-agent`): merges findings from all agents, resolves contradictions, assigns confidence ratings per claim, and produces a unified document.

## Research Rules

- Prefer specs, official docs, maintainers, and source code over blog posts or tutorials
- Use open-source or free tools first; call out paid requirements explicitly
- Include publication dates or version numbers for time-sensitive claims
- Distinguish clearly between facts, opinions, and inferred best practices
- Every claim must include a citation or source reference

## Key Behaviors

- **Citation-driven**: every claim carries a source reference
- **Confidence-rated**: per-section confidence scoring (high/medium/low) based on source quality
- **Contradiction resolution**: when agents disagree, findings are reconciled with explicit notes
- **Composable output**: structured markdown designed to be consumed by `/adk:docs-write`, `/adk:spec`, `/adk:plan`, and other skills
- **Time-aware**: includes publication dates and version numbers for currency

## Workflow

Follows the 6-phase workflow.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, assumptions, required tools, and success criteria |
| 1. Research & Options | yes | Define research scope, identify primary sources |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Launch research child agents in parallel |
| 5. Validate & Learn | yes | Verify citations, cross-reference findings, check for gaps |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect dependencies, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

Structured markdown with the following sections:

```markdown
## Research: <topic>

### Key Findings
- <finding 1> [Source](url)
- <finding 2> [Source](url)

### <Subtopic 1>
<detailed findings with inline citations>

### Code Examples
<practical snippets when relevant>

### Risks & Tradeoffs
<edge cases, limitations, open questions — deep mode only>

### Sources
1. [Source Title](url) — <what it covers>

### Confidence
<per-section: high/medium/low based on source quality>
```

Verbosity adapts to `--verbosity`:

- **short**: key findings and sources list only
- **standard**: full structured output with all sections
- **detailed**: standard output plus confidence ratings, risks, and code examples

If `--save <path>` is provided, output is written to that path. Otherwise returned inline.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:plan` | Turn research into an executable plan |
| `/adk:spec` | Formalize requirements informed by research |
| `/adk:docs-write` | Publish research as durable documentation |
| `/adk:dev-build` | Implement after research concludes |

## Examples

```
/adk:research "Next.js App Router migration patterns"
/adk:research "gRPC vs REST for microservices" --deep
/adk:research "React Server Components" --save ./docs/rsc-research.md
/adk:research "Kubernetes autoscaling strategies" --deep --verbosity detailed
/adk:research "SQLite WAL mode" --verbosity short
```
