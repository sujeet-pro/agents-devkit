---
title: 'diagram-drawio'
description: 'Create draw.io diagrams — precise layout with rich icon library for network topology, enterprise architecture, and BPMN'
skill_name: diagram-drawio
category: task
workflow_tier: full
user_invocable: true
---

# diagram-drawio

Use `diagram-drawio` to create draw.io diagrams — precise layout with rich icon library for network topology, enterprise architecture, and BPMN. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`diagram-drawio` belongs to the `task` layer and is declared at the `full` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--render` | flag | off | Render to image after generating source |
| `--format` | `svg`, `png` | `svg` | Output image format |
| `--theme` | `both`, `light`, `dark` | `both` | Theme variants to render |
| `--help` | flag | off | Show help |

### Parameter Notes

- `--render` changes the deliverable from source-only generation to source plus rendered assets.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before rendering | Run preflight.py for diagramkit and MCP validation. Ensure npm packages are installed. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Keep both editable source file and rendered SVG. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:workspace-conventions` | always | All work inside the project repo. Temp files in `.temp/<task-slug>/` (gitignored). Diagrams in `diagrams/` (sibling to doc, or project root). Both light+dark SVG and PNG. Respect `diagramkit.config.json` when present. Always commit source files with rendered output. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

### Workflow

### 1. Confirm

Confirm: diagram type, components to show, layout pattern, output location. Invoke `/adk:workspace-conventions` to determine output location.

### 2. Execute

Parse the description to identify:

- Components, services, and infrastructure to show
- Relationships and data flows
- Logical groupings (layers, zones, regions)
- The best layout approach (hierarchical, left-to-right, grid)

Write a `.drawio` file to the determined output location following the XML format reference below. Ensure `.temp/` is gitignored if using temp files.

### 3. Verify

Run the rendering pipeline (Step 1–4 above). Then report:

```
Draw.io diagram complete:
  Source: ./diagrams/network-topology.drawio
  Output:
    ./diagrams/network-topology-light.svg
    ./diagrams/network-topology-dark.svg
    ./diagrams/network-topology-light.png
    ./diagrams/network-topology-dark.png

Edit in browser: https://app.diagrams.net (load the .drawio file)
VS Code: Install the draw.io extension and open the file directly.
```

---

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:diagram` — parent routing skill that auto-detects engine
- `/adk:diagram-mermaid` — text-based diagrams (flowcharts, sequence, ER, etc.)
- `/adk:diagram-excalidraw` — hand-drawn architecture diagrams
- `/adk:diagram-graphviz` — strict DOT layout for dependency graphs
- `/adk:docs-write` — documentation that may embed diagrams

## Additional Reference

### Human in the Loop

- **Plan first (Phase 0)**: Always confirm intent — diagram type, components, layout pattern — before generating.
- **Auto mode**: When invoked with `--auto` or by a parent skill, skip confirmations and proceed directly.

### Rendering Pipeline

Rendering always produces both **light and dark** variants in **SVG and PNG** by default.

### Step 1: Determine Output Location

1. If a `diagramkit.config.json` exists at the project root → use its `outputDir` setting
2. If invoked by a doc skill → place in `diagrams/` folder sibling to the document
3. Otherwise → place in `./diagrams/` at the project root

### Step 2: Render with diagramkit (Primary)

```bash
# SVG — both light and dark
diagramkit render diagram.drawio --format svg --theme both

# PNG — both themes, 2x scale for retina
diagramkit render diagram.drawio --format png --theme both --scale 2
```

diagramkit uses Playwright Chromium for draw.io rendering. It creates dark variants automatically by:

1. Loading the `.drawio` XML in a headless browser with the draw.io renderer
2. Applying contrast optimization to element colors
3. Adjusting background to dark surface

Standard fill colors from the Color Combinations table below are designed to work with this contrast optimization.

If the project has a `diagramkit.config.json`, diagramkit reads it automatically for output directory, default format, theme, and scale.

**Guidelines for dark mode compatibility:**

- Avoid very light fills (close to white) — they lose distinction when darkened
- Avoid very dark fills (close to black) — they become invisible on dark backgrounds
- Use mid-tone stroke colors — dark strokes adapt better than very light ones
- Use `fontColor=#333333` — diagramkit adjusts this for dark mode

### Step 3: Fallback — draw.io Desktop CLI

If diagramkit is not installed or fails, use the draw.io desktop app's CLI export.

**Install:** Download from https://github.com/jgraph/drawio-desktop/releases

