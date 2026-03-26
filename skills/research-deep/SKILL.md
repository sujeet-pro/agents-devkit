---
name: research-deep
description: Exhaustive software engineering research using the shared multi-agent research pipeline
user_invocable: true
arguments:
  - name: topic
    description: "Topic to research"
    required: true
  - name: output
    description: "Output format: markdown, outline, notes, google-doc, confluence (default: markdown)"
    required: false
  - name: save
    description: "Optional file path to save output"
    required: false
---

# Deep Research

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, and `skills/_references/output-formats.md`.

This is a convenience wrapper around `/devkit:research` with `depth=exhaustive`. It runs the full 5-agent research pipeline for comprehensive coverage.

## Preflight

Before launching child agents, run:

`zsh scripts/check-skill-deps.zsh research-deep output=<output>`

If the output target is Google Docs or Confluence, verify MCP connectivity with a lightweight read.

## Required Child Agents

Run all 5 agents in parallel:

- **Primary-source researcher** (`research-agent`): searches official docs, specs, RFCs, and maintainers' guidance. Produces findings with citations and publication dates.
- **Implementation researcher** (`research-agent`): searches real repositories, migration notes, Stack Overflow answers, and practical examples. Produces implementation patterns with source links.
- **Risk analyst**: identifies edge cases, tradeoffs, version compatibility issues, breaking changes, and open questions. Produces a risk brief with severity ratings.
- **Synthesis agent** (`consensus-agent`): merges findings from all research agents, resolves contradictions, assigns confidence ratings per claim, and produces a unified research document.
- **Publishing agent** (`source-publisher`): formats and publishes the final research to the target output when the destination is Google Docs or Confluence.

## Workflow

1. **Scope.** Clarify the research question, boundaries, and expected deliverables.
2. **Launch all 5 agents.** Run primary-source, implementation, and risk passes in parallel.
3. **Synthesize.** The synthesis agent merges all findings with confidence ratings and contradiction resolution.
4. **Publish.** The publishing agent formats output for the requested destination.
5. **Save.** If `save` is provided, write the output to the specified path.

Save intermediary artifacts to `.temp/research-deep/`.

## Output

A comprehensive research document with executive summary, detailed findings by subtopic, code examples, risk analysis, numbered source references, and per-section confidence ratings.

## Adjacent Skills

- `/devkit:research` for configurable-depth research
- `/devkit:research-quick` for fast, 2-agent research
- `/devkit:write-article` for research-backed article drafting
