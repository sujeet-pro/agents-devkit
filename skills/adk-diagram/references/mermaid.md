# Mermaid Reference

Use Mermaid for text-first diagrams that should diff cleanly in Git and live comfortably next to markdown docs.

Accepted source extensions:

- `.mermaid`
- `.mmd`
- `.mmdc`

Use `diagramkit-integration.md` for rendering commands and `markdown-integration.md` for embeds. This guide focuses on how to build the Mermaid source correctly.

## Build Rules

1. Start every source file with a comment header:

```text
%% Diagram: <title>
%% Type: <diagram-type>
```

1. Pick the smallest diagram type that matches the job.
2. Use semantic IDs such as `auth_service` or `orders_api`, not `a` or `n1`.
3. Keep a single diagram focused. Split large systems into multiple diagrams instead of forcing 30+ nodes into one file.
4. Prefer `classDef` and `linkStyle` over repetitive inline styling.
5. Use hex colors, not named colors.
6. Let `diagramkit` control theme selection during render; do not hardcode Mermaid theme directives unless the project explicitly requires it.
7. For diagrams embedded via `<img>` tags in browsers or webviews, add `%%{init: {'htmlLabels': false}}%%` at the top of the source file. This ensures the rendered SVG uses native SVG text instead of `<foreignObject>`, which fails when loaded as an image.

## Type Routing


| Type           | Directive              | Best for                                                   |
| -------------- | ---------------------- | ---------------------------------------------------------- |
| `flowchart`    | `flowchart TD`         | Process flows, pipelines, service handoffs, decision trees |
| `sequence`     | `sequenceDiagram`      | Message passing, API exchanges, protocols                  |
| `class`        | `classDiagram`         | OOP structure, inheritance, interfaces                     |
| `state`        | `stateDiagram-v2`      | State machines and lifecycle transitions                   |
| `er`           | `erDiagram`            | Database entities and relationships                        |
| `gantt`        | `gantt`                | Timelines, schedules, rollout plans                        |
| `gitgraph`     | `gitGraph`             | Branching and release histories                            |
| `mindmap`      | `mindmap`              | Concept maps and decision trees                            |
| `timeline`     | `timeline`             | Milestones, roadmaps, history                              |
| `c4`           | `C4Context` or friends | C4 architecture views                                      |
| `pie`          | `pie`                  | Simple categorical distribution                            |
| `quadrant`     | `quadrantChart`        | Priority or evaluation matrices                            |
| `sankey`       | `sankey-beta`          | Flow volumes between stages                                |
| `xy`           | `xychart-beta`         | Small chart-like comparisons                               |
| `block`        | `block-beta`           | Structured block layouts                                   |
| `architecture` | `architecture-beta`    | Icon-driven architecture diagrams                          |
| `kanban`       | `kanban`               | Board-style work status views                              |
| `journey`      | `journey`              | User journey or service experience maps                    |
| `packet`       | `packet-beta`          | Bit- or field-level packet layouts                         |
| `radar`        | `radar-beta`           | Multi-axis comparison                                      |
| `requirement`  | `requirementDiagram`   | Requirements tracing                                       |


## Flowchart

- Directive: `flowchart TD` or `flowchart LR`
- Use when: the diagram is mostly nodes, decisions, and directed flow

```text
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

    A --> B
    A -.-> C
    A ==> D

    subgraph title
        nodes...
    end
```

```text
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

## Sequence

- Directive: `sequenceDiagram`
- Use when: ordering, call timing, or participant interactions are the important part

```text
sequenceDiagram
    participant A as Alice
    participant B as Bob
    actor U as User

    A->>B: Synchronous message
    A-->>B: Dashed response
    A-)B: Async message

    activate B
    B->>A: Response
    deactivate B

    Note over A,B: Shared note

    alt Condition
        A->>B: Path 1
    else Other
        A->>B: Path 2
    end

    loop Every minute
        A->>B: Heartbeat
    end

    par Parallel
        A->>B: Task 1
    and
        A->>C: Task 2
    end

    autonumber
```

```text
%% Diagram: OAuth2 Authorization Code Flow
%% Type: sequence
sequenceDiagram
    autonumber
    actor user as User
    participant app as Client App
    participant auth as Auth Server
    participant api as Resource API

    user->>app: Click "Login"
    app->>auth: Authorization request
    auth->>user: Show login form
    user->>auth: Enter credentials
    auth->>app: Authorization code
    app->>auth: Exchange code for token
    auth->>app: Access token + refresh token
    app->>api: API request (Bearer token)
    api->>app: Protected resource
    app->>user: Display data
