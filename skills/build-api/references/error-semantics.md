# Error semantics — status codes and error envelope

This reference is the canonical mapping `build-api` follows when designing or evolving an HTTP / RPC contract. Internalize this table; deviations require an explicit reason in the contract notes.

## HTTP status codes — semantic table

| Status | Use when | Do NOT use for |
| --- | --- | --- |
| `200 OK` | Successful read or successful write that returns a representation. | Logical errors smuggled into a `success: false` body. |
| `201 Created` | A new resource was created; include `Location` header. | Idempotent updates (use 200). |
| `202 Accepted` | Work was accepted for asynchronous processing; return a status URL. | Synchronous work that has finished — use 200 / 201. |
| `204 No Content` | Successful operation with no response body (DELETE, idempotent PUT with no representation). | When the client needs ANY information back — use 200. |
| `301 / 308` | Permanent move; safe to cache. | Temporary redirect — use 302/307. |
| `400 Bad Request` | Generic client error; the request was malformed (e.g. unparseable JSON). | Logical validation errors — use 422. |
| `401 Unauthorized` | No credentials, or credentials invalid; client can retry after authenticating. | Authenticated user lacking permission — use 403. |
| `403 Forbidden` | Authenticated and identified, but not allowed to perform this action on this resource. | Resource doesn't exist — use 404 (unless leaking existence is itself a problem). |
| `404 Not Found` | The resource doesn't exist or is not visible to the caller. | Authorization failures where existence-leak matters (use 404 anyway, intentionally). |
| `409 Conflict` | Request conflicts with current resource state (e.g. version conflict, duplicate unique key). | Validation errors — use 422. |
| `410 Gone` | The resource existed and is permanently removed. | Temporarily unavailable — use 503. |
| `422 Unprocessable Entity` | Request was syntactically valid but semantically invalid (validation errors per field). | Generic parse errors — use 400. |
| `429 Too Many Requests` | Rate-limited; include `Retry-After`. | Server overload — use 503. |
| `500 Internal Server Error` | Unexpected server-side failure; do NOT leak the cause. | Known business errors — use the appropriate 4xx. |
| `502 Bad Gateway` | Upstream returned an invalid response. | This service's own failure — use 500. |
| `503 Service Unavailable` | Service is temporarily down (maintenance, overload); include `Retry-After` if known. | Persistent failure — use 500. |
| `504 Gateway Timeout` | Upstream timed out. | This service's own slow code path — use 500 + log. |

## Standard error envelope (recommended default)

Pick ONE envelope for the whole repo. Common shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable, safe to show.",
    "details": [
      { "field": "email", "issue": "must be a valid email address" }
    ],
    "request_id": "req_01HXYZ..."
  }
}
```

Rules:

- `code` is a stable, machine-readable string (`VALIDATION_ERROR`, `RATE_LIMITED`, `NOT_FOUND`, `CONFLICT`, `UNAUTHORIZED`, `FORBIDDEN`, `INTERNAL_ERROR`). Adding a new code is an additive contract change; renaming one is breaking.
- `message` is for humans, NOT for branching logic. Consumers must branch on `code`, not `message`.
- `details` is optional, structured per `code`.
- `request_id` lets the caller include it in a support ticket and helps correlate server logs.
- NEVER include stack traces, SQL fragments, internal paths, env names, or credentials in any error response — even at 500.

## Idempotency

- `GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE` are idempotent by HTTP definition; uphold it.
- `POST` is not idempotent; if you need it to be, accept an `Idempotency-Key` header and document its semantics (window of validity, scope).
- Retry safety: callers will retry on 5xx and on network errors. Idempotency must hold across these retries.

## Pagination

Pick ONE strategy per repo:

- **Cursor-based** (preferred for large or active datasets): `?limit=50&cursor=...`; response includes `next_cursor` (and `prev_cursor` if needed).
- **Page/offset** (acceptable for small, mostly-stable datasets): `?page=2&page_size=50`; response includes `total` only when cheap.
- Always cap `limit` server-side. Document the cap in the schema.

## Versioning posture

Choose explicitly per surface:

- **Additive-only** (preferred for internal monorepo APIs): no version segment; new fields are optional; existing fields never change shape.
- **URL-versioned** (e.g. `/v1/...`): clear, easy for caches and routing; bump only on breaking changes.
- **Header-versioned** (`Accept: application/vnd.api+json;version=2`): more flexible for partner APIs; harder to cache.
- **Per-resource versioning**: avoid; explosion of combinations.

## Naming conventions

- URL paths: lowercase, kebab-case, plural nouns (`/customers/{id}/orders`).
- JSON bodies: pick one casing repo-wide (`snake_case` or `camelCase`) and never mix.
- Booleans: positive form (`is_active`), not negative (`is_not_disabled`).
- Timestamps: ISO 8601 in UTC with the `Z` suffix; field name ends in `_at` (`created_at`, `updated_at`).
- IDs: prefix-typed string (`cust_01HXYZ...`) — easier to tell apart in logs than raw UUIDs.

## CLI / library surface

The same rules apply by analogy:

- Flags: `--kebab-case`, long form for clarity, short form only for the most-used flags. Document defaults explicitly.
- Library exports: one public `index.ts` (or equivalent); deep imports are NOT part of the contract unless explicitly documented.
- Errors: thrown errors are part of the contract — type them, name them, don't change the class hierarchy quietly.
