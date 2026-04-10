---
title: Research & Planning
description: Research topics, create implementation plans, and write specifications
order: 5
---

# Research & Planning

These skills work best as a chain: use `research` when you need evidence, `spec` when you need a durable requirements artifact, and `plan` when you know the direction and want an executable sequence of work.

> **Quick start:** when you are still exploring the problem, begin with `/adk:research <prompt-text>`. When the direction is already clear, jump straight to `/adk:plan --mode write <prompt-text>`.

## Scenarios

- [Research A Topic](#research-a-topic)
- [Turn Research Into A Plan](#turn-research-into-a-plan)
- [Execute Or Track A Plan](#execute-or-track-a-plan)
- [Write Or Analyze A Specification](#write-or-analyze-a-specification)
- [Create Governance Rules](#create-governance-rules)

---

## Research A Topic

Use `research` when the job is understanding, comparing, or gathering source-backed evidence.

```text
/adk:research <prompt-text>
/adk:research Next.js App Router migration patterns
/adk:research <prompt-text> --deep
/adk:research <prompt-text> --save <path>
```

`--deep` is the right upgrade when you need broader evidence, risk analysis, and synthesis. `--save` is useful when the research should become input for later skills.

---

## Turn Research Into A Plan

Use `plan` when you want ADK to convert the current understanding into a sequence of steps.

```text
/adk:plan --mode brainstorm <prompt-text>
/adk:plan --mode write <prompt-text>
/adk:plan --mode write --spec <path> <prompt-text>
```

Brainstorm mode helps when the approach itself is still open. Write mode is for turning a chosen direction into a concrete implementation plan. Add `--spec` when a formal spec already exists and should constrain the plan.

---

## Execute Or Track A Plan

Once the plan exists, stay in the `plan` skill for execution and progress tracking.

```text
/adk:plan --mode execute --plan <path>
/adk:plan --mode track --plan <path>
```

Use execute mode when the work is approved and ready to run. Use track mode when you want an up-to-date read on progress, blockers, and remaining work without re-planning from scratch.

---

## Write Or Analyze A Specification

Use `spec` when the missing artifact is a durable requirements document or a formal analysis of an existing spec.

```text
/adk:spec --mode write <prompt-text>
/adk:spec --mode write --depth thorough <prompt-text>
/adk:spec --mode analyze <path>
/adk:spec --mode checklist <path>
```

Write mode creates the specification, analyze mode audits an existing one, and checklist mode turns the requirements into a quality checklist you can use as a validation gate.

---

## Create Governance Rules

Use constitution mode when the output should be a durable set of principles or quality gates for later work.

```text
/adk:spec --mode constitution --action create <prompt-text>
```

This is useful when a team needs explicit non-negotiables that future planning, implementation, and review workflows should honor.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Research and compare options | `research` | `<prompt-text>`, `--deep`, `--save` |
| Brainstorm or write a plan | `plan` | `--mode brainstorm`, `--mode write`, `--spec` |
| Execute or track a plan | `plan` | `--mode execute`, `--mode track`, `--plan` |
| Write a new specification | `spec` | `--mode write`, `--depth` |
| Analyze or checklist an existing spec | `spec` | `--mode analyze`, `--mode checklist`, `<path>` |
| Define governance or quality gates | `spec` | `--mode constitution`, `--action` |

## Related Skills

- **[`dev-build`](/reference/skill-dev-build/)** when the plan is ready to turn into implementation.
- **[`docs-write`](/reference/skill-docs-write/)** when the research or spec should be published as a polished document.
- **[`audit`](/reference/skill-audit/)** when you want to check existing code against the standards or intent you just documented.
