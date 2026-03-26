---
name: research-quick
description: Quick multi-agent software research using the shared research pipeline with shorter scope and faster output
user_invocable: true
arguments:
  - name: topic
    description: "Topic to search"
    required: true
  - name: output
    description: "Output format: notes, outline, markdown (default: notes)"
    required: false
  - name: save
    description: "Optional file path to save output"
    required: false
---

# Quick Research

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, and `skills/_references/output-formats.md`.

This is a convenience wrapper around `/devkit:research` with `depth=quick`. It runs a fast 2-agent research pipeline for rapid answers.

## Preflight

Before launching child agents, run:

`zsh scripts/check-skill-deps.zsh research-quick`

## Required Child Agents

Run 2 agents in parallel:

- **Primary-source researcher** (`research-agent`): searches official docs, specs, and maintainers' guidance for the topic. Focuses on the most authoritative and recent sources. Produces findings with citations.
- **Implementation researcher** (`research-agent`): searches real repositories, practical examples, and community patterns. Produces implementation snippets with source links.

## Workflow

1. **Scope.** Clarify the research question and boundaries.
2. **Launch 2 agents.** Run primary-source and implementation passes in parallel.
3. **Merge.** Combine findings, deduplicate, and assign confidence ratings.
4. **Format.** Produce the output in the requested format (notes, outline, or markdown).
5. **Save.** If `save` is provided, write the output to the specified path.

## Output

A concise research output with key findings, practical examples, source references, and confidence ratings. Optimized for speed over exhaustiveness.

## Adjacent Skills

- `/devkit:research` for configurable-depth research
- `/devkit:research-deep` for exhaustive, 5-agent research
- `/devkit:write-article` for research-backed article drafting
