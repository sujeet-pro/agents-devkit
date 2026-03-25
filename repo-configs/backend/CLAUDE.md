# Backend Repository

This is a **backend** repository (Java or Python). All code, reviews, and generation must follow backend engineering best practices for reliability, security, and maintainability.

## Devkit Integration

Load backend guidelines from the agents-devkit installation:

```
~/.claude/guidelines/general.md          — baseline code quality rules
~/.claude/guidelines/backend-java.md     — Java-specific rules (if available)
~/.claude/guidelines/backend-python.md   — Python-specific rules (if available)
```

Apply the general guidelines always. Apply the language-specific guidelines based on the primary language of this repository.

## API Design

### RESTful Conventions

1. **Use nouns for resource endpoints.** `/users`, `/orders`, `/products` — not `/getUsers`, `/createOrder`.
2. **HTTP methods convey intent:**
   - `GET` — read (safe, idempotent)
   - `POST` — create (not idempotent)
   - `PUT` — full replace (idempotent)
   - `PATCH` — partial update (idempotent)
   - `DELETE` — remove (idempotent)
3. **Consistent response structure.** All responses must follow a standard envelope:
   ```json
   {
     "data": { ... },
     "meta": { "page": 1, "totalPages": 10 },
     "errors": []
   }
   ```
4. **Use proper HTTP status codes:**
   - `200` OK, `201` Created, `204` No Content
   - `400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `409` Conflict, `422` Unprocessable Entity
   - `500` Internal Server Error, `503` Service Unavailable
5. **Version APIs.** Use URL path versioning (`/api/v1/users`) or header versioning.
6. **Pagination for all list endpoints.** Support `page`/`pageSize` or cursor-based pagination. Never return unbounded result sets.
7. **Consistent filtering and sorting.** Use query parameters: `?status=active&sort=createdAt&order=desc`.

### API Documentation

- Every endpoint must have OpenAPI/Swagger documentation
- Request and response schemas must be defined
- Error responses must be documented with example payloads
- Authentication requirements must be specified per endpoint

## Error Handling

### Principles

1. **Fail fast.** Validate all inputs at the boundary (controller/handler level). Do not let invalid data propagate deep into the system.
2. **Use typed errors.** Define application-specific exception/error classes with error codes, not generic exceptions.
3. **Error responses must be actionable.** Include:
   - A machine-readable error code (e.g., `USER_NOT_FOUND`, `INVALID_EMAIL`)
   - A human-readable message
   - Contextual details (which field failed validation, what the constraint is)
   - A request/correlation ID for debugging
4. **Never expose internal details in production.** Stack traces, SQL queries, file paths, and internal service names must not appear in API responses.
5. **Log errors with context.** Every caught exception must be logged with: the operation being performed, relevant entity IDs, the user/request context, and the full stack trace.
6. **Distinguish client errors from server errors.** Client errors (4xx) are expected and should not trigger alerts. Server errors (5xx) indicate bugs or outages and must trigger alerts.

### Error Hierarchy

```
ApplicationException
├── ValidationException (400)
├── AuthenticationException (401)
├── AuthorizationException (403)
├── NotFoundException (404)
├── ConflictException (409)
└── InternalException (500)
```

## Security

### Authentication and Authorization

1. **Authenticate every request** at the middleware/filter level. No endpoint should be accidentally public.
2. **Use role-based or attribute-based access control.** Check permissions at the service layer, not just at the controller.
3. **Validate tokens server-side.** Never trust client-provided claims without server verification.
4. **Session management.** Use secure, HttpOnly, SameSite cookies or short-lived JWTs with refresh tokens.

### Input Validation

1. **Validate all external input.** Request bodies, query parameters, path parameters, headers, and file uploads.
2. **Use allowlists.** Define what is permitted, not what is forbidden.
3. **Parameterize all queries.** Never concatenate user input into SQL, NoSQL, LDAP, or shell commands.
4. **Sanitize output.** Encode data appropriately for its destination (HTML, JSON, XML, logs).

### Data Protection

1. **Encrypt sensitive data at rest** (passwords with bcrypt/argon2, PII with AES-256).
2. **Use TLS for all network communication.**
3. **Never log sensitive data.** PII, passwords, tokens, credit card numbers, and API keys must not appear in logs.
4. **Audit trail.** Log security-relevant events: login, logout, permission changes, data access, admin operations.

### Dependency Security

1. **Scan dependencies for vulnerabilities** in CI (Snyk, OWASP Dependency-Check, or similar).
2. **Pin dependency versions.** Use lockfiles and review dependency updates before merging.
3. **Minimize dependencies.** Every dependency is an attack surface.

## Testing

### Test Pyramid

```
        /  E2E Tests  \         — few, critical paths only
       / Integration    \       — API + database + external services
      /   Unit Tests      \     — many, fast, isolated
