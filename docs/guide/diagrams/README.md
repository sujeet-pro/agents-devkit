---
title: Diagrams
description: Create architecture, flow, sequence, and dependency diagrams with the right engine
order: 4
---

# Diagrams

Use the `diagram` router when you know what you want to explain but not which rendering engine fits best. If you already know the engine, call the engine-specific skill directly.

> **Quick start:** `/adk:diagram <prompt-text>` lets the router choose the engine from the diagram type, the prompt, and the existing assets in the repository.

## Scenarios

- [Let The Router Choose](#let-the-router-choose)
- [Mermaid For Text-First Diagrams](#mermaid-for-text-first-diagrams)
- [Excalidraw For Hand-Drawn Overviews](#excalidraw-for-hand-drawn-overviews)
- [Drawio For Precise Layouts](#drawio-for-precise-layouts)
- [Graphviz For Strict Graphs](#graphviz-for-strict-graphs)
- [Render And Theme Output](#render-and-theme-output)

---

## Let The Router Choose

Start here when you have a diagram request but not a preferred engine.

```text
/adk:diagram <prompt-text>
/adk:diagram system context for the payments platform
/adk:diagram --engine mermaid <prompt-text>
/adk:diagram --engine excalidraw <prompt-text>
```

Use `--engine` only when you want to bypass routing and force a specific backend.

---

## Mermaid For Text-First Diagrams

Mermaid is the most natural fit for flowcharts, sequence diagrams, state diagrams, ER diagrams, timelines, and other text-native diagram types.

```text
/adk:diagram-mermaid <prompt-text>
/adk:diagram-mermaid --type sequence <prompt-text>
/adk:diagram-mermaid --type sequence OAuth2 authorization code flow
/adk:diagram-mermaid --type er <prompt-text>
```

When the diagram needs to live comfortably in markdown or be easy to diff in Git, Mermaid is usually the best choice.

---

## Excalidraw For Hand-Drawn Overviews

Use Excalidraw when the goal is an approachable architecture sketch or a whiteboard-style explanation.

```text
/adk:diagram-excalidraw <prompt-text>
/adk:diagram-excalidraw system architecture overview with frontend, API, and database
/adk:diagram-excalidraw --palette aws <prompt-text>
```

The palette flag is useful when you want the output to visually match a cloud or platform context.

---

## Drawio For Precise Layouts

Use draw.io when exact positioning, rich icon sets, BPMN, or infrastructure layouts matter more than raw text diffs.

```text
/adk:diagram-drawio <prompt-text>
/adk:diagram-drawio network topology with firewalls and load balancers
```

This is the best fit for enterprise architecture diagrams and cloud/network topology where shapes and placement do a lot of the explanatory work.

---

## Graphviz For Strict Graphs

Use Graphviz when the important part is the graph structure itself: dependency maps, call graphs, import graphs, and other strictly laid out relationships.

```text
/adk:diagram-graphviz <prompt-text>
/adk:diagram-graphviz module dependency graph
/adk:diagram-graphviz --layout dot <prompt-text>
```

The layout flag lets you steer the graph algorithm when you need a specific hierarchy or visual balance.

---

## Render And Theme Output

All engines can produce rendered assets when you need SVG or PNG output rather than source alone.

```text
/adk:diagram-mermaid --render --format png <prompt-text>
/adk:diagram-excalidraw --theme dark <prompt-text>
```

Use `--render` when the deliverable is the image asset itself, and use `--theme` when you want a specific light, dark, or dual-theme output.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the engine | `diagram` | `<prompt-text>`, `--engine`, `--type` |
| Text-first flow, sequence, state, ER, or timeline | `diagram-mermaid` | `<prompt-text>`, `--type`, `--render`, `--format` |
| Hand-drawn architecture overview | `diagram-excalidraw` | `<prompt-text>`, `--palette`, `--theme` |
| Precise enterprise or network layout | `diagram-drawio` | `<prompt-text>` |
| Dependency or call graph | `diagram-graphviz` | `<prompt-text>`, `--layout` |

## Related Skills

- **[`docs-write`](/reference/skill-docs-write/)** when the diagram is part of a larger document.
- **[`spec`](/reference/skill-spec/)** when the diagram is a supporting artifact for a durable technical specification.
- **[`design`](/reference/skill-design/)** when the task is product or UI design rather than technical system visualization.
