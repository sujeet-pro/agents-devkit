---
title: Agent Reference
description: 15 shared agent definitions used by ADK skills
order: 2
---

# Agent Reference

ADK includes 15 shared agent definitions in the `agents/` directory. These provide reusable system prompts for child agents spawned by skills during execution.

## How Agents Work

Skills launch child agents in parallel during Phase 4 (Execute). Each agent receives focused context for its role and produces findings that the parent skill merges and deduplicates.

## Agent Index

| Agent | Purpose |
| ----- | ------- |
| `code-reviewer` | Multi-perspective code review |
| `repo-auditor` | Whole-codebase architecture and maintainability review |
| `doc-reviewer` | Technical document review |
| `research-agent` | Primary-source and implementation research |
| `source-publisher` | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `consensus-agent` | Merge and reconcile multi-agent outputs |
| `frontend-designer` | Frontend and design system direction |
| `pr-fixer` | Read PR comments and apply targeted code fixes |
| `security-reviewer` | Security-focused code review (OWASP, auth, data) |
| `migration-analyst` | Framework/library migration analysis |
| `guideline-auditor` | Audit guidelines against authoritative sources |
| `code-snippet-agent` | Code snippet extraction and formatting |
| `intent-analyst` | Expand user intent, assumptions, complexity, and routing |
| `plan-reviewer` | Review plans for completeness and sequencing |
| `progress-tracker` | Monitor execution progress, stalls, and recovery |

## Standard Team Shapes

Skills compose agents into teams for different types of work:

### Review Team

context reader + architecture reviewer + quality reviewer + documentation reviewer + domain specialist

### Research Team

landscape mapper + primary-source researcher + implementation researcher + risk analyst

### Documentation Team

source analyst + outline editor + fact checker + code/diagram specialist + publisher

### Security Audit Team

auth reviewer + data flow analyzer + dependency scanner + OWASP checker

### Planning Team

intent analyst + plan reviewer
