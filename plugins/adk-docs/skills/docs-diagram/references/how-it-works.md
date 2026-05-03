# `docs-diagram` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User prompt: type + subject + optional --scope"] --> P0["Phase 0: classify type + slug + .temp/"]
    P0 --> P1["Phase 1: preflight (adk-info, scope exists, diagramkit)"]
    P1 --> ScopeArg{"--scope given?"}
    ScopeArg -- yes --> P2["Phase 2: read scope -> elements.md"]
    ScopeArg -- no --> P3["Phase 3: draft .mermaid from description"]
    P2 --> Budget{"Nodes > 15?"}
    Budget -- yes --> Split["Split: overview + zoom-in(s)"]
    Budget -- no --> P3
    Split --> P3
    P3 --> P4["Phase 4: validate syntax + render (if diagramkit)"]
    P4 --> P5["Phase 5: report + embed snippet"]
```

## Type classifier

```mermaid
flowchart TD
    Prompt["Subject + context"] --> Q1{"Interaction between actors?"}
    Q1 -- yes --> Sequence["sequenceDiagram"]
    Q1 -- no --> Q2{"Lifecycle / status transitions?"}
    Q2 -- yes --> State["stateDiagram-v2"]
    Q2 -- no --> Q3{"Data entities + relations?"}
    Q3 -- yes --> ER["erDiagram"]
    Q3 -- no --> Q4{"UML class hierarchy?"}
    Q4 -- yes --> Class["classDiagram"]
    Q4 -- no --> Q5{"Architecture / containers?"}
    Q5 -- yes --> C4["C4Container"]
    Q5 -- no --> Q6{"Time-ordered events?"}
    Q6 -- durations --> Gantt["gantt"]
    Q6 -- events only --> Timeline["timeline"]
    Q6 -- no --> Q7{"Git branching?"}
    Q7 -- yes --> GitGraph["gitgraph"]
    Q7 -- no --> Q8{"Hierarchical outline?"}
    Q8 -- yes --> Mindmap["mindmap"]
    Q8 -- no --> Flowchart["flowchart (default)"]
```

## Split strategy selection

```mermaid
flowchart TD
    Big["elements.md > 15 nodes"] --> Shape{"What shape?"}
    Shape -- has subsystems --> Overview["Overview + zoom-in per subsystem"]
    Shape -- lifecycle --> Phases["Split by lifecycle phase"]
    Shape -- many actors --> PerActor["One sequence per actor view"]
    Overview --> Limit["Cap at 3 diagrams per run"]
    Phases --> Limit
    PerActor --> Limit
    Limit --> Emit["Emit split diagrams"]
```
