---
title: "agentic-teams"
description: Child-agent contract and standard team shapes for parallel work
skill_name: agentic-teams
category: guideline
workflow_tier: helper
user_invocable: false
---

# agentic-teams

Defines the contract for parallel child agents and provides standard team shapes for review, research, documentation, and other multi-agent workflows.

## Purpose

Ensures consistent agent spawning patterns: each child gets full context, results are merged with deduplication, and minority findings are preserved when risk differs.

## Agent Scaling

| Complexity | Agent Count |
|------------|-------------|
| Small | 1 (no parallelism) |
| Medium | 2–3 parallel agents |
| Large | 4–5 parallel agents |

## Standard Team Shapes

| Shape | Roles |
|-------|-------|
| **Review** | Context reader, Architecture reviewer, Quality reviewer, Documentation reviewer, Domain specialist |
| **Research** | Landscape mapper, Primary-source researcher, Implementation researcher, Risk analyst |
| **Documentation** | Source analyst, Outline editor, Fact checker, Code/diagram specialist, Publisher |
| **Diagram** | Structure agent, Notation agent, Validation agent |
| **Security** | Auth reviewer, Data flow analyzer, Dependency scanner, OWASP checker |
| **Migration** | Usage analyzer, Changelog researcher, Migration planner, Risk assessor |
| **Engineering** | Analyst, Researcher, Writer, Reviewer |
| **Planning** | Intent analyst, Plan reviewer |
| **Execution** | Progress tracker, Domain specialist |

## Merge Rules

- Deduplicate overlapping findings
- Preserve minority findings when risk assessment differs
- Lower confidence for single-agent findings
- Prefer primary sources over secondary

## Invoked By

Loaded by the workflow helper set for Medium and Large complexity tasks that benefit from parallel work.
