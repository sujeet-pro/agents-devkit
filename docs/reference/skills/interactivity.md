---
title: "interactivity"
description: Agent-first interaction orchestration with optional external TUI
skill_name: interactivity
category: task
workflow_tier: full
user_invocable: true
---

# interactivity

Structured user interaction orchestration for option selection, data capture, edits, and human approval. Inline-first with optional external TUI for complex forms.

## When to Use

- Complex option selection with many choices
- Structured data capture (forms)
- Edit/review loops with approval
- When inline prompts aren't sufficient

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<goal>` | free text | (required) | Interaction goal description |
| `--mode` | `auto`, `options`, `collect`, `edit`, `review` | `auto` | Interaction mode |
| `--tui` | `true`, `false` | `false` | Use external TUI for complex interactions |
| `--form` | file path | — | Form definition file |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Modes

| Mode | Purpose |
|------|---------|
| `auto` | Auto-detect from context |
| `options` | Present choices, get selection |
| `collect` | Gather structured data |
| `edit` | Edit/revise content |
| `review` | Review and approve/reject |

## Workflow

Full 6-phase workflow.

## Examples

```text
/adk:interactivity select a deployment strategy --mode options
/adk:interactivity collect project requirements --mode collect --form ./templates/requirements.md
/adk:interactivity review the API design --mode review
```
