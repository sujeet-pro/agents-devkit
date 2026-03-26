# Low Level Design (LLD) Guidelines

Guidelines for writing and reviewing Low Level Design sections. An LLD provides implementation-level detail for a single component or feature, sufficient for a developer to implement without guesswork about expected behavior, interfaces, or edge cases.

**Important**: LLD is typically a **section within a Tech Spec**, not a separate document. Use these guidelines when writing the "Detailed Design (LLD)" section of a Tech Spec (see `tdd.md`). Create a standalone LLD document only when the system is large enough that the implementation details require their own review audience separate from the architecture overview.

**Audience**: Developers who will implement and maintain the component, and reviewers who need to verify the design is complete and correct.

**References**:
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [HLD vs LLD — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/difference-between-high-level-design-and-low-level-design/)

---

## 1. Required Sections

Every LLD must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Component Specification | Scope, responsibilities, and boundaries of the component. |
| 2 | Class/Module Diagrams | Internal structure showing classes, modules, and their relationships. |
| 3 | API Endpoint Definitions | Complete interface specification for all endpoints. |
| 4 | Database Schema Details | Table definitions, indexes, constraints, and migrations. |
| 5 | Sequence Diagrams for Key Flows | Step-by-step interaction sequences for critical operations. |
| 6 | Error Handling Specification | All error conditions, codes, and recovery behavior. |
| 7 | Configuration Specification | All configurable parameters with types, defaults, and constraints. |
| 8 | Performance Considerations | Optimization strategies, caching, and known bottlenecks. |

---

## 2. Content Standards

### Component Specification
- State what this component does in one paragraph. Reference the parent HLD or TDD for broader context.
- Define the component boundary: what it owns, what it delegates, and what it assumes about its environment.
- List all dependencies (libraries, services, infrastructure) with specific versions where version matters.
- Identify the public interface surface: what other components or users can call or observe.

### Class/Module Diagrams
- Show the internal structure using UML class diagrams or module dependency diagrams.
- For each class or module, document:
  - **Purpose**: One sentence describing why it exists.
  - **Public methods**: Signature, parameters, return type, and brief description.
  - **Key relationships**: Inheritance, composition, dependency injection.
- Indicate which classes are public API and which are internal implementation details.
- Use design patterns by name when applicable (Repository, Factory, Strategy, etc.) so implementers understand the intent.

### API Endpoint Definitions
- Every endpoint must be fully specified:

| Field | Requirement |
|---|---|
| HTTP Method | GET, POST, PUT, PATCH, DELETE |
| Path | Full path including path parameters (e.g., `/api/v1/users/{userId}/orders`) |
| Request Headers | Required and optional headers with types |
| Query Parameters | Name, type, required/optional, default, constraints |
| Request Body | Full JSON schema with field types, constraints, and examples |
| Response Body | Schema for each status code (200, 201, 400, 404, 500, etc.) |
| Error Responses | Error code, message format, and when each error occurs |
| Authentication | Required auth method and minimum permissions |
| Rate Limiting | Limits per endpoint if they differ from defaults |

- Provide a concrete request/response example for each endpoint.
- Document idempotency behavior for mutating endpoints.

### Database Schema Details
- For each table or collection, document:
  - Column/field name, data type, nullable, default value, and constraints.
  - Primary key, foreign keys, and unique constraints.
  - Indexes with included columns and the queries they optimize.
  - Partitioning strategy if applicable (partition key, retention policy).
- Include the migration script or migration steps for schema changes.
- Document the read/write patterns the schema is optimized for.
- Address data volume estimates and growth rate to justify index and partition choices.

### Sequence Diagrams for Key Flows
- Include a sequence diagram for every operation that involves more than two components or has non-obvious ordering.
- At minimum, cover: the primary happy path, the most common error path, and any asynchronous or eventual-consistency flows.
- Each diagram must show:
  - All participating actors and components.
  - The exact method calls or messages exchanged.
  - Return values and error conditions.
  - Timing constraints or timeouts where relevant.
