# LLD-NNN: [Component Name] — Low Level Design

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Low Level Design |
| Document ID | LLD-NNN |
| Status | Draft |
| Owner | [name] |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Parent HLD / Tech Spec | [HLD-NNN / TS-NNN link] |
| Repository | [repo name and path] |

## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## 1. Component Specification

[One paragraph describing what this component does. Reference the parent HLD or Tech Spec for broader context.]

- **Boundary**: [What it owns, what it delegates, what it assumes about its environment]
- **Public Interface Surface**: [What other components or users can call or observe]
- **Dependencies**: [Libraries, services, infrastructure with specific versions where version matters]

## 2. Class / Module Structure

<!-- DIAGRAM: UML class diagram or module dependency diagram showing internal structure -->

### [Module/Class A]

- **Purpose**: [One sentence — why it exists]
- **Pattern**: [Repository / Factory / Strategy / etc.]
- **Public Methods**:

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| [name] | [typed params] | [return type] | [what it does] |

### [Module/Class B]

- **Purpose**: [One sentence]
- **Pattern**: [Design pattern if applicable]
- **Public Methods**:

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| [name] | [typed params] | [return type] | [what it does] |

## 3. API Endpoint Definitions

### [Endpoint Group Name]

#### `[METHOD] /api/v1/[resource]`

| Field | Value |
|-------|-------|
| Authentication | [Required auth method and permissions] |
| Rate Limit | [X requests/minute] |
| Idempotent | [Yes/No — idempotency key if applicable] |

**Request**:

```json
{
  "field": "type — description (required/optional, default, constraints)"
}
```

**Response 200**:

```json
{
  "field": "type — description"
}
```

**Error Responses**:

| Status | Error Code | Condition |
|--------|-----------|-----------|
| 400 | [VALIDATION_ERROR] | [Invalid input] |
| 404 | [NOT_FOUND] | [Resource does not exist] |
| 409 | [CONFLICT] | [Concurrent modification] |

## 4. Database Schema

### Table: [table_name]

| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NO | gen_random_uuid() | PK | [description] |
| [column] | [type] | [YES/NO] | [default] | [FK/UNIQUE/CHECK] | [description] |
| created_at | TIMESTAMPTZ | NO | NOW() | | Creation timestamp |
| updated_at | TIMESTAMPTZ | NO | NOW() | | Last modification |

**Indexes**:

| Index Name | Columns | Type | Optimizes |
|-----------|---------|------|-----------|
| [name] | [columns] | [B-tree/GIN/GiST] | [Which queries] |

**Partitioning**: [Strategy if applicable — partition key, retention policy]

<!-- DIAGRAM: ER diagram showing table relationships -->

### Migration

```sql
-- Migration: [description]
-- Up
[SQL statements]

-- Down
[Rollback SQL statements]
```

## 5. Sequence Diagrams

### Primary Flow: [Name]

<!-- DIAGRAM: Sequence diagram showing the happy path with all participating components -->

### Error Flow: [Name]

<!-- DIAGRAM: Sequence diagram showing the primary error path with timeouts and fallbacks -->

### Async Flow: [Name]

<!-- DIAGRAM: Sequence diagram showing eventual-consistency or async processing flows -->

## 6. Error Handling

### Error Codes

| Error Code | HTTP Status | Condition | User Message | Recovery Action |
|------------|-------------|-----------|-------------|----------------|
| [CODE] | [status] | [when this occurs] | [user-facing message] | [what to do] |

### External Dependency Failures

| Dependency | Timeout | Circuit Breaker | Fallback | Retry Policy |
|-----------|---------|----------------|----------|-------------|
| [Name] | [Xms] | [threshold, reset] | [cached/default/error] | [max retries, backoff, jitter] |

### Partial Failure Handling

[How multi-step operations handle partial failures — saga pattern, compensation, or manual intervention.]

## 7. Configuration

| Parameter | Type | Default | Constraints | Hot Reload | Env Override | Description |
|-----------|------|---------|-------------|-----------|-------------|-------------|
| [name] | [type] | [value] | [range] | [yes/no] | [ENV_VAR] | [description] |

### Environment-Specific Defaults

| Parameter | Dev | Staging | Production |
|-----------|-----|---------|------------|
| [name] | [value] | [value] | [value] |

## 8. Performance Considerations

### Hot Paths

| Path | Optimization | Expected Throughput | Expected Latency |
|------|-------------|-------------------|-----------------|
| [Name] | [Caching/Batching/Async] | [X req/sec] | [p99 < Xms] |

### Caching Strategy

| Cache | Key Structure | TTL | Invalidation | Pattern |
|-------|-------------|-----|-------------|---------|
| [Name] | [key format] | [duration] | [Triggers] | [Cache-aside/Write-through] |

### Known Bottlenecks

| Bottleneck | Mitigation | Status |
|-----------|-----------|--------|
| [Description] | [Connection pooling/Batching/Partitioning] | [Addressed/Planned] |
