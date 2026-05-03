# Mermaid types catalog

The 10 diagram types `docs-diagram` supports, with when-to-use, sweet
spot, and minimal idiomatic syntax. Used by the type classifier and
the draft step.

## 1. flowchart — branching / decision / process

### When to use
- Conditional flow with decisions.
- Default when nothing else fits.

### Sweet spot
- 5-10 nodes, 3-7 edges, 1-2 decision diamonds.

### Syntax

```mermaid
flowchart TD
    A["Start"] --> B{"Decision?"}
    B -- yes --> C["Do X"]
    B -- no --> D["Do Y"]
    C --> E["Done"]
    D --> E
```

## 2. sequenceDiagram — interactions over time

### When to use
- Request-response across services.
- Actor → system → actor flows.

### Sweet spot
- 3-5 participants, 5-15 messages.

### Syntax

```mermaid
sequenceDiagram
    actor U as User
    participant A as API
    participant D as DB
    U->>A: GET /orders
    A->>D: SELECT ...
    D-->>A: rows
    A-->>U: JSON
```

## 3. classDiagram — UML class hierarchies

### When to use
- OOP hierarchy; inheritance; interfaces.
- SDK surface.

### Sweet spot
- 3-8 classes, clear interface/implementation distinction.

### Syntax

```mermaid
classDiagram
    class AuthClient {
        +login(email) Session
        +logout()
    }
    class OidcAuthClient {
        +login(email) Session
    }
    AuthClient <|-- OidcAuthClient
```

## 4. stateDiagram-v2 — lifecycle / state machine

### When to use
- Finite states with transitions.
- Order / job / resource lifecycle.

### Sweet spot
- 3-7 states, 4-10 transitions.

### Syntax

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Running
    Running --> Succeeded
    Running --> Failed
    Failed --> Pending: retry
    Succeeded --> [*]
```

## 5. erDiagram — entity-relationship

### When to use
- Database schema overview.
- Data-domain model.

### Sweet spot
- 4-8 entities; relationships first, column lists second.

### Syntax

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER {
        uuid id PK
        uuid user_id FK
        string status
    }
```

## 6. gantt — time-bound tasks with durations

### When to use
- Project / release / migration timeline.
- Tasks with start + duration, not just events.

### Sweet spot
- 5-10 tasks, 1-3 sections.

### Syntax

```mermaid
gantt
    title Q3 Migration
    dateFormat YYYY-MM-DD
    section Auth
    Enable dual-stack    :2026-07-01, 14d
    Migrate clients      :14d
    Remove legacy path   :2026-08-15, 7d
```

## 7. gitgraph — git branching model

### When to use
- Explaining the release branching / trunk model.
- Tracking a specific merge flow.

### Sweet spot
- 1-3 branches, 5-10 commits.

### Syntax

```mermaid
gitGraph
    commit id: "main"
    branch feature
    commit id: "feat A"
    commit id: "feat B"
    checkout main
    merge feature
    commit id: "release"
```

## 8. mindmap — hierarchical brainstorm

### When to use
- Concept decomposition.
- Feature hierarchy.

### Sweet spot
- 3 levels deep; 3-5 children per parent.

### Syntax

```mermaid
mindmap
  root((Platform))
    Checkout
      Cart
      Orders
    Auth
      OIDC
      Session
    Observability
      Metrics
      Traces
```

## 9. timeline — events over time

### When to use
- Event-ordered narrative (incident, release history).
- Events, not durations.

### Sweet spot
- 2-4 sections, 5-15 events total.

### Syntax

```mermaid
timeline
    title Release history
    section 2026 Q2
        2026-05-01 : v1.2.0
        2026-05-15 : v1.2.1
    section 2026 Q3
        2026-07-10 : v2.0.0 (OIDC)
```

## 10. C4 — architecture (C4 model)

### When to use
- Architecture docs; system / container / component view.
- Cross-system boundaries.

### Sweet spot
- 4-8 containers + 1-3 external systems.

### Syntax

```mermaid
C4Container
    title Checkout — container view
    Person(user, "User")
    System_Boundary(ck, "Checkout") {
        Container(api, "API", "Kotlin / Spring Boot")
        ContainerDb(db, "Orders DB", "Postgres 15")
    }
    Rel(user, api, "HTTPS")
    Rel(api, db, "SQL")
```

(Note: the exact C4 Mermaid syntax may need the `C4Context`,
`C4Container`, or `C4Component` variant depending on zoom level;
pick based on the subject.)

## Type → file extension

All 10 types go into `.mermaid` files. GitHub / Confluence /
diagramkit all render via the first-line declaration
(`sequenceDiagram`, `flowchart TD`, etc.).