```

## Class

- Directive: `classDiagram`
- Use when: you need visibility, methods, interfaces, inheritance, or multiplicity

```text
classDiagram
    class ClassName {
        +String publicField
        -int privateField
        #List~String~ protectedField
        +publicMethod() ReturnType
        -privateMethod(param: Type) void
    }

    ClassA <|-- ClassB : inherits
    ClassA *-- ClassC : composition
    ClassA o-- ClassD : aggregation
    ClassA --> ClassE : association
    ClassA ..> ClassF : dependency
    ClassA ..|> InterfaceG : implements
    ClassA "1" --> "*" ClassH : multiplicity
```

```text
%% Diagram: Repository Pattern
%% Type: class
classDiagram
    class Repository~T~ {
        <<interface>>
        +findById(id: string) T
        +findAll() List~T~
        +save(entity: T) void
        +delete(id: string) void
    }

    class UserRepository {
        -db: Database
        +findById(id: string) User
        +findAll() List~User~
        +save(user: User) void
        +delete(id: string) void
        +findByEmail(email: string) User
    }

    class User {
        +String id
        +String email
        +String name
        -String passwordHash
        +verifyPassword(password: string) bool
    }

    Repository~T~ <|.. UserRepository : implements
    UserRepository --> User : manages
```

## State

- Directive: `stateDiagram-v2`
- Use when: states and transitions matter more than message sequencing

```text
stateDiagram-v2
    [*] --> State1
    State1 --> State2 : event
    State2 --> [*]

    state fork_state <<fork>>
    state join_state <<join>>
    state if_state <<choice>>

    state CompositeState {
        [*] --> SubState1
        SubState1 --> SubState2
    }

    note right of State1 : Note text
```

```text
%% Diagram: Order Lifecycle
%% Type: state
stateDiagram-v2
    [*] --> draft : Create Order

    state "Order Processing" as processing {
        draft --> pending_payment : Submit
        pending_payment --> paid : Payment Received
        paid --> preparing : Start Preparation

        state payment_check <<choice>>
        pending_payment --> payment_check : Check Payment
        payment_check --> paid : Success
        payment_check --> payment_failed : Declined

        payment_failed --> pending_payment : Retry
        payment_failed --> cancelled : Max retries
    }

    preparing --> shipped : Ship Order
    shipped --> delivered : Confirm Delivery
    delivered --> [*]
    cancelled --> [*]
```

## ER

- Directive: `erDiagram`
- Use when: you need entities, attributes, and crow's-foot cardinality

```text
erDiagram
    ENTITY1 ||--o{ ENTITY2 : "relationship"

    ENTITY {
        type name PK "comment"
        type name FK
        type name UK
    }
```

```text
%% Diagram: E-Commerce Data Model
%% Type: er
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        uuid id PK
        string email UK
        string name
        timestamp created_at
    }

    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        uuid id PK
        uuid customer_id FK
        decimal total
        enum status "pending|paid|shipped|delivered"
    }

    ORDER_ITEM }o--|| PRODUCT : references
```

## Gantt

- Directive: `gantt`
- Use when: scheduling, sequencing, and milestones are central

```text
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends

    section Section Name
    Task Name        :id, start_date, duration
    Active Task      :active, id, start_date, duration
    Critical Task    :crit, id, start_date, duration
    Milestone        :milestone, id, start_date, 0d
    After dependency :id, after other_id, duration
```

```text
%% Diagram: Sprint Plan
%% Type: gantt
gantt
    title Q2 Sprint 4
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends

    section Backend
    API redesign       :crit, api, 2025-04-07, 5d
    Database migration :db, after api, 3d
    Integration tests  :test, after db, 2d

    section QA
    Regression testing :qa, after test, 3d
    Release            :milestone, release, after qa, 0d
```

## GitGraph

- Directive: `gitGraph`
- Use when: branch flow and merge history are the primary story

```text
gitGraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "feature-start"
    branch feature/auth
    checkout feature/auth
    commit id: "add-login"
    checkout develop
    merge feature/auth id: "merge-auth"