- Number the steps and reference them in the explanatory text.

### Error Handling Specification
- **Enumerate all error codes** the component can produce. Use a table:

| Error Code | HTTP Status | Condition | User-Facing Message | Recovery Action |
|---|---|---|---|---|
| `ORDER_NOT_FOUND` | 404 | Order ID does not exist | "Order not found" | Verify the order ID |
| `INSUFFICIENT_STOCK` | 409 | Requested quantity exceeds available stock | "Not enough items in stock" | Reduce quantity or retry later |

- For each external dependency, document what happens when it fails: timeout, circuit breaker behavior, fallback response, and retry policy.
- Specify retry policies with concrete parameters: max retries, backoff strategy (linear, exponential), jitter, and maximum delay.
- Document how partial failures are handled in multi-step operations (saga pattern, compensation, or manual intervention).

### Configuration Specification
- List every configurable parameter in a table:

| Parameter | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `db.pool.maxSize` | integer | 20 | 1-100 | Maximum database connection pool size |
| `cache.ttl.seconds` | integer | 300 | 60-3600 | Cache entry time-to-live |
| `retry.maxAttempts` | integer | 3 | 1-10 | Maximum retry attempts for transient failures |

- Distinguish between build-time, deploy-time, and runtime configuration.
- Document which parameters require a restart and which can be changed dynamically.
- Specify environment-specific overrides (dev, staging, production defaults).

### Performance Considerations
- Identify the expected hot paths and document the optimization strategy for each.
- Specify caching strategy: what is cached, cache key structure, TTL, invalidation triggers, and cache-aside vs write-through behavior.
- Document database query plans for critical queries if performance is a concern.
- Identify known bottlenecks and the mitigation approach (connection pooling, batching, async processing).
- State the expected throughput and latency targets for this component, derived from the HLD's NFRs.

---

## 3. Structure & Flow

- The LLD must be specific enough that a developer can implement the component by following the document. If a decision is left ambiguous, the document is incomplete.
- Reference the HLD for context but do not duplicate it. The LLD covers "how", not "what" or "why" at the system level.
- Use concrete examples throughout. Abstract descriptions like "the service processes the request" are not helpful; show the actual data transformations.
- All edge cases must be specified. If the behavior for an edge case is undefined, list it as an open question. Do not leave gaps for implementers to guess.

---

## 4. Common Issues

- **Missing edge cases**: The document covers the happy path but does not specify what happens with empty inputs, maximum-size payloads, concurrent modifications, or clock skew.
- **Incomplete error specification**: Errors are described generically ("returns an error") without specific codes, messages, or recovery guidance.
- **Schema without migration plan**: New tables or columns are defined but the migration from the current state is not described.
- **Sequence diagrams without error paths**: Diagrams show only the happy path. The error and timeout paths are where most bugs live.
- **Configuration without constraints**: Parameters are listed without valid ranges, leading to misconfiguration in production.
- **Vague performance section**: "We will add caching" without specifying what, where, or how invalidation works.

---

## 5. Review Checklist

- [ ] Component boundary and responsibilities are clearly defined
- [ ] Class/module diagram shows internal structure with public interfaces identified
- [ ] Every API endpoint has method, path, full request/response schemas, and error responses
- [ ] Concrete request/response examples are provided for each endpoint
- [ ] Database schema includes column types, constraints, indexes, and migration steps
- [ ] Sequence diagrams cover happy path, primary error path, and async flows
- [ ] All error codes are enumerated with HTTP status, condition, and recovery action
- [ ] Retry policies specify max retries, backoff strategy, and maximum delay
- [ ] All configuration parameters are listed with type, default, and constraints
- [ ] Performance section addresses caching strategy with invalidation approach
- [ ] Edge cases are explicitly specified, not left to implementer judgment
- [ ] Document is detailed enough for implementation without additional design meetings
- [ ] No TODO/TBD placeholders remain in the final version
