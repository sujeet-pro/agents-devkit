# Flowchart

**Directive:** `flowchart TD` (or `LR`, `RL`, `BT`)

**Syntax:**

```
flowchart TD
    id[Rectangle]
    id2(Rounded)
    id3([Stadium])
    id4[[Subroutine]]
    id5[(Database)]
    id6((Circle))
    id7{Diamond}
    id8{{Hexagon}}
    id9[/Parallelogram/]
    id10[\Parallelogram alt\]
    id11[/Trapezoid\]
    id12[\Trapezoid alt/]

    %% Edge types
    A --> B           %% Arrow
    A --- B           %% Open link
    A -.- B           %% Dotted
    A -.-> B          %% Dotted arrow
    A ==> B           %% Thick arrow
    A -- text --> B   %% Arrow with text
    A -. text .-> B   %% Dotted with text
    A == text ==> B   %% Thick with text

    %% Subgraphs
    subgraph title
        nodes...
    end
```

**Example:**

```
%% Diagram: CI/CD Pipeline
%% Type: flowchart
flowchart LR
    subgraph build["Build Stage"]
        checkout[Checkout Code] --> lint[Run Linter]
        lint --> test[Run Tests]
        test --> compile[Compile]
    end

    subgraph deploy["Deploy Stage"]
        staging[Deploy Staging] --> smoke[Smoke Tests]
        smoke --> prod[Deploy Production]
    end

    compile --> staging
    prod --> monitor[Monitor Health]

    classDef stage fill:#4C78A8,stroke:#2E5A88,color:#fff
    class checkout,lint,test,compile stage
```