```

```text
%% Diagram: Git Branching Strategy
%% Type: gitgraph
gitGraph
    commit id: "init"
    branch develop
    commit id: "setup-ci"
    branch feature/user-auth
    commit id: "auth-models"
    commit id: "auth-routes"
    checkout develop
    merge feature/user-auth id: "merge-auth"
    checkout main
    merge develop id: "release" tag: "v1.0.0"
```

## Mindmap

- Directive: `mindmap`
- Use when: hierarchy, concept grouping, or branching ideas are the goal

```text
mindmap
    root((Central Topic))
        Branch 1
            Leaf 1a
            Leaf 1b
        Branch 2
            Leaf 2a
                Sub-leaf
```

```text
%% Diagram: System Architecture Decision Map
%% Type: mindmap
mindmap
    root((Architecture<br/>Decisions))
        Frontend
            React SPA
                Next.js SSR
                Vite CSR
        Backend
            API Design
                REST
                GraphQL
        Infrastructure
            Cloud Provider
                AWS
                GCP
```

## Timeline

- Directive: `timeline`
- Use when: you want grouped chronology without task scheduling semantics

```text
timeline
    title Timeline Title
    section Period 1
        Event 1 : Description
        Event 2 : Description
    section Period 2
        Event 3 : Description
```

```text
%% Diagram: Product Roadmap
%% Type: timeline
timeline
    title 2025 Product Roadmap
    section Q1
        Auth System : OAuth2 integration
                    : SSO support
    section Q2
        Mobile App : iOS launch
                   : Android launch
    section Q3
        Marketplace : Partner integrations
                    : Payment processing
```

## C4

- Directives: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`
- Use when: you want standard C4 semantics inside Mermaid

```text
C4Context
    title System Context

    Person(user, "User", "Description")
    System(system, "System", "Description")
    System_Ext(ext, "External System", "Description")
    SystemDb(db, "Database", "Description")
    System_Boundary(boundary, "Boundary Label") {
        System(inner, "Inner System", "Description")
    }

    Rel(user, system, "Uses", "HTTPS")
    BiRel(system, ext, "Exchanges data", "gRPC")
    Rel_D(system, db, "Reads/writes", "SQL")
```

```text
%% Diagram: E-Commerce System Context
%% Type: c4
C4Context
    title E-Commerce Platform - System Context

    Person(customer, "Customer", "Browses and purchases products")
    Person(admin, "Admin", "Manages inventory and orders")

    System(ecommerce, "E-Commerce Platform", "Handles product catalog, orders, and payments")
    System_Ext(payment, "Payment Gateway", "Processes credit card transactions")
    System_Ext(shipping, "Shipping Provider", "Handles order fulfillment")

    Rel(customer, ecommerce, "Browses, orders", "HTTPS")
    Rel(admin, ecommerce, "Manages", "HTTPS")
    Rel(ecommerce, payment, "Processes payments", "HTTPS/API")
```

## Pie

- Directive: `pie`
- Use when: a small part-to-whole comparison is enough and richer chart tooling is unnecessary

```text
pie title Chart Title
    "Segment 1" : 40
    "Segment 2" : 30
    "Segment 3" : 20
```

```text
%% Diagram: Error Distribution
%% Type: pie
pie title Production Errors by Category
    "Timeout" : 35
    "Auth Failure" : 25
    "Validation" : 20
    "Database" : 12
    "External API" : 8
```

## Quadrant

- Directive: `quadrantChart`
- Use when: ranking items across two axes matters more than process flow

```text
quadrantChart
    title Chart Title
    x-axis Low --> High
    y-axis Low --> High
    quadrant-1 Label
    quadrant-2 Label
    quadrant-3 Label
    quadrant-4 Label
    Item A: [0.8, 0.9]
    Item B: [0.3, 0.7]
```

```text
%% Diagram: Technical Debt Prioritization
%% Type: quadrant
quadrantChart
    title Technical Debt Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Plan Carefully
    quadrant-3 Deprioritize
    quadrant-4 Quick Wins
    Upgrade Node.js: [0.3, 0.9]
    Fix N+1 queries: [0.4, 0.8]
    Migrate to TypeScript: [0.9, 0.7]
```

## Sankey

- Directive: `sankey-beta`
- Use when: you need source-to-target volume movement

```text
sankey-beta

Source,Target,Value
Source1,Target1,25
Source1,Target2,15
Source2,Target1,10
```

