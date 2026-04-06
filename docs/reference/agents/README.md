---
title: Agent Reference
description: Shared agent definitions used by ADK skills
order: 2
---

# Agent Reference

ADK includes 15 shared agent definitions in the `agents/` directory. These provide reusable system prompts for child agents spawned by skills during execution.

## How Agents Work

Skills launch child agents in parallel during Phase 4 (Execute). Each agent receives focused context for its role and produces findings that the parent skill merges and deduplicates.

## Agent Index

| Agent | Model | Purpose | Used By |
|-------|-------|---------|---------|
| `code-reviewer` | opus | Multi-perspective code review across 10 dimensions | review-pr, review-repo |
| `repo-auditor` | opus | Whole-codebase architecture and maintainability review | review-repo, audit |
| `doc-reviewer` | opus | Technical document review for accuracy and completeness | review-doc, docs-review |
| `research-agent` | opus | Primary-source and implementation research | research |
| `source-publisher` | sonnet | Publish to GitHub, Bitbucket, Confluence, or Google Docs | write, review-pr |
| `consensus-agent` | sonnet | Merge and reconcile multi-agent outputs | team, review-pr |
| `frontend-designer` | opus | Frontend and design system direction | design |
| `pr-fixer` | opus | Read PR comments and apply targeted code fixes | review-fixes |
| `security-reviewer` | opus | Security-focused code review (OWASP, auth, data handling) | audit, review-pr |
| `migration-analyst` | opus | Framework/library migration path analysis | develop |
| `guideline-auditor` | sonnet | Audit guidelines against authoritative sources | audit |
| `code-snippet-agent` | sonnet | Code snippet extraction and formatting for docs | write, docs-repo |
| `intent-analyst` | sonnet | Expand user intent, surface assumptions and routing | use |
| `plan-reviewer` | sonnet | Validate plan completeness, ordering, and estimates | use, plan |
| `progress-tracker` | sonnet | Monitor execution progress, detect stalls and failures | use, plan |

## Standard Team Shapes

Skills compose agents into teams for different types of work:

- **Review Team**: context reader + architecture reviewer + quality reviewer + documentation reviewer + domain specialist
- **Research Team**: landscape mapper + primary-source researcher + implementation researcher + risk analyst
- **Documentation Team**: source analyst + outline editor + fact checker + code/diagram specialist + publisher
- **Security Audit Team**: auth reviewer + data flow analyzer + dependency scanner + OWASP checker
- **Planning Team**: intent analyst + plan reviewer
