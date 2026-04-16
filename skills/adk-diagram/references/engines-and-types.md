# Engines And Types

## Reference Routing

Start with `README.md`, then use this file to choose the engine and the next detailed reference.

## Engine Selection

Use the smallest engine that fits the job:


| Signal                                                                                                                                                        | Engine     | Read next       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | --------------- |
| process, workflow, sequence, ER, class, state, timeline, gantt, C4, mindmap, pie, quadrant, sankey, XY, packet, radar, requirement, journey, or block diagram | Mermaid    | `mermaid.md`    |
| architecture overview, system context, codebase map, freeform explanation, or hand-drawn presentation visual                                                  | Excalidraw | `excalidraw.md` |
| network topology, cloud deployment, BPMN, org chart, enterprise system map, or multi-page layout                                                              | Draw.io    | `drawio.md`     |
| dependency graph, call graph, strict automatic layout, or existing `.dot` / `.gv` source                                                                      | Graphviz   | `graphviz.md`   |


If `--engine` is given, respect it unless the request is clearly incompatible with that source format.

## Mermaid Type Routing

When Mermaid is the chosen engine, use `--type` as the strongest hint and then read the matching section in `mermaid.md`.


| Type           | Use when                                                | Section                           |
| -------------- | ------------------------------------------------------- | --------------------------------- |
| `flowchart`    | process flow, pipeline, service handoff, decision tree  | `mermaid.md` -> `## Flowchart`    |
| `sequence`     | requests, callbacks, protocol exchange, auth handshakes | `mermaid.md` -> `## Sequence`     |
| `class`        | inheritance, interface, model structure                 | `mermaid.md` -> `## Class`        |
| `state`        | lifecycle, transitions, state machine                   | `mermaid.md` -> `## State`        |
| `er`           | entities, keys, crow's-foot relationships               | `mermaid.md` -> `## ER`           |
| `gantt`        | schedule, milestone plan, rollout timing                | `mermaid.md` -> `## Gantt`        |
| `gitgraph`     | branch strategy, merge flow, release history            | `mermaid.md` -> `## GitGraph`     |
| `mindmap`      | concept map, brainstorming tree, option breakdown       | `mermaid.md` -> `## Mindmap`      |
| `timeline`     | roadmap or chronological milestone view                 | `mermaid.md` -> `## Timeline`     |
| `c4`           | context, container, component, deployment view          | `mermaid.md` -> `## C4`           |
| `pie`          | small part-to-whole comparison                          | `mermaid.md` -> `## Pie`          |
| `quadrant`     | priority or evaluation matrix                           | `mermaid.md` -> `## Quadrant`     |
| `sankey`       | weighted flow between stages                            | `mermaid.md` -> `## Sankey`       |
| `xy`           | quick bar/line comparison inside Mermaid                | `mermaid.md` -> `## XY`           |
| `block`        | grouped block layout                                    | `mermaid.md` -> `## Block`        |
| `architecture` | icon-driven Mermaid architecture view                   | `mermaid.md` -> `## Architecture` |
| `kanban`       | board-style work status                                 | `mermaid.md` -> `## Kanban`       |
| `journey`      | user or service experience map                          | `mermaid.md` -> `## Journey`      |
| `packet`       | bit or header field layout                              | `mermaid.md` -> `## Packet`       |
| `radar`        | multi-axis comparison                                   | `mermaid.md` -> `## Radar`        |
| `requirement`  | requirements traceability                               | `mermaid.md` -> `## Requirement`  |


## Excalidraw Fit

Use Excalidraw when:

- layout matters more than strict syntax
- the user wants a hand-drawn or presentation-style overview
- the document needs a system-context or concept-map diagram rather than a procedural chart
- you need raw JSON guidance for labels, containers, or elbow arrows

## Draw.io Fit

Use Draw.io when:

- the diagram is infrastructure-heavy
- the value comes from precise layout and icon libraries
- the prompt mentions topology, cloud providers, racks, zones, swimlanes, or BPMN
- you need XML-level control over pages, containers, or connector styles

## Graphviz Fit

Use Graphviz when:

- the repo already contains `.dot`, `.gv`, or `.graphviz` files
- the diagram is mostly nodes and edges with strict layout rules
- clustering, rank constraints, or graph algorithms matter more than hand-tuned positions
- ports, record nodes, or explicit layout engines are part of the request

