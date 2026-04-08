---
title: "research"
description: Multi-agent engineering research with citations and confidence ratings
skill_name: research
category: task
workflow_tier: full
---

# research

Researches engineering topics using parallel agents that search official docs, specs, implementations, and community patterns. Produces structured markdown with citations.

## When to Use

- Investigate a technology, pattern, or approach before building
- Compare alternatives with cited evidence
- Deep investigation with risk analysis

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<topic>` | free text | (required) | The topic to research |
| `--deep` | flag | off | 4-agent deep research instead of 2-agent standard |
| `--save` | file path | inline output | Save research to a file |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Research Modes

### Standard (default) — 2 agents

1. **Primary-source researcher** — official docs, specs, RFCs, maintainer guidance
2. **Implementation researcher** — real repos, migration notes, community patterns

### Deep (`--deep`) — 4 agents

1. **Primary-source researcher** — same as standard
2. **Implementation researcher** — broader (also Stack Overflow, GitHub issues)
3. **Risk analyst** — edge cases, tradeoffs, breaking changes, open questions
4. **Synthesis agent** — merges findings, resolves contradictions, assigns confidence

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm topic, assumptions, success criteria |
| 1. Research | Define scope, identify primary sources |
| 2. Approach | Present research strategy, user approves |
| 3. Planning | Assign agent roles and search domains |
| 4. Execute | Launch parallel research agents |
| 5. Validate | Verify citations, cross-reference, check gaps |

## Output Format

```markdown
## Research: <topic>

### Key Findings
- <finding> [Source](url)

### <Subtopic>
<detailed findings with citations>

### Code Examples
<snippets when relevant>

### Risks & Tradeoffs (deep mode only)
<edge cases, limitations>

### Sources
1. [Title](url) — coverage

### Confidence
<per-section: high/medium/low>
```

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams`, `interaction`.

## Examples

```text
/adk:research "Next.js App Router migration patterns"
/adk:research "gRPC vs REST for microservices" --deep
/adk:research "React Server Components" --save ./docs/research/rsc.md
/adk:research "Kubernetes autoscaling" --deep --verbosity detailed
/adk:research "SQLite WAL mode" --verbosity short
```
