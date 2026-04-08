---
title: "workflow"
description: 6-phase workflow framework with complexity-adaptive phase skipping
skill_name: workflow
category: guideline
workflow_tier: helper
user_invocable: false
---

# workflow

Defines the 6-phase workflow framework that all full-tier skills follow. The invoking skill runs the phases — `workflow` provides the structure and rules.

## Purpose

Provides phase definitions, complexity-adaptive skipping, artifact management (`.temp/<task-slug>/`), and rules for which helper skills to load at each phase.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--complexity` | `trivial`, `small`, `medium`, `large` | auto-detect | Override complexity estimation |
| `--auto` | flag | off | Skip all human confirmations |

## Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Intent Expansion | Restate goal, surface assumptions, estimate complexity |
| 1 | Research & Options | Gather context, explore approaches |
| 2 | Approach Selection | Present options, user selects |
| 3 | Planning | Break into tasks/waves |
| 4 | Execute | Implement the plan |
| 5 | Validate & Learn | Self-review, verify, simplify |

## Complexity Skipping

| Complexity | Phases Run | Example |
|------------|-----------|---------|
| Trivial | 0 → 4 | "what's the git status?" |
| Small | 0 → 1 → 4 → 5 | "rename this variable" |
| Medium | 0 → 1 → 2 → 4 → 5 | "review this PR" |
| Large | All 6 phases | "implement auth with OAuth2" |

## Helper Loading Rules

| Condition | Helpers Loaded |
|-----------|----------------|
| Always | `workflow`, `communication`, `preflight-check`, `interaction` |
| Complexity >= Medium | Add `principal-engineer`, `agentic-teams` |
| When producing output | Add `output-format` |

## Invoked By

All full-tier task skills. Not user-invocable.
