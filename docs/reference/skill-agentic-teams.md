---
title: "agentic-teams"
description: "Child-agent contract for parallel agentic teams with standard team shapes"
skill_name: agentic-teams
category: guideline
workflow_tier: helper
user_invocable: false
---

# agentic-teams

Child-agent contract that defines how DevKit skills launch parallel agent teams. Provides standard team shapes for review, research, documentation, diagrams, security, migration, planning, and execution monitoring.

## Purpose

- Define the contract for launching and merging parallel child agents across platforms
- Provide reusable team shapes so skills don't reinvent role assignments
- Ensure child agents receive full task context, not partial session fragments
- Establish merge rules for combining multi-agent results with confidence tracking

## Key Behaviors

### Core Rules

1. Launch at least 2 child agents in parallel for analysis, review, research, writing, or generation work
2. Child agents receive the full task context they need, not partial fragments or hidden session history
3. Keep agent roles distinct so each one owns a perspective or deliverable
4. Merge results in the parent session with explicit confidence notes and duplicate removal
5. If the platform does not support child agents, simulate the same role split sequentially and note that parallel execution was unavailable

### Platform-Specific Rules

| Platform | Behavior |
|----------|----------|
| Claude / Claude Code | Use Agentic Teams or child agents in parallel |
| Codex | Use child agents with full context; keep them focused by role |
| Gemini CLI | Prefer native agents or extensions; fall back to sequential role-based passes |
| Cursor / Cursor CLI | Stay inside Cursor. Use built-in agent/model capabilities only. Do not shell out to external CLIs |
| OpenCode and similar CLIs | Use built-in agent or multi-model features first; call external CLIs only when no equivalent exists and host is not Cursor |

### Standard Team Shapes

| Team | Roles |
|------|-------|
| **Review** | Context reader, Architecture reviewer, Quality reviewer, Documentation reviewer, Domain specialist |
| **Research** | Landscape mapper, Primary-source researcher, Implementation researcher, Risk analyst |
| **Documentation** | Source analyst, Outline editor, Fact checker, Code/diagram specialist, Publisher |
| **Diagram** | Structure agent, Notation agent, Validation agent |
| **Security Audit** | Auth reviewer, Data flow analyzer, Dependency scanner, OWASP checker |
| **Migration** | Usage analyzer, Changelog researcher, Migration planner, Risk assessor |
| **Engineering Workflow** | Analyst, Researcher, Writer, Reviewer |
| **Planning** | Intent analyst, Plan reviewer |
| **Execution Monitoring** | Progress tracker, Domain specialist |

### Merge Rules

- Merge only overlapping findings that describe the same issue
- Preserve minority opinions when they change risk assessment
- Mark single-agent findings as lower confidence until verified
- Prefer official docs, repository code, and existing source comments over generic advice

## What It Provides

- Standard team shapes that skills reference by name when launching child agents
- Platform detection rules so skills adapt to the current execution environment
- Merge protocol for combining multi-agent output into a single coherent result
- Fallback behavior for platforms without native child agent support

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | parallel work needed (medium+ complexity) |
| `code-review-repo` | always (repo reviews use parallel teams) |
| `audit` | parallel work needed |
| `dev-build` | medium+ complexity with multiple waves |
| `dev-refactor` | medium+ complexity |
| `dev-migrate` | always (migrations use the Migration team shape) |
| `docs-write` | medium+ complexity |
| `docs-review` | parallel review needed |
| `docs-repo` | always (repo docs use parallel teams) |
| `design` | parallel work needed |
| `research` | always (research uses the Research team shape) |
| `plan` | always (planning uses the Planning team shape) |
| `workflow` (Phase 1, 4) | medium+ complexity |
