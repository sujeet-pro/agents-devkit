---
title: "diagram-drawio"
description: Create draw.io diagrams — precise layout with rich icon library
skill_name: diagram-drawio
category: task
workflow_tier: full
---

# diagram-drawio

Creates draw.io XML diagrams with precise layout and rich icon libraries for network topology, enterprise architecture, and BPMN process flows.

## When to Use

- Network topology diagrams with exact positioning
- Enterprise architecture with AWS, Azure, GCP icons
- BPMN process flows
- Diagrams that need to be edited later in the draw.io editor

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--render` | flag | auto | Render to image |
| `--format` | `svg`, `png` | `svg` | Render output format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm diagram scope |
| 1. Research | Load draw.io XML format and icon references |
| 4. Execute | Generate `.drawio` XML, render if requested |
| 5. Validate | Verify XML structure is valid |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `workspace-conventions`.

## Examples

```text
/adk:diagram-drawio network topology with firewalls and load balancers
/adk:diagram-drawio BPMN order fulfillment process
/adk:diagram-drawio --render --format png enterprise architecture
```
