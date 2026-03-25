---
name: write-tech-radar
description: Use when you need to draft or directly revise a professional technology radar with Adopt, Trial, Assess, or Hold recommendations backed by evidence
user_invocable: true
arguments:
  - name: topic
    description: "Specific technology to evaluate, or 'landscape' to survey the full category"
    required: true
  - name: categories
    description: "Categories to evaluate: languages, frameworks, tools, platforms, or a comma-separated combination (default: all relevant categories)"
    required: false
---

# Technology Radar

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly revise the radar artifact. If you only want comment-only review, use `/devkit:review-doc`.

## Preflight

Before starting research or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-tech-radar`

## Required Child Agents

Run at least these child agents in parallel:

- Landscape researcher
- Adoption analyst
- Risk assessor
- Recommendation writer

## Output

Produce a professional radar document with evidence-backed classifications, dates, methodology notes, and concrete recommendations.
