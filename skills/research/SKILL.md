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

## Preflight

Before launching child agents, run:

`zsh scripts/check-skill-deps.zsh research output=<output>`

If the output target is Google Docs or Confluence, verify MCP connectivity with a lightweight read.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/research-and-fact-checking.md`

## Required Child Agents

Choose child-agent count and roles by depth:

### quick (2 agents)
- **Primary-source researcher** (`research-agent`): searches official docs, specs, and maintainers' guidance for the topic. Produces findings with citations and publication dates.
- **Implementation researcher** (`research-agent`): searches real repositories, migration notes, and practical examples. Produces implementation patterns with source links.

### standard (3 agents)
- **Primary-source researcher**: same as quick.
- **Implementation researcher**: same as quick.
- **Risk analyst**: identifies edge cases, tradeoffs, version compatibility issues, and open questions. Produces a risk brief with severity ratings.

### deep (4 agents)
- All standard agents, plus:
- **Synthesis agent** (`consensus-agent`): merges findings from all agents, resolves contradictions, and produces a unified research document with confidence ratings per claim.

### exhaustive (5 agents)
- All deep agents, plus:
- **Publishing agent** (`source-publisher`): formats and publishes the final research to the target output (Google Docs or Confluence) when requested.

## Workflow

1. **Scope.** Clarify the research question, boundaries, and expected deliverables.
2. **Launch agents.** Run the appropriate number of child agents in parallel based on `depth`.
3. **Merge.** Combine findings: deduplicate overlapping results, resolve contradictions, and assign confidence ratings.
4. **Format.** Produce the output in the requested format:
   - **markdown**: structured document with sections, citations, and code examples
   - **outline**: hierarchical bullet points with key findings
   - **notes**: brief, flat list of findings with links
   - **google-doc**: publish through Google Drive MCP
   - **confluence**: publish through Confluence MCP
5. **Save.** If `save` is provided, write the output to the specified path.

Save intermediary artifacts to `.temp/research/`.

## Research Rules

- Prefer specs, official docs, maintainers, and source code over blog posts or tutorials.
- Use open-source or free tools first; call out paid requirements explicitly.
- Include publication dates or version numbers for time-sensitive claims.
- Distinguish clearly between facts, opinions, and inferred best practices.
- Every claim must include a citation or source reference.

## Output

A research document containing:

- **Executive Summary**: key findings in 2-3 sentences
- **Detailed Findings**: organized by subtopic with citations
- **Code Examples**: practical snippets when relevant
- **Risk and Tradeoffs**: edge cases, limitations, and open questions
- **Sources**: numbered reference list with URLs and dates
- **Confidence Ratings**: per-section confidence (high, medium, low) based on source quality

## Adjacent Skills

- `/devkit:research-quick` for fast, 2-agent research
- `/devkit:research-deep` for exhaustive, 5-agent research
- `/devkit:write-article` for research-backed article drafting
- `/devkit:write-tool-eval` for structured tool comparisons
