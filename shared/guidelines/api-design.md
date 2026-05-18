# guideline: API design

> Loaded when the task involves an HTTP/RPC contract — REST/GraphQL/gRPC endpoint, internal RPC, SDK surface, library export.

## Decision: which protocol

- **REST/HTTPS JSON**: public APIs, cross-team, browser-first. Default unless reason to deviate.
- **GraphQL**: many client shapes, federated graphs, frontend velocity matters more than backend cache simplicity.
- **gRPC / Protobuf**: internal RPC, hot paths, polyglot services, strong contract typing.
- **WebSockets / SSE**: real-time push, bidirectional needed.

## REST hard rules

1. **Resource nouns, not verbs**. `/orders/123/items` not `/getOrderItems`.
2. **HTTP semantics**: GET safe + idempotent; POST creates; PUT replaces (idempotent); PATCH partial; DELETE idempotent.
3. **Status codes that mean what they say**. 200 only for actual success; 4xx for client error with body explaining; 5xx for server bug, never for a 404. Don't 200 + `{ok: false}`.
4. **Idempotency keys** for any non-idempotent endpoint clients retry. Header: `Idempotency-Key`.
5. **Pagination**: cursor-based (`?cursor=...&limit=20`). Offset-based fails at scale.
6. **Versioning**: header (`Accept: application/vnd.acme.v2+json`) or URL prefix (`/v2/...`). Pick one, document it, hold it.
7. **Errors**: structured body — `{error: {code, message, request_id}}`. Codes are machine-readable; messages are human-readable.

## Contract documents

- Every new endpoint ships with an OpenAPI 3.1 entry (or proto file for gRPC).
- Breaking changes go in CHANGELOG with explicit migration steps.
- Deprecate before removing: `Deprecation:` header + sunset date.

## Anti-patterns

- "Just add a flag" to a list endpoint to return a different shape. Add an explicit endpoint instead.
- Returning auth state as a body field; auth state is a header.
- Mixing read + write in one POST endpoint (`POST /orders/process` that maybe creates, maybe updates).
- Optional fields with magic defaults that change behavior server-side. Be explicit.
- Public APIs that lean on client-side validation. Validate server-side, period.

## GraphQL specifics

- Resolver-per-field is the abstraction. Don't fan out N+1 queries — use DataLoader.
- Authorize at field level for sensitive data, not just at root.
- Versioning: deprecate fields with `@deprecated(reason: ...)`, never remove without telemetry showing zero use.

## gRPC / proto specifics

- Field tags are forever. Never reassign or reuse a tag number.
- Add fields with sensible defaults; never remove fields, only deprecate.
- Stream vs unary: unary unless you need backpressure or persistent push.

## Cite when reviewing

- Repo's existing OpenAPI / proto.
- `security.md` for authn/authz on new endpoints.
- `observability.md` for instrumentation (every endpoint emits request_id, latency, status).
