---
title: "code-review-repo"
description: Whole-repository review producing a prioritized improvement plan
skill_name: code-review-repo
category: task
workflow_tier: full
---

# code-review-repo

Reviews an entire repository for architecture, code quality, patterns, tech debt, and more. Read-only — produces a prioritized improvement plan without modifying files.

## When to Use

- Onboarding to a new codebase and want to understand its quality
- Periodic codebase health check
- Identifying tech debt and prioritizing fixes

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `[path]` | directory path | repo root | Scope the review to a directory |
| `--focus` | `architecture`, `quality`, `patterns`, `testing`, `security`, `performance`, `deps`, `docs`, `all` | auto-detect | Review dimension(s) |
| `--mode` | `auto`, `standard`, `interactive` | `auto` | Interaction style |
| `--output` | `markdown`, `json` | `markdown` | Output format |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm scope and focus dimensions |
| 1. Research | Scan repo structure, detect stack, load coding guidelines |
| 2. Approach | Present focus dimensions, user selects depth |
| 3. Planning | Break into review waves for parallel agents |
| 4. Execute | Parallel child agents review each dimension |
| 5. Validate | Merge findings, prioritize into improvement plan |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `review-standards`, `principal-engineer`, `agentic-teams`, `interaction`, `coding`.

## Examples

```text
/adk:code-review-repo
/adk:code-review-repo ./src/api --focus architecture
/adk:code-review-repo --focus all --verbosity detailed
/adk:code-review-repo --output json
/adk:code-review-repo --mode interactive
```
