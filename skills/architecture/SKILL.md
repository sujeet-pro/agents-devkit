---
name: architecture
description: "adk - [helper] [guidelines] Helper skill that provides software architecture patterns, principles, and review criteria. Used by review, audit, and design skills."
user-invocable: false
argument-hint: "[--focus frontend|backend|fullstack|infra]"
allowed-tools: [Glob, Grep, Read]
workflow-tier: helper
---

# Architecture Guidelines Loader

This skill scans the repository to determine the architecture type and loads the relevant architecture guidelines. Other skills invoke this before review, audit, design, or development work that involves architectural decisions.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--focus` | `frontend`, `backend`, `fullstack`, `infra` | auto-detect | Force a specific architecture focus area |

### Behavior Variations

- **Auto-detect** (default): scans project structure, dependencies, and config files to determine architecture type
- **`--focus <area>`**: overrides auto-detection and loads guidelines for the specified area
- Always loads core architecture principles
- Conditionally loads area-specific patterns based on detected or specified focus
- Loads anti-pattern detection criteria for all focus areas

### Examples

```
(invoked automatically by /adk:code-review-pr, /adk:audit, /adk:design, /adk:dev-build)
/adk:architecture --focus backend
/adk:architecture --focus fullstack
```

---

## Workflow

This is a helper skill invoked by other skills, not directly by users. It does not own the 6-phase workflow — the invoking skill does.

## Architecture Detection

Scan the repository to determine the primary architecture type and focus areas.

### Detection Signals

| Signal | Focus |
|--------|-------|
| `package.json` with React/Vue/Svelte/Angular | frontend |
| `next.config.*`, `nuxt.config.*`, `astro.config.*` | frontend (SSR/SSG) |
| `src/pages/`, `src/app/`, `src/components/` | frontend |
| `.storybook/`, design tokens, `tailwind.config.*` | frontend (design system) |
| `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml` | backend |
| `pyproject.toml` with FastAPI/Django/Flask | backend |
| `src/main/`, `cmd/`, `internal/` | backend |
| API route handlers, GraphQL schemas, OpenAPI specs | backend (API) |
| Both frontend and backend signals present | fullstack |
| `Dockerfile`, `docker-compose.*`, `k8s/`, `helm/` | infra |
| `terraform/`, `pulumi/`, `.github/workflows/` | infra |
| `Makefile`, `justfile`, CI config files | infra |

### Precedence

When multiple signals are present, select the broadest applicable focus:

1. If both frontend and backend signals → `fullstack`
2. If infra signals are dominant (no application code) → `infra`
3. Otherwise → the strongest single signal

---

## Core Architecture Principles

These apply regardless of focus area. Evaluate all code against these principles from a principal engineer perspective.

### Separation of Concerns

Each module, layer, or component should have a single, well-defined responsibility. UI rendering logic should not contain business rules. Data access should not know about HTTP transport.

### Single Responsibility

A class, module, or function should have one reason to change. When a change in business logic requires modifying the same file as a change in persistence logic, the responsibilities are tangled.

### Dependency Inversion

High-level modules should not depend on low-level modules. Both should depend on abstractions. Concretely: business logic imports interfaces, not database drivers. Frameworks are implementation details, not architectural foundations.

### Interface Segregation

No consumer should be forced to depend on methods it does not use. Prefer narrow, role-specific interfaces over broad ones. A `ReadRepository` and `WriteRepository` are better than a single `Repository` with twelve methods.

### CQRS (Where Applicable)

Separate read and write models when:
- Read and write loads differ significantly
- Read models benefit from denormalization
- Event sourcing is in play

Do not apply CQRS to simple CRUD systems — it adds complexity without proportional benefit.

### Event-Driven vs Request-Response

- **Request-response**: synchronous, easier to reason about, appropriate for user-facing operations that need immediate feedback
- **Event-driven**: asynchronous, better for decoupling, appropriate for cross-service communication, audit trails, and eventual consistency

Choose based on the consistency and latency requirements of the specific operation, not as a blanket architectural decision.

### Architecture Styles

| Style | When to Use | When to Avoid |
|-------|-------------|---------------|
| **Layered** (controller → service → repository) | Small to medium apps with clear request/response flows | When layers become pass-through with no logic |
| **Hexagonal** (ports & adapters) | When the domain must be framework-agnostic or testable in isolation | Simple CRUD apps where the indirection adds overhead |
| **Clean Architecture** | Complex domains with multiple delivery mechanisms (API, CLI, queue) | MVPs, prototypes, or apps with a single delivery mechanism |
| **Modular monolith** | Teams that need service boundaries without distributed system complexity | When services genuinely need independent deployment |
| **Microservices** | Independent deployment, scaling, and team ownership requirements | Early-stage products, small teams, or when boundaries are unclear |

---

## Frontend Architecture Patterns

Loaded when focus is `frontend` or `fullstack`.

### Component Hierarchy and Composition

- Prefer composition over inheritance — use render props, slots, or children
- Separate **container** components (data fetching, state management) from **presentational** components (rendering, styling)
- Keep component files under 300 lines — extract sub-components when complexity grows
- Co-locate related files: component, styles, tests, and types in the same directory

### State Management

| Pattern | When to Use |
|---------|-------------|
| **Local state** (useState, ref) | UI-only state: form inputs, toggles, modals |
| **Lifted state** | State shared between 2-3 sibling components |
| **Context / provide-inject** | App-wide settings: theme, locale, auth status |
| **External store** (Redux, Zustand, Pinia) | Complex cross-cutting state with derived data |
| **Server state** (React Query, SWR, TanStack Query) | API response caching, optimistic updates, background refetch |

Avoid duplicating server state in a client store. If the data comes from an API, use a server state library.

### Data Fetching Strategies

- **Fetch on mount**: simple, but causes waterfalls when nested components each fetch independently
- **Fetch in route loader**: eliminates waterfalls, enables parallel loading, best for route-level data
- **Streaming / suspense**: progressive rendering while data loads
- **Stale-while-revalidate**: show cached data immediately, refresh in background

Prefer route-level data loading over component-level fetching to avoid request waterfalls.

### Route-Based Code Splitting

- Split at route boundaries — each route loads its own chunk
- Use dynamic imports (`lazy()`, `defineAsyncComponent`) for heavy components
- Prefetch likely next routes on hover or viewport proximity
- Keep the initial bundle under 200KB (gzipped) for good Core Web Vitals

### Design System Integration

- Use design tokens (colors, spacing, typography) from the design system — never hardcode values
- Follow the component API surface defined by the design system
- Extend through composition and wrapper components, not by modifying the design system source
- Document deviations from the design system with rationale

---

## Backend Architecture Patterns

Loaded when focus is `backend` or `fullstack`.

### API Design

#### REST

- Use nouns for resources, HTTP verbs for actions (`GET /users`, `POST /orders`)
- Version APIs in the URL path (`/v1/`) or via Accept header
- Return consistent error shapes: `{ error: { code, message, details } }`
- Use appropriate HTTP status codes — 200 for success, 201 for creation, 400 for validation, 404 for not found, 409 for conflict, 500 for server errors
- Paginate collections with cursor-based or offset-based pagination
- Support filtering, sorting, and field selection via query parameters

#### GraphQL

- Design schema around domain concepts, not database tables
- Use DataLoader to batch and deduplicate database queries (N+1 prevention)
- Limit query depth and complexity to prevent abuse
- Separate Query and Mutation types clearly

#### gRPC

- Define services in `.proto` files with clear method contracts
- Use streaming for real-time or large-payload operations
- Version via package naming (`v1`, `v2`)

### Service Boundaries and Domain-Driven Design

- Identify bounded contexts by looking for natural seams: where different teams work, where language changes, where data ownership differs
- Each bounded context owns its data — no shared databases between contexts
- Use anti-corruption layers at context boundaries to translate between domain models
- Aggregate roots enforce invariants for their cluster of entities

### Database Access Patterns

| Pattern | When to Use |
|---------|-------------|
| **Repository** | When the domain layer must be persistence-agnostic |
| **Active Record** | Simple CRUD with 1:1 mapping between objects and tables |
| **Query Builder** | Complex queries that don't map to domain operations |
| **Raw SQL** | Performance-critical queries, reports, or analytics |

Prefer the simplest pattern that serves the use case. A repository wrapping an ORM wrapping SQL is three layers of indirection — use a repository only when domain isolation justifies it.

### Error Handling and Resilience

- Distinguish between **expected errors** (validation, not found, conflict) and **unexpected errors** (infrastructure failures, bugs)
- Expected errors return structured error responses with actionable messages
- Unexpected errors log full context, return generic messages, and trigger alerts
- Apply circuit breakers for external service calls
- Use retries with exponential backoff and jitter for transient failures
- Set timeouts on all external calls — never wait indefinitely
- Design for partial failure: degrade gracefully when a dependency is unavailable

### Observability

| Pillar | Purpose | Implementation |
|--------|---------|----------------|
| **Logging** | Discrete events | Structured JSON logs with correlation IDs |
| **Metrics** | Aggregate measurements | RED metrics (Rate, Errors, Duration) per service |
| **Tracing** | Request flow across services | Distributed traces with span context propagation |

- Every service should expose health check endpoints (`/health`, `/ready`)
- Log at appropriate levels: ERROR for failures requiring attention, WARN for degraded state, INFO for significant business events, DEBUG for development
- Include correlation/request IDs in all log entries for traceability

---

## Infrastructure Patterns

Loaded when focus is `infra` or when infrastructure files are detected.

### Container Orchestration

- Use multi-stage Docker builds to minimize image size
- Run containers as non-root users
- Pin base image versions — never use `:latest` in production
- Define resource requests and limits for every container
- Use health checks and readiness probes

### CI/CD Pipelines

- Pipeline stages: lint → test → build → security scan → deploy
- Keep builds fast: parallelize test suites, cache dependencies, use incremental builds
- Deploy to staging before production — never skip the staging step
- Use feature flags over long-lived feature branches
- Automate rollback: detect failure metrics and revert within SLA

### Infrastructure as Code

- All infrastructure must be defined in code — no manual console changes
- Use modules/functions to encapsulate reusable infrastructure components
- Store state remotely with locking (Terraform state, Pulumi state)
- Separate environment configs from infrastructure definitions
- Review infrastructure changes with the same rigor as application code

### Environment Management

- Use environment variables for runtime configuration — never hardcode secrets
- Manage secrets via a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager)
- Maintain parity between development, staging, and production environments
- Document any intentional differences between environments

---

## Anti-Patterns to Detect

Flag these when reviewing or auditing code. Each includes detection signals and severity.

### God Classes / God Modules

**Severity**: High
**Signals**: files over 500 lines, classes with 10+ methods spanning unrelated domains, modules imported by >50% of the codebase
**Fix**: decompose by responsibility into focused modules

### Circular Dependencies

**Severity**: High
**Signals**: import cycles, modules that import each other directly or transitively
**Fix**: extract shared abstractions, apply dependency inversion, introduce an event bus or mediator

### Leaky Abstractions

**Severity**: Medium
**Signals**: consumers working around an abstraction's limitations, catch-and-rethrow patterns that add no context, wrapper functions that pass through every parameter
**Fix**: redesign the abstraction to match actual usage patterns, or remove it if the underlying API is simpler

### Over-Engineering

**Severity**: Medium
**Signals**: premature abstraction (abstract base class with one implementation), speculative generality (configuration for features that don't exist), unnecessary indirection (service → adapter → repository → ORM → SQL for simple CRUD)
**Fix**: remove the abstraction, use the concrete implementation directly, add abstraction only when a second use case actually appears

### Under-Engineering

**Severity**: High
**Signals**: missing error handling (bare catch-all or no catch at all), no input validation on public APIs, no logging for failures, missing authentication/authorization checks, no rate limiting on public endpoints
**Fix**: add the missing safety nets — these are not optional in production code

---

## Output

Produce a summary listing the detected focus and loaded guidelines. The calling skill uses this to apply architecture standards.

```text
## Architecture Guidelines Loaded

Focus: backend (detected via go.mod, cmd/, internal/)

Loaded:
- Core architecture principles
- Backend architecture patterns
- Anti-pattern detection criteria

Detected patterns:
- Layered architecture (cmd/ → internal/service/ → internal/repository/)
- REST API (internal/handler/)
- Repository pattern (internal/repository/)
```
