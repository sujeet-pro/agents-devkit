---
title: "interaction"
description: Inline interaction protocols for confirmations, selections, and approvals
skill_name: interaction
category: guideline
workflow_tier: helper
user_invocable: false
---

# interaction

Inline-only interaction protocols (no TTY) for structured prompts and compact user responses throughout the workflow.

## Purpose

Defines standard protocols for human-in-the-loop interactions: intent confirmation, approach selection, plan approval, review findings, and progress dashboards.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `-i` | flag | on | Inline mode (default, no external UI) |
| `--auto` | flag | off | Skip all confirmations |

## Protocols

| Protocol | Used In | User Response Format |
|----------|---------|---------------------|
| Intent Confirmation | Phase 0 | "yes" / "no" / corrections |
| Approach Selection | Phase 2 | Number, "mix", or custom |
| Plan Approval | Phase 3 | "approve" / "reject" / edits |
| Review Findings | Phase 4-5 | "accept" / "reject" / "edit" per finding |
| Progress Dashboard | Phase 4 | Wave status display |

## Invoked By

All full-tier task skills via the workflow helper set ("Always" tier). Skipped when `--auto` is passed.
