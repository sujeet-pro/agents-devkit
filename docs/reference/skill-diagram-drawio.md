---
title: "diagram-drawio"
description: Create draw.io diagrams — precise layout with rich icon library for network topology, enterprise architecture, and BPMN
skill_name: diagram-drawio
category: task
workflow_tier: full
user_invocable: true
---

# diagram-drawio

Generate precise, professionally-styled diagrams as `.drawio` XML files. Rich shape libraries for AWS, Azure, GCP, and Cisco infrastructure icons. Supports network topology, enterprise architecture, BPMN, org charts, and multi-page diagrams. Writes a `.drawio` source file and renders to SVG/PNG with automatic light/dark mode variants via `diagramkit render`.

Can be invoked directly or via `/adk:diagram --engine drawio`. Accepted file extensions: `.drawio`, `.drawio.xml`, `.dio`.

## When to Use

- Create network topology diagrams with infrastructure icons (routers, switches, firewalls)
- Build AWS, Azure, or GCP architecture diagrams with native cloud service shapes
- Generate BPMN business process diagrams
- Create org charts or multi-page diagram sets
- Produce diagrams requiring precise pixel-level positioning
- Build container/swimlane-based diagrams with nested elements
- Create diagrams editable in the draw.io web app or VS Code extension

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text | — | What to diagram. Natural language description |
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg` \| `png` | `svg` | Output image format |
| `--theme` | `both` \| `light` \| `dark` | `both` | Theme variants to render |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| AWS infrastructure described | Uses `mxgraph.aws4.*` shape library (EC2, Lambda, S3, RDS, VPC, SQS, etc.) |
| Azure infrastructure described | Uses `mxgraph.azure.*` shape library (Virtual Machine, App Service, SQL Database, etc.) |
| GCP infrastructure described | Uses `mxgraph.gcp2.*` shape library (Compute Engine, Cloud Run, Cloud SQL, etc.) |
| Network topology described | Uses `mxgraph.cisco.*` shapes (routers, switches, firewalls, servers) |
| Multi-page requested | Generates multiple `<diagram>` elements within the `<mxfile>` wrapper |
| Invoked by `/adk:diagram` | Receives forwarded parameters, runs in `--auto` mode |

## Priorities

The skill focuses on producing correct, professionally-styled draw.io XML:

1. **XML validity** — well-formed `.drawio` XML with required root cells (`id="0"` and `id="1"`)
2. **Layout precision** — consistent grid alignment (120x60 standard, 120x80 cylinders, 40px spacing)
3. **Shape library accuracy** — correct `mxgraph.*` style strings for cloud and infrastructure icons
4. **Edge routing** — orthogonal edge style for clean diagrams, labeled edges for protocols/data types
5. **Container nesting** — relative coordinates for elements inside swimlanes/containers
6. **Dark mode readability** — mid-tone fills, `fontColor=#333333`, no pure white/black fills

## Key Behaviors

- **Rich icon libraries**: native shapes for AWS (EC2, Lambda, S3, RDS, etc.), Azure (VM, App Service, Functions, etc.), GCP (Compute Engine, Cloud Run, etc.), and Cisco networking equipment
- **Container/swimlane grouping**: elements inside containers use relative x/y coordinates; supports nested groups like VPC → Subnet → Instance
- **Multi-page diagrams**: overview + detail pages within a single `.drawio` file
- **Orthogonal edge routing**: `edgeStyle=orthogonalEdgeStyle` for clean 90-degree connections
- **ER-style endpoints**: ERmandOne, ERmany, ERoneToMany, ERzeroToMany, ERzeroToOne arrowheads
- **Semantic IDs**: `api-server` not `node-1` for readable XML source
- **Consistent color system**: blue (default), green (data/success), orange (warning), red (error), purple (services), yellow (highlight), gray (infrastructure)

## Workflow

Follows the 6-phase workflow with complexity-adaptive phase skipping.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm diagram type, components, layout pattern, output location |
| 1. Research & Options | yes | Identify components, relationships, data flows, logical groupings |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate `.drawio` XML file with shapes, edges, containers, and styling |
| 5. Validate & Learn | yes | Render to SVG/PNG (light+dark), verify renderability, naming, consistency |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before rendering | Run preflight.py, validate diagramkit and npm packages |
| `output-format` | producing output | short/standard/detailed verbosity; keep source + rendered files |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work | Launch 2+ child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `workspace-conventions` | always | Diagrams in `diagrams/`, both light+dark SVG and PNG, respect `diagramkit.config.json` |

## Output Format

All output includes:

- `.drawio` XML source file (editable in draw.io web app or VS Code extension)
- Rendered images (when `--render` is used):
  - `<name>-light.svg` and `<name>-dark.svg`
  - `<name>-light.png` and `<name>-dark.png`
- Completion report with file paths and instructions to open in draw.io

Rendering uses `diagramkit render` (primary, Playwright Chromium-based) or the draw.io Desktop CLI (fallback). Dark mode uses diagramkit's contrast optimization for element colors and dark surface background.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:diagram` | Let the router auto-detect the best engine |
| `/adk:diagram-mermaid` | Text-based diagrams (flowcharts, sequence, ER, Gantt, C4) |
| `/adk:diagram-excalidraw` | Hand-drawn architecture overviews and freeform layouts |
| `/adk:diagram-graphviz` | Strict algorithmic layout for dependency graphs |
| `/adk:docs-write` | Documentation that may embed diagrams |

## Examples

```
/adk:diagram-drawio "3-tier web application architecture"
/adk:diagram-drawio "AWS VPC with public and private subnets"
/adk:diagram-drawio "Azure microservices deployment"
/adk:diagram-drawio "GCP data pipeline with Pub/Sub and BigQuery"
/adk:diagram-drawio "corporate network topology with DMZ"
/adk:diagram-drawio "BPMN order fulfillment process"
/adk:diagram-drawio --render --format png "multi-page system architecture"
/adk:diagram-drawio --theme dark "Kubernetes cluster layout"
/adk:diagram-drawio --help
```
