---
title: 'agentic-teams'
description: 'Child-agent contract for parallel agentic teams. Standard team shapes for review, research, docs, diagrams, security, migration, planning'
skill_name: agentic-teams
category: guideline
workflow_tier: helper
user_invocable: false
---

# agentic-teams

`agentic-teams` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`agentic-teams` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

This helper does not expose a broad user-facing parameter surface beyond the narrow controls in `SKILL.md`. In practice, task skills load it indirectly and supply the context it needs.

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


## Additional Reference

### Core Rules

1. Launch at least 2 child agents in parallel for analysis, review, research, writing, or generation work.
2. Child agents receive the full task context they need, not partial fragments or hidden session history.
3. Keep agent roles distinct so each one owns a perspective or deliverable.
4. Merge results in the parent session with explicit confidence notes and duplicate removal.
5. If the platform does not support child agents, simulate the same role split sequentially and say that parallel execution was unavailable.

### Platform Rules

- **Claude / Claude Code**: use Agentic Teams or child agents in parallel.
- **Codex**: use child agents with full context; keep them focused by role.
- **Gemini CLI**: prefer Gemini's native agents or extensions. If native child agents are unavailable, run role-based passes sequentially.
- **Cursor / Cursor CLI**: stay inside Cursor. Use Cursor's built-in agent/model capabilities only. Do **not** shell out to `claude`, `codex`, or `gemini` from Cursor.
- **OpenCode and similar CLIs**: use built-in agent or multi-model features first; only call external CLIs when the current tool has no equivalent and the host is not Cursor.

### Standard Team Shapes

### Review Team

- **Context reader**: reads the diff, source material, and existing comments.
- **Architecture reviewer**: checks boundaries, coupling, migrations, and long-term maintainability.
- **Quality reviewer**: checks correctness, security, performance, tests, and code patterns.
- **Documentation reviewer**: checks docs, naming, comments, and reviewer ergonomics.
- **Domain specialist**: frontend, backend, design system, docs, or platform-specific concerns.

### Research Team

- **Landscape mapper**: frames the problem and subtopics.
- **Primary-source researcher**: collects official docs, specs, and maintainers' guidance.
- **Implementation researcher**: checks real repositories, examples, and migration notes.
- **Risk analyst**: finds edge cases, tradeoffs, and open questions.

### Documentation Team

- **Source analyst**: reads code, docs, tickets, or external source material.
- **Outline editor**: designs the information architecture.
- **Fact checker**: verifies claims, versions, links, and examples.
- **Code or diagram specialist**: prepares examples and visuals.
- **Publisher**: prepares markdown plus source-specific output such as Confluence or Google Docs.

### Diagram Team

- **Structure agent**: identifies entities, flows, and grouping.
- **Notation agent**: chooses Mermaid, Excalidraw, or draw.io.
- **Validation agent**: checks renderability, naming, and consistency with the written narrative.

### Security Audit Team

- **Auth reviewer**: authentication and authorization flows, session management, JWT handling.
- **Data flow analyzer**: traces sensitive data through the system, checks encryption, logging, exposure.
- **Dependency scanner**: checks for known CVEs, outdated packages, license issues.
- **OWASP checker**: systematic OWASP Top 10 review against the codebase.

### Migration Team

- **Usage analyzer**: finds all usage of the source framework/library in the codebase.
- **Changelog researcher**: reads official migration guides, changelogs, and breaking change lists.
- **Migration planner**: maps breaking changes to specific files and creates step-by-step plan.
- **Risk assessor**: evaluates effort, risk, and identifies codemods or automation available.

### Engineering Workflow Team

- **Analyst**: reads source material (PR comments, git history, codebase structure, configs).
- **Researcher**: gathers authoritative sources (official docs, specs, community best practices).
- **Writer**: produces the deliverable (ADR, runbook, changelog, onboarding guide, API docs).
- **Reviewer**: checks accuracy, completeness, and actionability of the output.

### Planning Team

- **Intent analyst**: analyzes user prompt, surfaces implicit requirements and ambiguities, maps to DevKit skills, estimates complexity, and applies Principal Engineer questioning.
- **Plan reviewer**: validates implementation plan completeness, wave ordering, effort estimates, and requirement coverage. Flags missing tasks, unrealistic estimates, and dependency violations.

### Execution Monitoring Team

- **Progress tracker**: monitors task completion across waves, detects stalls and failures, categorizes failure types, and suggests recovery strategies.
- **Domain specialist**: the relevant domain agent for the task type (adk-code-reviewer for code changes, adk-doc-reviewer for documentation, adk-security-reviewer for security-sensitive work, etc.).

### Merge Rules

- Merge only overlapping findings that describe the same issue.
- Preserve minority opinions when they change risk assessment.
- Mark single-agent findings as lower confidence until verified.
- Prefer official docs, repository code, and existing source comments over generic advice.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