```bash
# macOS path (adjust for Linux/Windows)
DRAWIO="/Applications/draw.io.app/Contents/MacOS/draw.io"

# Light variants
$DRAWIO --export --format svg --output diagrams/diagram-light.svg diagram.drawio
$DRAWIO --export --format png --output diagrams/diagram-light.png --scale 2 diagram.drawio

# Dark variants — draw.io CLI does not natively support dark mode export.
# Workaround: modify the XML to set dark background and adjust colors, then export.
# For best dark mode results, use diagramkit.
$DRAWIO --export --format svg --output diagrams/diagram-dark.svg diagram.drawio
$DRAWIO --export --format png --output diagrams/diagram-dark.png --scale 2 diagram.drawio
```

On Linux, the binary is typically `drawio` or `/usr/bin/draw.io`. On Windows, use `"C:\Program Files\draw.io\draw.io.exe"`.

### Step 4: Verify Outputs

Confirm these files exist:
- `<name>-light.svg` and `<name>-dark.svg`
- `<name>-light.png` and `<name>-dark.png`

---

### XML Format Reference

### File Structure

```xml
<mxfile host="diagramkit" modified="2024-01-01T00:00:00.000Z" type="device">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1200" pageHeight="900"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Diagram elements go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Key structural rules:

- `id="0"` is the root cell (always required)
- `id="1"` is the default layer (always required, parent="0")
- All diagram elements have `parent="1"` (or a custom layer/container ID)
- Vertices have `vertex="1"`, edges have `edge="1"`

### Basic Vertex (Shape)

```xml
<mxCell id="node-1" value="Service A" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Basic Edge (Connection)

```xml
<mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
        edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Edge with Label

```xml
<mxCell id="edge-2" value="REST API" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
        edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

---

### Shape Libraries

### Basic Shapes

| Shape | Style String |
|-------|-------------|
| Rectangle | `rounded=0;whiteSpace=wrap;` |
| Rounded Rectangle | `rounded=1;whiteSpace=wrap;` |
| Ellipse | `ellipse;whiteSpace=wrap;` |
| Circle | `ellipse;whiteSpace=wrap;aspect=fixed;` |
| Diamond | `rhombus;whiteSpace=wrap;` |
| Cylinder (DB) | `shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;size=25;fixedSize=1;` |
| Parallelogram | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;fixedSize=1;size=20;` |
| Cloud | `ellipse;shape=cloud;whiteSpace=wrap;` |
| Document | `shape=document;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=0.27;` |
| Trapezoid | `shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;fixedSize=1;size=20;` |

### Infrastructure Shapes

| Shape | Style String |
|-------|-------------|
| Server | `shape=mxgraph.cisco.servers.standard_server;` |
| Database | `shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;` |
| Firewall | `shape=mxgraph.cisco.firewalls.firewall;` |
| Router | `shape=mxgraph.cisco.routers.router;` |
| Switch | `shape=mxgraph.cisco.switches.workgroup_switch;` |
| Load Balancer | `shape=mxgraph.aws4.application_load_balancer;` |
| Container | `rounded=1;whiteSpace=wrap;arcSize=10;dashed=1;dashPattern=5 5;` |
| Swimlane | `swimlane;startSize=30;` |

### AWS Shapes

| Service | Style String |
|---------|-------------|
| EC2 | `shape=mxgraph.aws4.ec2;` |
| Lambda | `shape=mxgraph.aws4.lambda_function;` |
| S3 | `shape=mxgraph.aws4.s3;` |
| RDS | `shape=mxgraph.aws4.rds;` |
| DynamoDB | `shape=mxgraph.aws4.dynamodb;` |
| API Gateway | `shape=mxgraph.aws4.api_gateway;` |
| CloudFront | `shape=mxgraph.aws4.cloudfront;` |
| VPC | `shape=mxgraph.aws4.virtual_private_cloud;` |
| SQS | `shape=mxgraph.aws4.sqs;` |
| SNS | `shape=mxgraph.aws4.sns;` |
| ECS | `shape=mxgraph.aws4.ecs;` |
| EKS | `shape=mxgraph.aws4.eks;` |

### Azure Shapes

| Service | Style String |
|---------|-------------|
| Virtual Machine | `shape=mxgraph.azure.virtual_machine;` |
| App Service | `shape=mxgraph.azure.app_service;` |
| SQL Database | `shape=mxgraph.azure.sql_database;` |
| Storage | `shape=mxgraph.azure.storage;` |
| Functions | `shape=mxgraph.azure.function_apps;` |
| Key Vault | `shape=mxgraph.azure.key_vaults;` |
| Load Balancer | `shape=mxgraph.azure.azure_load_balancer;` |

### GCP Shapes

| Service | Style String |
|---------|-------------|
| Compute Engine | `shape=mxgraph.gcp2.compute_engine;` |
| Cloud Run | `shape=mxgraph.gcp2.cloud_run;` |
| Cloud SQL | `shape=mxgraph.gcp2.cloud_sql;` |
| Cloud Storage | `shape=mxgraph.gcp2.cloud_storage;` |
| Cloud Functions | `shape=mxgraph.gcp2.cloud_functions;` |
| Pub/Sub | `shape=mxgraph.gcp2.cloud_pubsub;` |
| GKE | `shape=mxgraph.gcp2.google_kubernetes_engine;` |

---

### Color Combinations

| Purpose | Fill | Stroke |
|---------|------|--------|
| Blue (default) | `#dae8fc` | `#6c8ebf` |
| Green (success/data) | `#d5e8d4` | `#82b366` |
| Orange (warning) | `#ffe6cc` | `#d6b656` |
| Red (error/external) | `#f8cecc` | `#b85450` |
| Purple (services) | `#e1d5e7` | `#9673a6` |
| Yellow (highlight) | `#fff2cc` | `#d6b656` |
| Gray (infrastructure) | `#f5f5f5` | `#666666` |
| Dark blue (headers) | `#1ba1e2` | `#006EAF` |