```text
%% Diagram: Request Traffic Flow
%% Type: sankey
sankey-beta

CDN,API Gateway,500
CDN,Static Assets,300
API Gateway,Auth Service,200
API Gateway,User Service,150
Auth Service,Database,80
User Service,Cache,50
```

## XY

- Directive: `xychart-beta`
- Use when: a quick bar/line comparison should stay inside Mermaid instead of moving to `adk-chart`

```text
xychart-beta
    title "Chart Title"
    x-axis [label1, label2, label3]
    y-axis "Y Label" 0 --> 100
    bar [10, 20, 30]
    line [8, 15, 28]
```

```text
%% Diagram: API Response Times
%% Type: xy
xychart-beta
    title "API Latency by Endpoint (ms)"
    x-axis ["/users", "/orders", "/products", "/search", "/auth"]
    y-axis "P95 Latency (ms)" 0 --> 500
    bar [45, 120, 65, 350, 30]
    line [35, 90, 50, 280, 25]
```

## Block

- Directive: `block-beta`
- Use when: you need grouped block layouts without using Draw.io

```text
block-beta
    columns 3

    a["Block A"]:2 b["Block B"]
    c["Block C"] d["Block D"] e["Block E"]

    a --> c
    b --> d

    block:group1
        columns 2
        f["Inner F"] g["Inner G"]
    end
```

```text
%% Diagram: Deployment Architecture
%% Type: block
block-beta
    columns 3

    block:cdn["CDN Layer"]
        columns 1
        cf["CloudFront"]
    end

    block:compute["Compute"]
        columns 2
        ecs1["ECS Task 1"] ecs2["ECS Task 2"]
    end

    block:data["Data"]
        columns 2
        rds["RDS PostgreSQL"] redis["ElastiCache"]
    end

    cf --> ecs1
    cf --> ecs2
    ecs1 --> rds
    ecs2 --> redis
```

## Architecture

- Directive: `architecture-beta`
- Use when: the request fits Mermaid's icon-driven architecture format better than freeform layout tools

```text
architecture-beta
    group api(cloud)[API Layer]

    service gateway(internet)[API Gateway] in api
    service auth(server)[Auth Service] in api
    service db(database)[PostgreSQL]

    gateway:R --> L:auth
    auth:B --> T:db
```

```text
%% Diagram: Microservices Architecture
%% Type: architecture
architecture-beta
    group frontend(cloud)[Frontend]
    group backend(cloud)[Backend Services]
    group data(cloud)[Data Layer]

    service cdn(internet)[CDN] in frontend
    service spa(server)[SPA] in frontend
    service gateway(internet)[API Gateway] in backend
    service users(server)[User Service] in backend
    service orders(server)[Order Service] in backend
    service postgres(database)[PostgreSQL] in data

    cdn:R --> L:spa
    spa:B --> T:gateway
    gateway:B --> T:users
    gateway:B --> T:orders
    users:B --> T:postgres
```

## Kanban

- Directive: `kanban`
- Use when: a board view is clearer than a flow diagram

```text
kanban
    todo[To Do]
        t1[Task description]
    progress[In Progress]
        t2[Active work]
    done[Done]
        t3[Completed item]
```

```text
%% Diagram: Sprint Board
%% Type: kanban
kanban
    todo[To Do]
        t1[Setup CI pipeline]
        t2[Write API docs]
        t3[Add rate limiting]
    progress[In Progress]
        t4[Auth service refactor]
        t5[Database migration]
    review[In Review]
        t6[Fix pagination bug]
    done[Done]
        t7[Add health check endpoint]
```

## Journey

- Directive: `journey`
- Use when: scoring experience across phases or actors is the main job

```text
journey
    title Journey Title
    section Phase
        Task: score: actor1, actor2
```

```text
%% Diagram: User Onboarding Journey
%% Type: journey
journey
    title New User Onboarding
    section Discovery
        Visit landing page: 5: User
        Read pricing: 3: User
    section Signup
        Create account: 4: User
        Verify email: 2: User
    section First Use
        View dashboard: 4: User
        Create first project: 3: User, System
```

## Packet

- Directive: `packet-beta`
- Use when: packet headers or bit ranges are the important structure

```text
packet-beta
    0-15: "Field Name"
    16-31: "Another Field"
    32-47: "Third Field"
```