```

### Test Requirements

1. **Unit tests for all business logic.** Services, validators, utilities, and domain models must have comprehensive unit tests.
2. **Integration tests for all API endpoints.** Every endpoint must have tests covering:
   - Happy path with valid input
   - Validation errors with invalid input
   - Authentication/authorization (authenticated, unauthenticated, wrong role)
   - Edge cases (empty results, pagination boundaries, concurrent access)
3. **Database tests use transactions or containers.** Tests must not depend on external database state. Use test containers, in-memory databases, or transaction rollback.
4. **External service calls must be mocked.** Tests must not make real HTTP calls to external services. Use WireMock, responses, or similar.
5. **Test data factories.** Use builder patterns or factory functions for test data. Do not copy-paste test data across tests.

### Test Quality

- Tests must be deterministic (no flakiness)
- Tests must be independent (no ordering dependencies)
- Test names must describe the behavior being verified
- Each test must have a single assertion focus (test one thing)

## PR Review Configuration

When reviewing PRs in this repository, automatically apply the `[be]` tag.

### Patterns to Watch For

1. **SQL injection**: String concatenation in queries instead of parameterized queries. Flag as CRITICAL.
2. **Missing authentication checks**: Endpoints or operations without auth verification. Flag as CRITICAL.
3. **Swallowed exceptions**: Empty catch blocks or catch blocks that only log without re-throwing or handling. Flag as WARNING.
4. **Missing input validation**: Controller/handler methods that pass raw input to service layer without validation. Flag as WARNING.
5. **N+1 queries**: Database queries inside loops. Flag as WARNING.
6. **Missing pagination**: List endpoints that return unbounded result sets. Flag as WARNING.
7. **Secrets in code**: API keys, passwords, connection strings hardcoded in source files. Flag as CRITICAL.
8. **Missing error responses**: New endpoints without proper error handling and error response documentation. Flag as WARNING.
9. **Missing tests**: New endpoints or business logic without test coverage. Flag as WARNING.
10. **Sensitive data in logs**: Logging PII, tokens, passwords, or other sensitive information. Flag as CRITICAL.

## Logging Standards

### Required Fields

Every log entry must include:
- Timestamp (ISO 8601)
- Log level (DEBUG, INFO, WARN, ERROR)
- Correlation/request ID
- Service name
- Message

### Log Levels

- **DEBUG**: Detailed diagnostic information for development
- **INFO**: Notable events in normal operation (request received, job completed)
- **WARN**: Unexpected situations that the system can handle (retry, fallback)
- **ERROR**: Failures that need investigation (unhandled exceptions, external service failures)

### Rules

- Use structured logging (JSON format) for production
- Include relevant entity IDs in log messages for traceability
- Never log sensitive data (see Security section)
- Log at the appropriate level (do not use ERROR for expected business conditions)

## Database Practices

1. **Migrations are versioned and forward-only.** Use Flyway, Alembic, or similar.
2. **Indexes for all query patterns.** Every `WHERE`, `JOIN`, and `ORDER BY` clause must be backed by an appropriate index.
3. **Connection pooling.** Always use connection pools. Configure pool sizes based on expected concurrency.
4. **Transactions for multi-step operations.** Use database transactions when multiple writes must succeed or fail together.
5. **Optimistic locking for concurrent updates.** Use version columns to prevent lost updates.
