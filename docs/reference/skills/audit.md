---
title: "audit"
description: Codebase, security, performance, or dependency audit — auto-detects focus
skill_name: audit
category: task
workflow_tier: full
---

# audit

Performs codebase, security, performance, or dependency audits. Read-only — produces findings and recommendations without modifying code.

## When to Use

- Security vulnerability assessment
- Performance bottleneck identification
- Dependency health check (outdated, vulnerable, unused)
- General code quality audit

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--focus` | `codebase`, `security`, `performance`, `dependency`, `all` | auto-detect | Audit dimension(s) |
| `--scope` | path(s) | repo root | Limit audit to specific directories |
| `--format` | `markdown`, `pr` | `markdown` | Output format |
| `--publish` | flag | off | Post findings to a platform |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Detect focus from keywords, confirm scope |
| 1. Research | Scan codebase, detect stack, load coding guidelines |
| 2. Approach | Present audit dimensions, user selects focus |
| 3. Planning | Break into audit waves for parallel agents |
| 4. Execute | Parallel child agents audit each dimension |
| 5. Validate | Merge findings, assign severity, prioritize |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `review-standards`, `principal-engineer`, `agentic-teams`, `interaction`, `coding`.

## Examples

```text
/adk:audit --focus security
/adk:audit --focus performance --scope src/api/
/adk:audit --focus dependency
/adk:audit --focus all --verbosity detailed
/adk:audit --focus security --format pr --publish
```
