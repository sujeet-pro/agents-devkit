---
name: write-onboarding
description: Use when you need to draft or directly revise a professional repository onboarding guide for new team members, transfers, or contributors
user_invocable: true
arguments:
  - name: audience
    description: "Target audience: new-hire, team-transfer, contributor (default: new-hire)"
    required: false
  - name: output
    description: "Output format: markdown, confluence (default: markdown)"
    required: false
---

# Onboarding Guide

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly refresh the onboarding material. If you only want review findings, use `/devkit:review-doc`.

## Preflight

Before analyzing the repository or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-onboarding`

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

Load additional guidelines when the repository type is identifiable:

- Frontend -> `skills/_references/guidelines/coding/frontend-nextjs.md`
- Backend -> `skills/_references/guidelines/coding/backend-general.md`
- Design system -> `skills/_references/guidelines/coding/design-system.md`

## Required Child Agents

Run at least these child agents in parallel:

- Architecture analyzer
- Workflow documenter
- Environment setup writer

## Output

Produce a professional onboarding guide with architecture context, setup steps, workflow documentation, and diagrams when they improve comprehension.
