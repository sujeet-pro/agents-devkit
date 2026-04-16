---
title: "Skill Reference"
description: "Complete reference for ADK skills — parameters, workflow contracts, and examples sourced from current SKILL.md files"
order: 1
---

# Skill Reference

Every page in this section is derived from the live `SKILL.md` file for that skill. Use the individual reference pages when you want the exact flag surface, workflow contract, helper-skill composition, and output expectations for the current repository state.

## Strategy and Governance

- [Skill Landscape and Gap Analysis](../skill-LANDSCAPE.md)
- [Skill Inspiration Map](../skill-INSPIRATION-MAP.md)
- [Category Routing Map](../skill-CATEGORY-ROUTING.md)
- [Skill Migration Map](../skill-MIGRATION-MAP.md)

## Common Parameters

Many user-invocable skills expose some combination of the following controls:

| Parameter | What it usually does |
|-----------|----------------------|
| `--help` | Print the embedded skill reference and stop |
| `--scope` | Limit analysis or execution to one path, surface, or target area |
| `--focus` | Keep the primary review, audit, or design lens explicit |
| `--action` | Choose a lifecycle action such as create, update, review, or publish |

## Planning & Research

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-brainstorm`](../skill-adk-brainstorm.md) | full | Run iterative brainstorming to narrow options, question assumptions, choose blast radius, and route into the right implementation or documentation skill. Use when a task needs design closure before work begins | [Details ->](../skill-adk-brainstorm.md) |
| [`adk-plan`](../skill-adk-plan.md) | full | Create an executable implementation plan with scoped files, risks, and validation checkpoints. Use when a request needs a reviewable plan before code or docs changes | [Details ->](../skill-adk-plan.md) |
| [`adk-research`](../skill-adk-research.md) | full | Run structured technical research with repo evidence, primary sources, and explicit uncertainty. Use when a task depends on external facts or upstream behavior | [Details ->](../skill-adk-research.md) |

## Development & Delivery

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-build`](../skill-adk-build.md) | full | Implement or enhance code with a plan, focused research, and validation. Use when building a feature, fixing a bug, or improving behavior in an existing codebase | [Details ->](../skill-adk-build.md) |
| [`adk-refactor`](../skill-adk-refactor.md) | full | Improve code structure without changing intent. Use when behavior should stay the same but readability, boundaries, or maintainability should improve | [Details ->](../skill-adk-refactor.md) |
| [`adk-migrate`](../skill-adk-migrate.md) | full | Upgrade frameworks, libraries, or patterns with breaking-change analysis and staged validation. Use when a dependency, framework, or architecture migration is the main task | [Details ->](../skill-adk-migrate.md) |
| [`adk-commit`](../skill-adk-commit.md) | abbreviated | Generate accurate commit messages, PR descriptions, or changelog summaries from real repository changes. Use when release communication is the main task | [Details ->](../skill-adk-commit.md) |

## Review

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-review-pr`](../skill-adk-review-pr.md) | full | Review a pull request for correctness, regression risk, and missing validation. Use when reviewing a branch or hosted pull request before merge | [Details ->](../skill-adk-review-pr.md) |
| [`adk-review-local-changes`](../skill-adk-review-local-changes.md) | full | Review local uncommitted or local branch changes before commit or PR. Use when the work exists locally and needs a pre-submit review | [Details ->](../skill-adk-review-local-changes.md) |
| [`adk-address-review-feedback`](../skill-adk-address-review-feedback.md) | full | Fix review feedback, update the code, and confirm the comments are addressed. Use when a PR or local review already produced actionable feedback | [Details ->](../skill-adk-address-review-feedback.md) |
| [`adk-review-docs`](../skill-adk-review-docs.md) | full | Review documentation for accuracy, completeness, clarity, style, and example quality. Use when documentation review itself is the main task | [Details ->](../skill-adk-review-docs.md) |

## Documentation

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-write-docs`](../skill-adk-write-docs.md) | full | Write, update, improve, or publish engineering documentation using named templates or a custom template URL or file. Use when documentation is the main deliverable | [Details ->](../skill-adk-write-docs.md) |

## Visuals & Design

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-diagram`](../skill-adk-diagram.md) | full | Create or update markdown docs with editable diagram source files across Mermaid, Excalidraw, Draw.io, and Graphviz, rendered via diagramkit. Use when a document needs a maintained in-repo diagram | [Details ->](../skill-adk-diagram.md) |
| [`adk-chart`](../skill-adk-chart.md) | full | Create data charts from source data or documented metrics with reusable data files and rendered assets. Use when the deliverable is a chart rather than a system diagram | [Details ->](../skill-adk-chart.md) |
| [`adk-design`](../skill-adk-design.md) | full | Design, audit, or polish interfaces with clear UX goals, accessibility constraints, and implementation realism. Use when UI or UX quality is the main job | [Details ->](../skill-adk-design.md) |

## Audits & Testing

| Skill | Tier | Description | Reference |
|-------|------|-------------|-----------|
| [`adk-audit-repo`](../skill-adk-audit-repo.md) | full | Audit a repository for correctness risks, maintainability issues, and validation gaps. Use when you need a prioritized improvement list instead of a line-by-line PR review | [Details ->](../skill-adk-audit-repo.md) |
| [`adk-audit-site`](../skill-adk-audit-site.md) | full | Audit a live site or webapp for SEO, performance, accessibility, security signals, metadata, and broken-user-flow issues. Use when the job is site health rather than repo health | [Details ->](../skill-adk-audit-site.md) |
| [`adk-test`](../skill-adk-test.md) | full | Verify behavior through acceptance, regression, or webapp-focused testing with explicit pass criteria and fresh evidence. Use when validation itself is the main task | [Details ->](../skill-adk-test.md) |

## Self-Sufficient Pattern

Task skills are designed to stay usable even in partial installations. They prefer shared helper skills when those helpers are available, but the inline fallback summaries inside each `SKILL.md` preserve the critical rules for workflow, communication, formatting, and validation.
