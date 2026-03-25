---
name: research
description: Multi-agent software engineering research with citations, official-source bias, and markdown or document output
user_invocable: true
arguments:
  - name: topic
    description: "Topic to research"
    required: true
  - name: depth
    description: "Depth: quick, standard, deep, exhaustive (default: standard)"
    required: false
  - name: output
    description: "Output format: markdown, outline, notes, google-doc, confluence (default: markdown)"
    required: false
  - name: save
    description: "Optional file path to save the research"
    required: false
---

# Research

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, and `skills/_references/output-formats.md`.

## Required Child Agents

Choose child-agent count by depth:

- quick: 2 agents
- standard: 3 agents
- deep: 4 agents
- exhaustive: 5 agents

Always include:

- `research-agent` for primary sources
- a second `research-agent` pass for implementation examples and migration notes

For deeper runs add:

- a risk and edge-case pass
- a synthesis pass through `consensus-agent`
- a publishing pass if the target is Google Docs or Confluence

## Research Rules

- Prefer specs, official docs, maintainers, and source code.
- Use open-source or free tools first; call out paid requirements explicitly.
- Include publication dates or version numbers for time-sensitive claims.
- Distinguish clearly between facts, opinions, and inferred best practices.
