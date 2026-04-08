---
title: "docs-repo"
description: Generate comprehensive repository documentation
skill_name: docs-repo
category: task
workflow_tier: full
---

# docs-repo

Generates comprehensive documentation for an entire repository using pagesmith conventions or plain markdown.

## When to Use

- Bootstrap documentation for a new repository
- Re-generate docs after major codebase changes
- Generate docs for a specific package in a monorepo

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--scope` | `full`, `package <name>` | `full` | Full repo or specific package |
| `--format` | `pagesmith`, `markdown` | auto-detect | Output format |
| `--init` | flag | off | Initialize documentation structure |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm scope and output format |
| 1. Research | Analyze repo structure, detect stack, read existing docs |
| 2. Approach | Present doc structure outline, user approves |
| 3. Planning | Plan pages and sections |
| 4. Execute | Generate documentation files |
| 5. Validate | Self-review for completeness and accuracy |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`, `docs-md`.

## Examples

```text
/adk:docs-repo
/adk:docs-repo --init
/adk:docs-repo --scope package my-library
/adk:docs-repo --format markdown
```
