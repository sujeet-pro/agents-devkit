# `docs-diagram` — worked examples

## Example 1 — sequence for a login flow

**Prompt:** `/adk-docs:docs-diagram sequence "OIDC login"`

`oidc-login.mermaid`:

```mermaid
%% OIDC login — drawn by adk-docs:docs-diagram on 2026-05-03 %%
sequenceDiagram
    actor U as User
    participant UI as Web UI
    participant BE as Backend
    participant IdP as OIDC IdP

    U->>UI: Click "Sign in"
    UI->>BE: POST /auth/start
    BE->>IdP: Redirect to authorize
    IdP-->>U: Credentials prompt
    U->>IdP: Enter credentials
    IdP-->>BE: Callback with code
    BE->>IdP: Exchange code for token
    IdP-->>BE: id_token + access_token
    BE-->>UI: Set session cookie
    UI-->>U: Signed in
```

10 participants/messages. Under budget.

## Example 2 — ER for the orders schema

**Prompt:** `/adk-docs:docs-diagram er "orders schema" --scope db/schema.sql`

`orders-schema.mermaid`:

```mermaid
%% orders schema — drawn by adk-docs:docs-diagram on 2026-05-03 %%
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_LINE : contains
    ORDER_LINE }o--|| SKU : references
    ORDER }o--|| PAYMENT : "paid by"
    ORDER }o--|| SHIPMENT : "shipped via"

    USER {
        uuid id PK
        string email
        timestamp created_at
    }
    ORDER {
        uuid id PK
        uuid user_id FK
        string status
        timestamp created_at
    }
    ORDER_LINE {
        uuid id PK
        uuid order_id FK
        uuid sku_id FK
        int quantity
        int price_cents
    }
    SKU {
        uuid id PK
        string code
        string name
    }
    PAYMENT {
        uuid id PK
        uuid order_id FK
        string status
        int amount_cents
    }
    SHIPMENT {
        uuid id PK
        uuid order_id FK
        string carrier
        string tracking
    }
```

6 entities; grounded in `db/schema.sql`.

## Example 3 — state machine for export jobs

**Prompt:** `/adk-docs:docs-diagram state "export job lifecycle"`

`export-job-lifecycle.mermaid`:

```mermaid
%% export job lifecycle — drawn by adk-docs:docs-diagram on 2026-05-03 %%
stateDiagram-v2
    [*] --> Pending
    Pending --> Running: worker picks up
    Running --> Succeeded: upload ok
    Running --> Failed: error
    Failed --> Pending: retry (manual)
    Succeeded --> [*]
    Failed --> [*]: abandon
```

4 states (plus start/end pseudo). Minimal.

## Example 4 — C4 container for checkout service

**Prompt:** `/adk-docs:docs-diagram c4 "checkout service" --scope services/checkout/`

`checkout-c4.mermaid`:

```mermaid
%% checkout service (C4 container) — drawn by adk-docs:docs-diagram on 2026-05-03 %%
C4Container
    title Checkout service — container view

    Person(user, "End user")
    System_Boundary(ckout, "Checkout") {
        Container(api, "API", "Kotlin / Spring Boot", "HTTPS")
        Container(worker, "Job worker", "Kotlin", "Redis queue")
        ContainerDb(db, "Orders DB", "Postgres 15")
        ContainerDb(cache, "Session cache", "Redis 7")
    }
    System_Ext(auth, "Auth IdP")
    System_Ext(payments, "Payments provider")

    Rel(user, api, "HTTPS")
    Rel(api, auth, "OIDC")
    Rel(api, db, "SQL")
    Rel(api, cache, "TCP")
    Rel(api, worker, "enqueue", "Redis")
    Rel(worker, payments, "HTTPS")
```

10 "boxes" (person + containers + external systems). Under budget.

## Example 5 — splitting a too-big diagram

**Prompt:** `/adk-docs:docs-diagram flowchart "full checkout architecture" --scope services/`

`elements.md` counts 23 nodes. The skill, under `--auto`, emits two files:

- `full-checkout.overview.mermaid` — 6 nodes: user, web, checkout, orders, payments, auth.
- `full-checkout.checkout-zoom.mermaid` — 9 nodes: the checkout service's internal components.

Report notes the split + suggests a third zoom-in if the orders
service internals are also of interest later.

## Example 6 — timeline for an incident

**Prompt:** `/adk-docs:docs-diagram timeline "2026-05-02 checkout outage"`

`checkout-outage-timeline.mermaid`:

```mermaid
%% 2026-05-02 checkout outage — drawn by adk-docs:docs-diagram on 2026-05-03 %%
timeline
    title 2026-05-02 Checkout Outage
    section Deploy
        12:58 : new version of checkout-api deployed (sha abc123)
    section Detection
        13:02 : DD monitor "checkout p99" fires
        13:04 : on-call acks in #platform-oncall
    section Mitigation
        13:12 : rollback started (git revert abc123)
        13:18 : rollback deployed; traffic shifting
    section Recovery
        13:22 : p99 recovered below SLO
        13:30 : incident closed
```

6 events. Short, readable.
