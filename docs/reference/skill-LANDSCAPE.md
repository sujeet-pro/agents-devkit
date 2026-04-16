---
title: Skill Landscape and Gap Analysis
description: Current public ADK skill coverage after the legacy-to-public catalog refactor
order: 2
---

# Skill Landscape and Gap Analysis

This page summarizes what the current public `adk-*` catalog covers and which legacy-era gaps were intentionally closed during the refactor.

## Current Public Coverage

| Area | Public Skills | Notes |
| --- | --- | --- |
| Planning and research | `adk-plan`, `adk-research` | plan-first and evidence-first entrypoints |
| Development and delivery | `adk-build`, `adk-refactor`, `adk-migrate`, `adk-commit` | implementation, structural cleanup, migrations, and change packaging |
| Review | `adk-review-pr`, `adk-review-local-changes`, `adk-address-review-feedback`, `adk-review-docs` | code and docs review surfaces |
| Documentation | `adk-write-docs` | named templates, custom templates, and publishing contract |
| Visual artifacts | `adk-diagram`, `adk-chart`, `adk-design` | system diagrams, data charts, and UI/UX design work |
| Audits and validation | `adk-audit-repo`, `adk-audit-site`, `adk-test` | repo audits, live-site audits, and explicit testing workflows |

## Gaps Closed In This Refactor

The refactor intentionally closed the main capability gaps that were still only present in `legacy-skills/` or external reference repos:

- documentation review is now a public skill via `adk-review-docs`
- named doc templates and custom template loading moved into `adk-write-docs`
- live site and SEO-style audit work moved into `adk-audit-site`
- explicit validation and UAT-style work moved into `adk-test`
- UI and UX direction moved into `adk-design`
- data chart generation moved into `adk-chart`
- commit, PR-summary, and changelog packaging moved into `adk-commit`

## Intentional Simplifications

The public catalog does not keep standalone router, helper, or compatibility-era workflow skills:

- helper behavior now lives in `ai-guidelines/` and copied references
- repo-maintenance wrappers live under `.claude/skills/prj-*`, `.cursor/skills/prj-*`, and `.agents/skills/prj-*`
- legacy connectors and router-era skills remain migration history, not public install surface

## Remaining Intentional Omissions

ADK still does not publish dedicated public skills for every niche workflow. The main missing specialist areas remain:

- CI-specific failure handling
- incident triage and postmortem automation as a standalone task skill
- DB- and infra-specific migration or operations skills

Those are deliberate omissions for now rather than accidental gaps.

## Migration Reference

For the legacy-to-public parity table and deletion criteria, see [Skill Migration Map](./skill-MIGRATION-MAP.md).
