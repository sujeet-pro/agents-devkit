---
title: "design"
description: UI/UX design direction with HTML previews or visual audit
skill_name: design
category: task
workflow_tier: full
---

# design

Creates UI/UX design directions with 5 HTML preview variations, or audits visual design quality. Produces distinctive, production-grade design options.

## When to Use

- Design a new UI component or page
- Create multiple design variations to choose from
- Audit existing UI for accessibility and visual quality

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--focus` | `ui`, `ux`, `visual`, `accessibility` | `ui` | Design focus area |
| `--framework` | free text | auto-detect | Target framework (React, Vue, etc.) |
| `--style` | free text | — | Design style guidance |
| `--theme` | free text | — | Theme constraints |
| `--action` | `design`, `audit` | `design` | Design or audit mode |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm design requirements and constraints |
| 1. Research | Analyze existing UI patterns in the codebase |
| 2. Approach | Present design directions |
| 3. Planning | Plan 5 variations |
| 4. Execute | Generate 5 HTML preview variations (parallel agents) |
| 5. Validate | Accessibility check, responsiveness verification |

For `--action audit`: delegates to `code-review-pr --focus ui`.

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`.

## Examples

```text
/adk:design login page for a SaaS application
/adk:design --focus accessibility dashboard component
/adk:design --action audit review the settings page UI
/adk:design --framework react --style "minimal, dark theme" navigation sidebar
```
