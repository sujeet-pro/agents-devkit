---
title: Skill Landscape and Gap Analysis
description: Popular software-engineering agent skills benchmarked against ADK
order: 2
---

# Skill Landscape and Gap Analysis

This document benchmarks ADK skills against commonly used software-engineering agent workflows and recommends gaps to close.

## External Sources Used

Primary (official):
- [Anthropic Claude Code - How it works](https://code.claude.com/docs/en/how-claude-code-works.md)
- [GitHub Copilot cloud agent - overview](https://docs.github.com/en/copilot/concepts/about-copilot-coding-agent)
- [GitHub Copilot cloud agent - MCP extension](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/extending-copilot-coding-agent-with-mcp)

Open-source ecosystem signal:
- [VoltAgent awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands)
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)

## What ADK Already Covers Well

ADK already has strong coverage for the highest-frequency software engineering workflows:

- implementation and debugging (`dev-build`)
- refactoring (`dev-refactor`)
- migration (`dev-migrate`)
- code review (`code-review-pr`, `code-review-repo`, `code-review-fix`)
- planning/specification (`plan`, `spec`)
- documentation (`docs-write`, `docs-review`, `docs-repo`, `docs-crud`, `docs-confluence`)
- research (`research`)
- testing/UAT (`test`)
- design and diagrams (`design`, `diagram-*`)
- setup, handoff, project lifecycle (`setup`, `handoff`, `project`)
- orchestration and routing (`use`, `dev`, `docs`, `code-review`, `diagram`, `team`)

## Coverage Matrix (Popular vs Current ADK)

| Skill area | Industry prevalence | ADK status | Notes |
|---|---|---|---|
| Implement/fix/debug code | Core | Strong | Covered by `dev-build` |
| Repo research and context gathering | Core | Strong | Covered by `research`, `use` |
| Plan-first execution | Core | Strong | Covered by `use`, `plan`, `workflow` |
| Code review | Core | Strong | Covered by review skill family |
| Refactor/tech debt | Core | Strong | Covered by `dev-refactor` |
| Migration/upgrade | Core | Strong | Covered by `dev-migrate` |
| Docs authoring/review | Core | Strong | Covered by docs skill family |
| PR/git automation | Core | Strong | Covered by `dev-commit` |
| Security audit and remediation | Core | Partial | `audit` is strong; dedicated fix flow can be stronger |
| CI/CD and release automation | Core | Partial | Setup exists; no dedicated CI/release task skill |
| Observability/incident triage | Emerging-core | Gap | No dedicated incident workflow skill |
| Dependency update/remediation | Emerging-core | Partial | `deps-tracker` is source-tracking, not package remediation |
| Performance optimization workflow | Emerging-core | Partial | In `audit`; no dedicated implement-optimization skill |
| Data/DB migration and query tuning | Specialized but common | Gap | No DB-focused task skill |
| Cloud/IaC operations | Specialized but common | Gap | No dedicated infra/deploy task skill |

## Philosophy Compliance Review

Assessment against the required philosophy:

1. **Self-contained skills with fallback guidance**  
   Status: **Mostly compliant**. Most full task skills include `Shared Skills` + `Inline Fallback`.

2. **One skill, one responsibility**  
   Status: **Mostly compliant**. Routing vs task split is clear for major categories.

3. **Human-in-the-loop + re-validation workflow**  
   Status: **Strong**. This is explicit in `use`, `plan`, and helper guidelines.

4. **Principal Engineer option-first approach**  
   Status: **Strong at framework level**, **mixed at execution consistency**. The pattern exists in shared guidance and many full skills, but should be uniformly enforced by policy checks.

## Recommended Skill Additions (High Priority)

To align with popular engineering usage and automation goals:

1. `adk-ci` (task)  
   Focus: CI failures, flaky tests, lint/build breakages, pipeline hardening.

2. `adk-release` (task)  
   Focus: release notes, version bump strategy, changelog generation, release validation checklist.

3. `adk-incident` (task)  
   Focus: incident triage, log/signal correlation, mitigation plan, postmortem draft.

4. `adk-deps-remediate` (task)  
   Focus: dependency update planning, breakage risk scoring, automated fix+verify loop.

5. `adk-db` (task)  
   Focus: schema migration planning, query optimization, data backfill and rollback safety.

## Recommended Router Expansions

Current router categories are strong for `dev`, `docs`, `code-review`, and `diagram`.
For consistency, add:

- `adk-quality` router -> `audit`, `test`, `incident`, `deps-remediate`
- `adk-delivery` router -> `ci`, `release`
- `adk-platform` router -> `setup`, future `db`, future `infra`

## Tool/Connector Preference Policy (Proposed Standard)

For external systems, use this order:

1. standard connectors in this repo (`github`, `bitbucket`, `confluence`, `jira`)
2. first-party CLI
3. first-party MCP
4. first-party API
5. third-party MCP/CLI/API fallback

This policy should be centralized in one shared routing reference and propagated to all task skills.
