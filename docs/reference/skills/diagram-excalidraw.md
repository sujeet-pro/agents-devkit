---
title: "diagram-excalidraw"
description: Create Excalidraw diagrams — hand-drawn style with JSON format reference
skill_name: diagram-excalidraw
category: task
workflow_tier: full
---

# diagram-excalidraw

Creates Excalidraw diagrams in the hand-drawn style. Produces `.excalidraw` JSON files with optional rendering via diagramkit.

## When to Use

- Architecture overviews with an approachable, whiteboard style
- Freeform layouts that don't fit strict diagram types
- Presentations and non-technical stakeholder communication
- Cloud architecture with themed palettes (AWS, Azure, GCP, K8s)

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--render` | flag | auto | Render to image |
| `--format` | `svg`, `png` | `svg` | Render output format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--palette` | `default`, `aws`, `azure`, `gcp`, `k8s` | `default` | Color palette for themed diagrams |
| `--help` | flag | — | Show parameters |

## Workflow

Phases 2–3 skipped.

| Phase | Action |
|-------|--------|
| 0. Intent | Confirm diagram scope |
| 1. Research | Load Excalidraw JSON format reference |
| 4. Execute | Generate `.excalidraw` JSON, render if requested |
| 5. Validate | Verify JSON structure is valid |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer`, `agentic-teams`, `interaction`, `workspace-conventions`.

## Examples

```text
/adk:diagram-excalidraw system architecture with frontend, API, and database
/adk:diagram-excalidraw --palette aws AWS infrastructure with VPC and load balancer
/adk:diagram-excalidraw --palette k8s Kubernetes cluster architecture
/adk:diagram-excalidraw --render --format png --theme dark microservices overview
```
