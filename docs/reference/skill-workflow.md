---
title: "workflow"
description: "6-phase workflow framework with complexity-adaptive phase skipping"
skill_name: workflow
category: guideline
workflow_tier: helper
user_invocable: false
---

# workflow

Structured 6-phase workflow that all full-tier DevKit skills follow. Front-loads human interaction into early phases and makes execution autonomous. Phases are adaptive — simpler tasks skip phases based on a complexity table.

## Purpose

- Provide a consistent execution framework across all DevKit task skills
- Ensure human-in-the-loop interaction happens before execution, not during
- Adapt workflow depth to task complexity so trivial tasks skip unnecessary ceremony
- Make execution resumable with progress tracking at wave boundaries
- Define when to load other shared skills based on complexity level

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--complexity` | `trivial` \| `small` \| `medium` \| `large` | auto-detect | Force a specific complexity level instead of auto-detection |
| `--auto` | flag | off | Skip user confirmations in Phases 0, 2, 3. All phases still execute but without waiting for human input |

## Key Behaviors

### Six Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Intent Expansion & Confirmation | Restate goal, show reasoning, list skills/tools needed, estimate complexity, confirm with user |
| 1 | Research & Options Discovery | Search docs and codebase, identify constraints, produce 2-3 concrete approaches |
| 2 | Approach Selection | User picks approach with trade-offs; PE questions resurface for Large tasks |
| 3 | Planning | Decompose into discrete tasks grouped into parallel waves with sequential dependencies |
| 4 | Execute | Implement plan autonomously — waves run sequentially, tasks within waves run in parallel |
| 5 | Validate & Learn | Iteration loop (up to 10 passes) of validation, self-review, simplification, and summary |

### Complexity-Adaptive Phase Skipping

| Complexity | Files | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|------------|-------|---------|---------|---------|---------|---------|---------|
| Trivial | 1 | inline | skip | skip | skip | direct | quick |
| Small | 2-3 | inline | lite | inline | brief | execute | verify |
| Medium | 4-8 | confirm | full | select | full | execute | full |
| Large | >8 | confirm+PE | full | select+PE | full | phased | full (10 iter) |

Phase descriptors: **skip** = not executed; **inline** = abbreviated in conversation; **confirm** = full intent confirmation; **confirm+PE** = with Principal Engineer check; **lite** = quick scan, no deep research; **brief** = high-level plan without wave decomposition; **direct** = execute without wave orchestration; **verify** = single validation pass; **full** = complete as described; **phased** = multiple sequential phases with progress checkpoints.

### Complexity Detection

| Factor | Trivial | Small | Medium | Large |
|--------|---------|-------|--------|-------|
| Files affected | 1 | 2-3 | 4-8 | >8 |
| Architectural decisions needed | No | No | Maybe | Yes |
| Requirements fully clear | Yes | Yes | Mostly | Partially |
| New abstractions required | No | No | Maybe | Yes |
| Discrete sub-tasks | 1 | 2-3 | 4-6 | >6 |

When uncertain, default to Medium.

### Conditional Reference Loading

The workflow defines when other shared skills are loaded based on complexity:

- **Always**: `workflow`, `communication`, `preflight-check`, `interaction`
- **Medium and Large only**: `principal-engineer`, `agentic-teams`
- **When producing output**: `output-format`

### Auto Mode

When `--auto` is passed:

- Phase 0: state intent and complexity, proceed without user confirmation
- Phase 1: execute research normally
- Phase 2: select the recommended approach automatically (first-ranked or lowest-risk)
- Phase 3: generate the plan and proceed without approval pause
- Phases 4-5: execute and validate normally

All phases still execute — auto mode only removes the human confirmation gates.

### Self-Review Principles (Phase 5)

Applied during the Phase 5 iteration loop as non-negotiable quality gates:

- Code must be human-readable, maintainable, and extensible
- Do only the minimum changes required — no gold-plating
- Do not implement features that might be needed in the future
- Three similar lines of code is better than a premature abstraction
- If it works and reads clearly, it is done

## What It Provides

- Consistent phase structure for all task skills to follow
- Complexity detection criteria and adaptive phase skipping rules
- Rules for when to load other shared skills
- Self-review principles for validation
- Auto-mode behavior for CI and scripted invocations
- Output rules: concise by default, markdown format, lead with conclusions, offer to elaborate

## Invoked By

All full-tier task skills invoke this skill, including:

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | always |
| `code-review-repo` | always |
| `code-review-fix` | always |
| `audit` | always |
| `dev-build` | always |
| `dev-refactor` | always |
| `dev-migrate` | always |
| `docs-write` | always |
| `docs-review` | always |
| `docs-repo` | always |
| `docs-crud` | always |
| `docs-confluence` | always |
| `design` | always |
| `plan` | always |
| `spec` | always |
| `research` | always |
| `handoff` | always |
| `interactivity` | always |
