# Draw.io Reference

Use Draw.io when exact layout, infrastructure icon libraries, BPMN-like structure, or multi-page diagrams matter more than plain-text diffability.

Accepted source extensions:

- `.drawio`
- `.drawio.xml`
- `.dio`

Use `diagramkit-integration.md` for rendering commands. This guide focuses on building the source XML.

## Best Fit

Choose Draw.io when:

- the diagram is infrastructure-heavy
- cloud or network icons carry meaning
- precise positioning matters
- the diagram needs containers, swimlanes, or multiple pages

Prefer Mermaid for text-first diagrams and Excalidraw for sketch-style overviews.

## Build Rules

1. Keep the required root cells: `id="0"` and `id="1"`.
2. Give nodes semantic IDs such as `api-gateway` or `private-subnet`.
3. Use `vertex="1"` for shapes and `edge="1"` for connectors.
4. Keep shared style fragments consistent across similar components.
5. Prefer orthogonal edges for architecture and network diagrams.
6. Use containers or swimlanes for zones, VPCs, layers, or teams.
7. Split very large diagrams into multiple pages instead of one crowded canvas.

## Minimal File Structure

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
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Basic Elements

### Vertex

```xml
<mxCell id="node-1" value="Service A" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

### Edge

```xml
<mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
        edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Labeled Edge

```xml
<mxCell id="edge-2" value="REST API" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
        edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Common Shape Libraries

### Basic Shapes

| Shape | Style string |
| --- | --- |
| Rectangle | `rounded=0;whiteSpace=wrap;` |
| Rounded rectangle | `rounded=1;whiteSpace=wrap;` |
| Ellipse | `ellipse;whiteSpace=wrap;` |
| Circle | `ellipse;whiteSpace=wrap;aspect=fixed;` |
| Diamond | `rhombus;whiteSpace=wrap;` |
| Cylinder | `shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;` |
| Hexagon | `shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;size=25;fixedSize=1;` |
| Parallelogram | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;fixedSize=1;size=20;` |
| Cloud | `ellipse;shape=cloud;whiteSpace=wrap;` |
| Document | `shape=document;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=0.27;` |
| Swimlane | `swimlane;startSize=30;` |

### Infrastructure Shapes

| Shape | Style string |
| --- | --- |
| Server | `shape=mxgraph.cisco.servers.standard_server;` |
| Database | `shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;` |
| Firewall | `shape=mxgraph.cisco.firewalls.firewall;` |
| Router | `shape=mxgraph.cisco.routers.router;` |
| Switch | `shape=mxgraph.cisco.switches.workgroup_switch;` |
| Load balancer | `shape=mxgraph.aws4.application_load_balancer;` |
| Container | `rounded=1;whiteSpace=wrap;arcSize=10;dashed=1;dashPattern=5 5;` |

### Cloud Shapes

| Platform | Example styles |
| --- | --- |
| AWS | `shape=mxgraph.aws4.ec2;`, `shape=mxgraph.aws4.lambda_function;`, `shape=mxgraph.aws4.s3;`, `shape=mxgraph.aws4.virtual_private_cloud;` |
| Azure | `shape=mxgraph.azure.virtual_machine;`, `shape=mxgraph.azure.app_service;`, `shape=mxgraph.azure.sql_database;` |
| GCP | `shape=mxgraph.gcp2.compute_engine;`, `shape=mxgraph.gcp2.cloud_run;`, `shape=mxgraph.gcp2.cloud_sql;` |

## Color Combinations

Use mid-tone colors that survive both light and dark renders:

| Purpose | Fill | Stroke |
| --- | --- | --- |
| Blue | `#dae8fc` | `#6c8ebf` |
| Green | `#d5e8d4` | `#82b366` |
| Orange | `#ffe6cc` | `#d6b656` |
| Red | `#f8cecc` | `#b85450` |
| Purple | `#e1d5e7` | `#9673a6` |
| Yellow | `#fff2cc` | `#d6b656` |
| Gray | `#f5f5f5` | `#666666` |

Common text style fragment:

```text
fontSize=12;fontStyle=1;fontColor=#333333;align=center;verticalAlign=middle;
```

Guidelines:

- avoid very light fills close to white
- avoid very dark fills close to black
- prefer `fontColor=#333333`
- keep stroke colors slightly darker than fills

## Edge Styles And Routing

### Common edge styles

| Style | Use |
| --- | --- |
| `edgeStyle=orthogonalEdgeStyle;` | Clean 90-degree routing for most architecture diagrams |
| `edgeStyle=elbowEdgeStyle;` | Single bend |
| `edgeStyle=entityRelationEdgeStyle;` | ER-style routing |
| `curved=1;` | Curved line |
| no `edgeStyle` | Straight line |

### Arrowheads

```text
endArrow=classic;startArrow=none;
```

Useful endpoint styles:

- `classic`
- `block`
- `open`
- `diamond`
- `diamondThin`
- `oval`
- `none`
- `ERmandOne`
- `ERmany`
- `ERoneToMany`

### Stroke fragments

```text
strokeWidth=2;dashed=1;dashPattern=5 5;strokeColor=#666666;
```

## Layout Patterns

### Hierarchical Top-Down

Best for architecture diagrams, org charts, and service layering.

```xml
<mxCell id="lb" value="Load Balancer" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="340" y="40" width="120" height="60" as="geometry"/>
</mxCell>

<mxCell id="api" value="API Server" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="1">
  <mxGeometry x="200" y="160" width="120" height="60" as="geometry"/>
</mxCell>
```

Grid guidance:

- column width: about 160 to 200px
- row height: about 120 to 160px
- standard node size: about 120x60
- leave about 40px between nearby elements

### Left-To-Right

Best for pipelines, request flows, or data movement.

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

### Containers And Swimlanes

Use containers for VPCs, zones, layers, or departments:

```xml
<mxCell id="vpc" value="VPC 10.0.0.0/16" style="swimlane;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;"
        vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="400" height="300" as="geometry"/>
</mxCell>

<mxCell id="subnet-public" value="Public Subnet" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
        vertex="1" parent="vpc">
  <mxGeometry x="20" y="50" width="160" height="60" as="geometry"/>
</mxCell>
```

When a shape is inside a container, its coordinates are relative to the container.

### Multi-Page Files

Use multiple `<diagram>` blocks when one file needs overview and detail pages:

```xml
<mxfile>
  <diagram id="overview" name="Overview">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
  <diagram id="detail-api" name="API Detail">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Example: Three-Tier Architecture

```xml
<mxfile host="diagramkit">
  <diagram id="arch" name="Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="lb" value="Load Balancer" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;"
                vertex="1" parent="1">
          <mxGeometry x="340" y="60" width="120" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="api-1" value="API Server 1" style="rounded=1;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;"
                vertex="1" parent="1">
          <mxGeometry x="200" y="180" width="120" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="db" value="PostgreSQL" style="shape=cylinder3;whiteSpace=wrap;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#d5e8d4;strokeColor=#82b366;"
                vertex="1" parent="1">
          <mxGeometry x="260" y="320" width="100" height="80" as="geometry"/>
        </mxCell>

        <mxCell id="e-lb-api1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;" edge="1" source="lb" target="api-1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Quality Rules

- Use semantic IDs, not generic `node-1` style names.
- Use descriptive labels and label important edges.
- Group related elements with swimlanes or containers.
- Prefer orthogonal edges for technical architecture diagrams.
- Keep one page focused; split into multiple pages when the layout becomes crowded.