```text
%% Diagram: TCP Header
%% Type: packet
packet-beta
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    103-103: "NS"
    104-104: "CWR"
    111-111: "FIN"
    112-127: "Window Size"
```

## Radar

- Directive: `radar-beta`
- Use when: multiple options need comparison across shared axes

```text
radar-beta
    title "Chart Title"
    axis1: "Label" 0 --> 10
    axis2: "Label" 0 --> 10
    axis3: "Label" 0 --> 10

    "Series 1": [8, 6, 7]
    "Series 2": [5, 9, 4]
```

```text
%% Diagram: Framework Comparison
%% Type: radar
radar-beta
    title "Framework Evaluation"
    axis1: "Performance"
    axis2: "DX"
    axis3: "Ecosystem"
    axis4: "Learning Curve"
    axis5: "Community"

    "Next.js": [8, 9, 9, 6, 9]
    "Remix": [9, 8, 6, 5, 6]
    "SvelteKit": [9, 9, 5, 7, 5]
```

## Requirement

- Directive: `requirementDiagram`
- Use when: you need requirement IDs, verification methods, risk, and traceability

```text
requirementDiagram
    requirement req_name {
        id: REQ-001
        text: Requirement description
        risk: low
        verifymethod: test
    }

    functionalRequirement func_req {
        id: REQ-002
        text: Functional requirement
        risk: medium
        verifymethod: inspection
    }

    element impl_element {
        type: module
        docRef: src/module.ts
    }

    impl_element - satisfies -> req_name
    func_req - derives -> req_name
```

```text
%% Diagram: Auth Requirements
%% Type: requirement
requirementDiagram
    requirement auth_system {
        id: AUTH-001
        text: System shall authenticate users via OAuth2
        risk: high
        verifymethod: test
    }

    functionalRequirement token_mgmt {
        id: AUTH-002
        text: System shall issue and validate JWT tokens
        risk: medium
        verifymethod: test
    }

    element auth_module {
        type: module
        docRef: src/auth/index.ts
    }

    token_mgmt - derives -> auth_system
    auth_module - satisfies -> auth_system
```

## Theming And Dark Mode

When rendering with `diagramkit render`, Mermaid diagrams get automatic light and dark variants:

1. Light mode uses Mermaid's default rendering.
2. Dark mode applies a dark theme and post-processing for contrast.
3. Text, fills, and stroke colors are adjusted for readability on dark surfaces.

Do not hardcode Mermaid's theme directive unless the repository explicitly needs it. Let the renderer control theme selection.

Prefer `classDef` for reusable styling:

```text
flowchart TD
    A[API Gateway]:::primary --> B[Auth Service]:::secondary
    A --> C[User Service]:::secondary
    B --> D[(Database)]:::storage
    C --> D

    classDef primary fill:#4C78A8,stroke:#2E5A88,color:#fff
    classDef secondary fill:#72B7B2,stroke:#4A9A95,color:#fff
    classDef storage fill:#E4A847,stroke:#C08C35,color:#fff
```

Colors that usually survive both modes well:


| Purpose   | Fill      | Stroke    |
| --------- | --------- | --------- |
| Primary   | `#4C78A8` | `#2E5A88` |
| Secondary | `#72B7B2` | `#4A9A95` |
| Accent    | `#E45756` | `#C23B3A` |
| Storage   | `#E4A847` | `#C08C35` |
| Success   | `#54A24B` | `#3D8B3D` |
| Neutral   | `#9B9B9B` | `#7B7B7B` |


Avoid:

- `#ffffff` or near-white fills
- `#000000` or near-black fills
- named colors such as `red` or `blue`
- very saturated neon colors

You can style edges with `linkStyle` when necessary:

```text
flowchart TD
    A --> B
    A -.-> C
    linkStyle 0 stroke:#4C78A8,stroke-width:2px
    linkStyle 1 stroke:#E45756,stroke-width:1px,stroke-dasharray:5
```

## Quality Rules

- Keep most Mermaid diagrams under about 15 nodes unless the chosen type naturally expects more.
- Use clear labels and semantic IDs.
- Use subgraphs for groups of related nodes.
- Use `TD` for hierarchical flows and `LR` for request or pipeline flows unless another direction is clearer.
- Quote labels when the text contains punctuation or reserved words.
- Split large systems into overview and detail diagrams instead of creating one overloaded source file.

