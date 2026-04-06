# Mindmap

**Directive:** `mindmap`

**Syntax (indentation-based):**

```
mindmap
    root((Central Topic))
        Branch 1
            Leaf 1a
            Leaf 1b
        Branch 2
            Leaf 2a
                Sub-leaf
            Leaf 2b
        Branch 3
```

Node shapes: `((circle))`, `(rounded)`, `[square]`, `))bang((`, `{{hexagon}}`, default (no brackets).

**Example:**

```
%% Diagram: System Architecture Decision Map
%% Type: mindmap
mindmap
    root((Architecture<br/>Decisions))
        Frontend
            React SPA
                Next.js SSR
                Vite CSR
            State Management
                Zustand
                React Query
        Backend
            API Design
                REST
                GraphQL
            Runtime
                Node.js
                Deno
        Infrastructure
            Cloud Provider
                AWS
                GCP
            Container Orchestration
                Kubernetes
                ECS
        Data
            Primary DB
                PostgreSQL
                MySQL
            Cache
                Redis
                Memcached
```
