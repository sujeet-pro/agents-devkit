---
title: "spec"
description: Analyze specs, write specifications, generate checklists, or write constitutions
skill_name: spec
category: task
workflow_tier: full
---

# spec

Writes specifications, analyzes existing ones for completeness and consistency, generates implementation checklists, and creates quality constitutions.

## When to Use

- Write a new specification for a feature or system
- Analyze an existing spec for gaps and ambiguity
- Generate a checklist from a specification
- Create or audit quality standards (constitutions)

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--mode` | `analyze`, `write`, `checklist`, `constitution` | auto-detect | Operation mode |
| `--spec` | file path | — | Existing specification to analyze |
| `--depth` | `quick`, `standard`, `thorough` | `standard` | Depth of analysis/writing |
| `--action` | `create`, `update`, `audit` | `create` | Constitution sub-action |
| `--scope` | path(s) | — | Scope for analysis |
| `--format` | format string | — | Output format |
| `--interactive` | flag | off | Enable interactive mode |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Modes

| Mode | Purpose | Output |
|------|---------|--------|
| `analyze` | Review spec for completeness, consistency, ambiguity | Analysis report |
| `write` | Create a new specification | Specification document |
| `checklist` | Turn a spec into actionable items | Checklist |
| `constitution` | Define quality criteria and standards | Constitution document |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Detect mode, confirm scope |
| 1. Research | Gather context (codebase, existing specs, research) |
| 2. Approach | Present structure/outline (write mode) |
| 3. Planning | Plan sections (write mode) |
| 4. Execute | Write/analyze/generate |
| 5. Validate | Self-review for completeness |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`.

## Examples

```text
/adk:spec --mode write user authentication service specification
/adk:spec --mode analyze ./docs/specs/auth-spec.md
/adk:spec --mode checklist ./docs/specs/auth-spec.md
/adk:spec --mode constitution --action create frontend code quality standards
/adk:spec --mode constitution --action audit ./docs/constitutions/frontend.md
/adk:spec --mode write --depth thorough payment processing specification
```