### Text Style Properties

```
fontSize=12;fontStyle=1;fontColor=#333333;align=center;verticalAlign=middle;
```

Font styles: `0` = normal, `1` = bold, `2` = italic, `3` = bold+italic, `4` = underline.

---

### Edge Styles and Routing

### Edge Style Options

| Style | Description |
|-------|-------------|
| `edgeStyle=orthogonalEdgeStyle;` | 90-degree elbow routing (most common) |
| `edgeStyle=elbowEdgeStyle;` | Single elbow point |
| `edgeStyle=entityRelationEdgeStyle;` | ER diagram style |
| `edgeStyle=isometricEdgeStyle;` | Isometric perspective |
| `curved=1;` | Curved line (with no edgeStyle) |
| (no edgeStyle) | Straight line |

### Arrow End Styles

```
endArrow=classic;startArrow=none;
```

| Value | Description |
|-------|-------------|
| `classic` | Standard arrow |
| `block` | Filled block arrow |
| `open` | Open arrow |
| `diamond` | Diamond (composition) |
| `diamondThin` | Thin diamond (aggregation) |
| `oval` | Circle endpoint |
| `none` | No arrowhead |
| `ERmandOne` | ER: exactly one |
| `ERmany` | ER: many |
| `ERoneToMany` | ER: one-to-many |
| `ERzeroToMany` | ER: zero-to-many |
| `ERzeroToOne` | ER: zero-to-one |

### Stroke Styles

```
strokeWidth=2;dashed=1;dashPattern=5 5;strokeColor=#666666;
```

| Property | Values |
|----------|--------|
| `strokeWidth` | 1, 2, 3, etc. |
| `dashed` | 0 (solid), 1 (dashed) |
| `dashPattern` | `5 5` (default dashed), `10 5` (long dash), `2 2` (dotted) |

---

### Layout Patterns

### Hierarchical (Top-Down)

Best for: Architecture diagrams, org charts, call hierarchies.

```xml
<!-- Row 1: Entry points -->
<mxCell id="lb" value="Load Balancer" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="340" y="40" width="120" height="60" as="geometry"/>
</mxCell>

<!-- Row 2: Services -->
<mxCell id="api" value="API Server" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="200" y="160" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="web" value="Web Server" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="480" y="160" width="120" height="60" as="geometry"/>
</mxCell>

<!-- Row 3: Data stores -->
<mxCell id="db" value="Database" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;"
        vertex="1" parent="1">
  <mxGeometry x="340" y="280" width="120" height="80" as="geometry"/>
</mxCell>
```

Grid guidelines:

- Column width: 160-200px
- Row height: 120-160px
- Element size: 120x60 (standard), 120x80 (cylinder)
- Spacing: 40px between elements

### Left-to-Right (Pipeline)

Best for: Data pipelines, CI/CD, request flows.

```xml
<mxCell id="input" value="Input" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="40" y="160" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="process" value="Process" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="240" y="160" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="output" value="Output" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="440" y="160" width="120" height="60" as="geometry"/>
</mxCell>
```

### Containers / Groups

Use swimlanes or dashed containers for grouping:

```xml
<!-- Container -->
<mxCell id="vpc" value="VPC 10.0.0.0/16" style="swimlane;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;"
        vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="400" height="300" as="geometry"/>
</mxCell>

<!-- Elements inside container (parent = container ID) -->
<mxCell id="subnet-public" value="Public Subnet" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="vpc">
  <mxGeometry x="20" y="50" width="160" height="60" as="geometry"/>
</mxCell>
```

Note: When elements are inside a container, their x/y coordinates are relative to the container.

### Multi-Page Diagrams

