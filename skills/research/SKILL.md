---
name: research
description: "[full] [research] Use when you need to research a software engineering topic — searches official sources, implementations, and community patterns, then produces structured markdown with citations"
user-invocable: true
argument-hint: "<topic> [--deep] [--save path] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Research

Read `references/agentic-teams.md` for the child-agent contract.

Load `references/research-methodology.md` for research quality standards.

---

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
/research "Next.js App Router migration patterns"
/research "gRPC vs REST for microservices" --deep
/research "React Server Components" --save ./docs/rsc-research.md
/research "Kubernetes autoscaling strategies" --deep --verbosity detailed
/research "SQLite WAL mode" --verbosity short
```

---



Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.


## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Define research scope, identify primary sources; Focused research on chosen approach, proposal at ./temp/proposal/ |
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

This output is designed to be consumed by other skills (`/write`, `/spec --mode write`, etc.) as a structured text corpus.

## Adjacent Skills

- See the parent router skill for related skills
