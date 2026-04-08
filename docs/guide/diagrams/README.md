---
title: Diagrams
description: Create architecture, flow, sequence, and dependency diagrams with the right engine
order: 4
---

# Diagrams

ADK supports four diagramming engines, each suited for different use cases. The `diagram` router auto-detects the best engine from your request, or you can invoke a specific engine directly.

> **Quick start:** `/adk:diagram create a sequence diagram of the auth flow` — the router picks the best engine.

## Scenarios

- [Choose the right engine](#choose-the-right-engine)
- [Mermaid diagrams](#mermaid-diagrams)
- [Excalidraw diagrams](#excalidraw-diagrams)
- [Draw.io diagrams](#drawio-diagrams)
- [Graphviz diagrams](#graphviz-diagrams)
- [Rendering and export](#rendering-and-export)
- [Light and dark mode](#light-and-dark-mode)

---

## Choose the Right Engine

The `diagram` router selects the engine based on signals in your request. You can also pass `--engine` to override:

| Engine | Best For | File Format |
|--------|----------|-------------|
| **Mermaid** | Flowcharts, sequences, class diagrams, ER diagrams, Gantt charts, state machines | `.mmd` |
| **Excalidraw** | Hand-drawn style architecture overviews, freeform layouts, whiteboard-style diagrams | `.excalidraw` |
| **Draw.io** | Precise layout, network topology, enterprise architecture, BPMN, rich AWS/Azure/GCP icons | `.drawio` |
| **Graphviz** | Dependency graphs, call graphs, strict hierarchical layouts, existing `.dot` files | `.dot` |

### Decision guide

- **Need it in markdown?** Use Mermaid — renders inline on GitHub, Confluence, and most doc platforms
- **Explaining to non-technical stakeholders?** Use Excalidraw — approachable hand-drawn style
- **Infrastructure or cloud architecture?** Use Draw.io — rich icon library for AWS, Azure, GCP
- **Visualizing dependencies or imports?** Use Graphviz — strict layout algorithms for directed graphs
- **Already have diagrams in the project?** ADK prefers the engine matching existing diagram files

### Router override

```text
/adk:diagram --engine mermaid auth flow diagram
/adk:diagram --engine excalidraw system architecture overview
```

---

## Mermaid Diagrams

Mermaid supports 21 diagram types. Use `--type` to specify, or let ADK auto-detect from your description.

### Flowchart

```text
/adk:diagram-mermaid create a flowchart of the user registration process
/adk:diagram-mermaid --type flowchart CI/CD pipeline with build, test, deploy stages
```

### Sequence diagram

```text
/adk:diagram-mermaid --type sequence OAuth2 authorization code flow between client, auth server, and resource server
```

### Class diagram

```text
/adk:diagram-mermaid --type classDiagram class hierarchy for the payment module
```

### Entity relationship diagram

```text
/adk:diagram-mermaid --type erDiagram database schema for the e-commerce system
```

### State diagram

```text
/adk:diagram-mermaid --type stateDiagram order lifecycle states from created to delivered
```

### Gantt chart

```text
/adk:diagram-mermaid --type gantt project timeline for Q3 milestones
```

### Other Mermaid types

ADK supports all 21 Mermaid types: `flowchart`, `sequence`, `classDiagram`, `stateDiagram`, `erDiagram`, `gantt`, `pie`, `quadrantChart`, `requirementDiagram`, `gitgraph`, `mindmap`, `timeline`, `sankey`, `journey`, `xychart`, `block`, `packet`, `kanban`, `architecture`, `c4`, `zenuml`.

---

## Excalidraw Diagrams

Hand-drawn style diagrams ideal for architecture overviews and presentations.

```text
/adk:diagram-excalidraw system architecture overview with frontend, API gateway, microservices, and database
```

### Palettes

Use themed color palettes for cloud architecture:

```text
/adk:diagram-excalidraw --palette aws AWS infrastructure diagram with VPC, subnets, and load balancer
/adk:diagram-excalidraw --palette k8s Kubernetes cluster architecture
```

Available palettes: `default`, `aws`, `azure`, `gcp`, `k8s`.

---

## Draw.io Diagrams

Precise layout with rich icon libraries for enterprise and cloud architecture.

```text
/adk:diagram-drawio network topology diagram with firewalls, load balancers, and app servers
/adk:diagram-drawio BPMN process for order fulfillment workflow
```

Draw.io excels at diagrams that need exact positioning and professional icon sets (AWS, Azure, GCP shapes).

---

## Graphviz Diagrams

Strict layout algorithms for dependency and hierarchy visualization.

```text
/adk:diagram-graphviz module dependency graph for the Python packages
/adk:diagram-graphviz call graph for the request handling pipeline
```

### Layout algorithms

```text
/adk:diagram-graphviz --layout dot dependency tree (top-to-bottom hierarchy)
/adk:diagram-graphviz --layout neato network topology with force-directed layout
/adk:diagram-graphviz --layout circo circular dependency visualization
```

Available layouts: `dot` (hierarchical), `neato` (force-directed), `fdp` (force-directed, large graphs), `sfdp` (scalable force-directed), `circo` (circular), `twopi` (radial).

---

## Rendering and Export

All diagram engines support rendering to images via diagramkit.

### Render to PNG

```text
/adk:diagram-mermaid --render --format png auth flow sequence diagram
```

### Render to SVG

```text
/adk:diagram-excalidraw --render --format svg system architecture
```

### Source only (no render)

By default, diagrams are rendered if diagramkit is available. To get only the source file:

```text
/adk:diagram-mermaid auth flow sequence diagram
```

---

## Light and Dark Mode

All engines support theme selection:

```text
/adk:diagram-mermaid --theme dark auth flow diagram
/adk:diagram-excalidraw --theme light system architecture
/adk:diagram-drawio --theme dark network topology
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Auto-detect engine | `diagram` | `--engine`, `--type` |
| Flowchart / sequence / ER / class | `diagram-mermaid` | `--type`, `--render`, `--format` |
| Hand-drawn architecture | `diagram-excalidraw` | `--palette`, `--render`, `--theme` |
| Enterprise / cloud / BPMN | `diagram-drawio` | `--render`, `--format`, `--theme` |
| Dependency / call graphs | `diagram-graphviz` | `--layout`, `--render`, `--format` |

## Related Skills

- **[`docs-write`](/reference/skills/docs-write/)** — embed diagrams in formal documents
- **[`design`](/reference/skills/design/)** — UI/UX design with HTML previews