```xml
<mxfile>
  <diagram id="overview" name="Overview">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Overview diagram -->
      </root>
    </mxGraphModel>
  </diagram>
  <diagram id="detail-api" name="API Detail">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- API detail diagram -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

### Complete Example: 3-Tier Architecture

```xml
<mxfile host="diagramkit">
  <diagram id="arch" name="Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1200" pageHeight="900">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Title -->
        <mxCell id="title" value="System Architecture" style="text;fontSize=20;fontStyle=1;align=center;"
                vertex="1" parent="1">
          <mxGeometry x="300" y="10" width="200" height="30" as="geometry"/>
        </mxCell>

        <!-- Load Balancer -->
        <mxCell id="lb" value="Load Balancer" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="340" y="60" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- API Servers -->
        <mxCell id="api-1" value="API Server 1" style="rounded=1;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;"
                vertex="1" parent="1">
          <mxGeometry x="200" y="180" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="api-2" value="API Server 2" style="rounded=1;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;"
                vertex="1" parent="1">
          <mxGeometry x="480" y="180" width="120" height="60" as="geometry"/>
        </mxCell>

        <!-- Database -->
        <mxCell id="db" value="PostgreSQL" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;"
                vertex="1" parent="1">
          <mxGeometry x="260" y="320" width="100" height="80" as="geometry"/>
        </mxCell>

        <!-- Cache -->
        <mxCell id="cache" value="Redis Cache" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffe6cc;strokeColor=#d6b656;"
                vertex="1" parent="1">
          <mxGeometry x="440" y="320" width="100" height="80" as="geometry"/>
        </mxCell>

        <!-- Edges -->
        <mxCell id="e-lb-api1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="lb" target="api-1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e-lb-api2" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="lb" target="api-2" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e-api1-db" value="SQL" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="api-1" target="db" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e-api2-db" value="SQL" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="api-2" target="db" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e-api1-cache" style="edgeStyle=orthogonalEdgeStyle;rounded=1;dashed=1;" edge="1" source="api-1" target="cache" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e-api2-cache" style="edgeStyle=orthogonalEdgeStyle;rounded=1;dashed=1;" edge="1" source="api-2" target="cache" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Complete Example: Network Topology

```xml
<mxfile host="diagramkit">
  <diagram id="network" name="Network">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Internet -->
        <mxCell id="internet" value="Internet" style="ellipse;shape=cloud;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#666666;"
                vertex="1" parent="1">
          <mxGeometry x="340" y="20" width="120" height="80" as="geometry"/>
        </mxCell>

        <!-- Firewall -->
        <mxCell id="fw" value="Firewall" style="rounded=1;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="350" y="140" width="100" height="50" as="geometry"/>
        </mxCell>

        <!-- DMZ Container -->
        <mxCell id="dmz" value="DMZ" style="swimlane;startSize=25;fillColor=#fff2cc;strokeColor=#d6b656;dashed=1;"
                vertex="1" parent="1">
          <mxGeometry x="160" y="230" width="480" height="120" as="geometry"/>
        </mxCell>

        <mxCell id="web-1" value="Web Server" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
                vertex="1" parent="dmz">
          <mxGeometry x="30" y="40" width="120" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="web-2" value="API Gateway" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
                vertex="1" parent="dmz">
          <mxGeometry x="330" y="40" width="120" height="50" as="geometry"/>
        </mxCell>

        <!-- Internal Network Container -->
        <mxCell id="internal" value="Internal Network" style="swimlane;startSize=25;fillColor=#d5e8d4;strokeColor=#82b366;dashed=1;"
                vertex="1" parent="1">
          <mxGeometry x="160" y="400" width="480" height="120" as="geometry"/>
        </mxCell>

        <mxCell id="app" value="App Server" style="rounded=1;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;"
                vertex="1" parent="internal">
          <mxGeometry x="30" y="40" width="120" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="db" value="Database" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;"
                vertex="1" parent="internal">
          <mxGeometry x="330" y="30" width="120" height="70" as="geometry"/>
        </mxCell>

        <!-- Connections -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="internet" target="fw" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="fw" target="web-1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="fw" target="web-2" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="web-1" target="app" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="app" target="db" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

### Quality Standards

1. **Use semantic IDs** — `api-server` not `node-1`.
2. **Use descriptive labels** — `PostgreSQL Primary` not `DB`.
3. **Group related elements** with swimlanes or dashed containers.
4. **Use consistent styling** — same color for same type of component.
5. **Use orthogonal edge routing** (`edgeStyle=orthogonalEdgeStyle`) for clean diagrams.
6. **Label important edges** — especially for protocols, ports, or data types.
7. **Keep it focused** — max 20-25 elements per page; split into multiple pages for complex systems.

---

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:diagram-drawio
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:diagram-drawio --render --format png <prompt-text>
```
