---
title: "workspace-conventions"
description: Workspace file conventions — temp files, diagram output, artifact locations
skill_name: workspace-conventions
category: guideline
workflow_tier: helper
user_invocable: false
---

# workspace-conventions

Defines where skills put temporary files, diagram outputs, chart outputs, and other artifacts.

## Purpose

Ensures consistent file placement across all skills. Prevents file clutter and provides predictable locations for generated artifacts.

## Conventions

| Artifact | Location | Gitignored |
|----------|----------|------------|
| Temporary/working files | `.temp/<task-slug>/` | Yes |
| Diagram sources | `docs/diagrams/` or alongside doc | No |
| Diagram renders | `docs/diagrams/` | No |
| Chart outputs | `docs/charts/` or alongside doc | No |
| Research artifacts | `.temp/<task-slug>/research/` | Yes |

## Task Slug Naming

Task slugs are kebab-case derived from the task description, used to namespace `.temp/` directories.

## .gitignore Management

Skills that create `.temp/` directories ensure `.temp/` is in `.gitignore`.

## Invoked By

All skills that create files: diagram skills, `docs-write`, `docs-repo`, `docs-crud`, `plan`, `spec`, `research`, `handoff`.
