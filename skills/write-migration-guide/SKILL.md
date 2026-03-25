---
name: write-migration-guide
description: Use when you need to draft or directly revise a professional migration guide mapped to real codebase files for a framework, library, or version upgrade
user_invocable: true
arguments:
  - name: from
    description: "Current version or framework (e.g., 'React 17', 'Next.js 13', 'Spring Boot 2.x')"
    required: true
  - name: to
    description: "Target version or framework (e.g., 'React 18', 'Next.js 14', 'Spring Boot 3.x')"
    required: true
  - name: scope
    description: "Migration scope: full, incremental (default: full)"
    required: false
---

# Migration Guide

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should produce or directly update the migration guide. If you only want review findings, use `/devkit:review-doc`.

## Preflight

Before analyzing the codebase or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-migration-guide`

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/coding/general.md`

Load additional coding guidelines when the migration involves a known domain:

- Frontend -> `skills/_references/guidelines/coding/frontend-nextjs.md`
- Backend -> `skills/_references/guidelines/coding/backend-general.md`
- Library -> `skills/_references/guidelines/coding/js-ts-library.md`

## Required Child Agents

Run at least these child agents in parallel:

- Usage analyzer
- Changelog researcher
- Migration planner
- Risk assessor

## Output

Produce a professional migration guide with file-mapped steps, verification guidance, risk register, and rollback notes.
