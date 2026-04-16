# Excalidraw Reference

Use Excalidraw for hand-drawn-feel architecture overviews, system-context sketches, and freeform explanation diagrams.

Accepted source extensions:

- `.excalidraw`

Use `diagramkit-integration.md` for rendering commands. This guide focuses on building valid Excalidraw source JSON.

## Best Fit

Choose Excalidraw when:

- layout and presentation matter more than strict diagram syntax
- the audience benefits from an approachable whiteboard-style visual
- the diagram is an overview, system context, or concept map
- the structure is not naturally a Mermaid flowchart or Graphviz graph

Prefer Mermaid for text-first technical diagrams and Draw.io for icon-heavy infrastructure layouts.

## Build Rules

1. Plan the layout before writing JSON.
2. Use rectangles, ellipses, text, arrows, and grouping boxes as the default vocabulary.
3. Give every visual element a stable semantic ID.
4. Treat labels as separate text elements, not inline properties.
5. Keep arrows orthogonal and explicit when readability matters.
6. Use grouping rectangles for layers, zones, and bounded contexts.
7. Validate JSON structure before claiming the diagram is ready.

## Minimal File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "diagramkit",
  "elements": [],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

## Layout Planning

Plan positions before generating elements.

### Vertical Flow

Best for layered architectures and hierarchies.

```text
Row 0: title
Row 1: users or entry points
Row 2: frontend or gateway
Row 3: orchestration
Row 4: services
Row 5: data layer
Row 6: external systems
```

Good defaults:

- columns at roughly `100`, `300`, `500`, `700`, `900`
- element width around `160` to `200`
- element height around `80` to `90`
- spacing around `40` to `50`

### Horizontal Flow

Best for pipelines and left-to-right process explanations.

```text
Stage x positions: 100, 350, 600, 850, 1100
Common y position: 200
```

### Hub And Spoke

Best for orchestrators, event buses, or central control planes.

```text
Center hub: x=500, y=350
Spokes around the hub at roughly 45-degree increments
```

## Critical Rules

### 1. Do Not Use Diamond Shapes

Raw Excalidraw JSON often renders arrow attachments poorly on diamonds. Use styled rectangles instead.

Suggested rectangle semantics:

| Meaning | Background | Stroke |
| --- | --- | --- |
| Orchestrator or hub | `#ffa8a8` | `#c92a2a` |
| Decision point | `#ffd8a8` | `#e8590c` |
| Central router | larger rectangle with strong stroke | matching semantic color |

### 2. Labels Need Two Elements

Do not rely on a `label` property. Every labeled shape needs:

1. a shape element with a `boundElements` reference to the text
2. a text element with `containerId` pointing back to the shape

Shape:

```json
{
  "id": "api-box",
  "type": "rectangle",
  "boundElements": [{ "type": "text", "id": "api-box-text" }]
}
```

Text:

```json
{
  "id": "api-box-text",
  "type": "text",
  "containerId": "api-box",
  "text": "API Server",
  "originalText": "API Server"
}
```

### 3. Position Text Explicitly

For text inside a shape:

- `text.x = shape.x + 5`
- `text.y = shape.y + (shape.height - text.height) / 2`
- `text.width = shape.width - 10`
- use `textAlign: "center"`
- use `verticalAlign: "middle"`
- use `\n` for multi-line labels

### 4. Elbow Arrows Need Three Properties

For right-angle arrows:

```json
{
  "type": "arrow",
  "roughness": 0,
  "roundness": null,
  "elbowed": true
}
```

Without all three, the arrow may render curved.

### 5. Arrow Anchors Must Start And End At Shape Edges

Use edge points, not centers:

| Edge | Formula |
| --- | --- |
| Top | `(x + width/2, y)` |
| Bottom | `(x + width/2, y + height)` |
| Left | `(x, y + height/2)` |
| Right | `(x + width, y + height/2)` |

### 6. Arrow Width And Height Follow The Bounding Box

If your points are:

```text
[[0, 0], [-440, 0], [-440, 70]]
```

Then:

- `width = 440`
- `height = 70`

## Common Element Types

| Type | Use |
| --- | --- |
| `rectangle` | Services, databases, containers, orchestrators, decision substitutes |
| `ellipse` | Users, external systems, start or end markers |
| `text` | Labels, titles, annotations |
| `arrow` | Data flow, dependencies, relationships |
| `line` | Section dividers or freeform boundaries |

## Required Properties

Every element should include the standard Excalidraw fields:

```json
{
  "id": "unique-id-string",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1971c2",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "seed": 1,
  "version": 1,
  "versionNonce": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

Useful text fields:

```json
{
  "text": "Label Text",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "baseline": 14,
  "containerId": "parent-shape-id",
  "originalText": "Label Text",
  "lineHeight": 1.25
}
```

Useful arrow fields:

```json
{
  "points": [
    [0, 0],
    [0, 110]
  ],
  "lastCommittedPoint": null,
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "elbowed": true
}
```

## Arrow Routing Patterns

| Pattern | Points | Use |
| --- | --- | --- |
| Down | `[[0,0], [0,h]]` | Straight vertical connection |
| Right | `[[0,0], [w,0]]` | Straight horizontal connection |
| L-left-down | `[[0,0], [-w,0], [-w,h]]` | Go left, then down |
| L-right-down | `[[0,0], [w,0], [w,h]]` | Go right, then down |
| L-down-left | `[[0,0], [0,h], [-w,h]]` | Go down, then left |
| L-down-right | `[[0,0], [0,h], [w,h]]` | Go down, then right |
| S-shape | `[[0,0], [0,h1], [w,h1], [w,h2]]` | Route around obstacles |
| U-turn | `[[0,0], [w,0], [w,-h], [0,-h]]` | Callback or return path |

### Bindings

Bindings improve visual attachment:

```json
{
  "startBinding": {
    "elementId": "source-shape-id",
    "focus": 0,
    "gap": 1,
    "fixedPoint": [0.5, 1]
  },
  "endBinding": {
    "elementId": "target-shape-id",
    "focus": 0,
    "gap": 1,
    "fixedPoint": [0.5, 0]
  }
}
```

Useful `fixedPoint` values:

- top: `[0.5, 0]`
- bottom: `[0.5, 1]`
- left: `[0, 0.5]`
- right: `[1, 0.5]`

### Bidirectional Arrows

```json
{
  "startArrowhead": "arrow",
  "endArrowhead": "arrow"
}
```

Supported arrowheads commonly used here:

- `null`
- `"arrow"`
- `"bar"`
- `"dot"`
- `"triangle"`

## Grouping

Use dashed rectangles for logical grouping such as namespaces, VPCs, or layers:

```json
{
  "id": "group-data-layer",
  "type": "rectangle",
  "strokeColor": "#2f9e44",
  "backgroundColor": "transparent",
  "strokeStyle": "dashed",
  "roughness": 0,
  "roundness": null,
  "boundElements": null
}
```

Group labels should usually be standalone text elements near the top-left of the grouping box.

## Color Palettes

### Default Palette

| Component | Background | Stroke |
| --- | --- | --- |
| Frontend or UI | `#a5d8ff` | `#1971c2` |
| Backend or API | `#d0bfff` | `#7048e8` |
| Database | `#b2f2bb` | `#2f9e44` |
| Storage | `#ffec99` | `#f08c00` |
| AI or ML | `#e599f7` | `#9c36b5` |
| External API | `#ffc9c9` | `#e03131` |
| Orchestration | `#ffa8a8` | `#c92a2a` |
| Validation | `#ffd8a8` | `#e8590c` |
| Network or security | `#dee2e6` | `#495057` |

### Cloud-Oriented Alternatives

| Palette | Typical use |
| --- | --- |
| `aws` | AWS system diagrams |
| `azure` | Azure architecture diagrams |
| `gcp` | GCP architecture diagrams |
| `k8s` | Kubernetes-focused deployments |

Keep one palette consistent within a single diagram unless a mixed-platform comparison is the point.

## Validation Checklist

- every labeled shape has both a shape and a text element
- every shape-text relationship is connected through `boundElements` and `containerId`
- every arrow uses points that start and end on shape edges
- elbow arrows set `elbowed: true`, `roundness: null`, and `roughness: 0`
- arrow `width` and `height` match the point bounding box
- no duplicate IDs exist
- the file is valid JSON

## Common Issues

| Issue | Fix |
| --- | --- |
| Labels do not appear | Use separate text elements instead of `label` |
| Arrows look curved | Set `elbowed: true`, `roundness: null`, `roughness: 0` |
| Arrows float away from shapes | Anchor from edge coordinates, not centers |
| Arrow endpoints are wrong | Recompute final point offsets from target edge position |
| Diagram feels cluttered | Split the diagram into overview and detail files |

## Quality Rules

- Keep diagrams focused and presentation-friendly.
- Use grouping boxes for layers or bounded contexts.
- Keep labels readable at normal doc scale.
- Favor stable, symmetric layout patterns over arbitrary placement.
- Split very large diagrams into overview and detail artifacts instead of forcing one canvas.
