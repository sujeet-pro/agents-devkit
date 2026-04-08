---
title: "test"
description: Interactive user acceptance testing with deliverable extraction and failure diagnosis
skill_name: test
category: task
workflow_tier: abbreviated
---

# test

Extracts testable deliverables from specs/plans and walks you through interactive user acceptance testing (UAT) with automatic failure diagnosis.

## When to Use

- Verify deliverables after implementation
- Walk through acceptance criteria interactively
- Diagnose test failures automatically

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<source>` | file path | (required) | Spec, plan, or requirement document |
| `--scope` | free text | — | Limit testing to specific areas |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Testing interaction style |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

Abbreviated — phases 2–3 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm source and scope |
| 1. Research | Extract testable deliverables from source |
| 4. Execute | Walk through tests interactively, diagnose failures |
| 5. Validate | Produce test report |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `interaction`.

## Examples

```text
/adk:test ./docs/specs/auth-spec.md
/adk:test ./docs/specs/auth-spec.md --scope "login flow"
/adk:test ./.temp/auth-plan/plan.md --mode auto-approve
```
