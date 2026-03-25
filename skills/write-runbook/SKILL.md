---
name: write-runbook
description: Use when you need to draft or directly revise a professional operational runbook for a service, deployment flow, or incident response path
user_invocable: true
arguments:
  - name: service
    description: "Service name or path to the service root directory"
    required: true
  - name: scope
    description: "Runbook scope: full, incident-response, deployment (default: full)"
    required: false
---

# Operational Runbook

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly improve the runbook. If you only want review comments, use `/devkit:review-doc`.

## Preflight

Before analyzing the service or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-runbook`

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/coding/backend-general.md`

## Required Child Agents

Run at least these child agents in parallel:

- Infrastructure analyzer
- Failure mode researcher
- Procedure writer

## Output

Produce a professional runbook with service context, deployment and rollback steps, monitoring guidance, incident response procedures, and diagrams when they clarify the topology.
