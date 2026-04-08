---
title: "dev-commit"
description: Smart commit messages and PR descriptions — auto-detects convention
skill_name: dev-commit
category: task
workflow_tier: full
---

# dev-commit

Generates smart commit messages and PR descriptions. Auto-detects your project's commit convention (conventional commits, gitmoji, or plain).

## When to Use

- Create a commit with an auto-generated message
- Generate a PR description from branch changes

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--auto` | flag | off | Skip confirmations |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameters |

## Workflow

Abbreviated workflow — skips approach selection and detailed planning.

| Phase | Action |
|-------|--------|
| 0. Intent | Detect staged changes, identify commit convention |
| 1. Research | Analyze diff, read recent commit history for style |
| 4. Execute | Generate commit message, create commit |
| 5. Validate | Verify commit was created successfully |

## Examples

```text
/adk:dev-commit
/adk:dev-commit --auto
```
