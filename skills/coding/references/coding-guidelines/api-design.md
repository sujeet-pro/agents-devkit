# API Design Review Guidelines

These guidelines apply to **API design** across REST, GraphQL, and RPC-style
interfaces. They supplement the general guidelines with rules for building APIs
that are consistent, evolvable, and pleasant to consume.

---

## 1. REST Resource Design

- **Use plural nouns for resources.** Resources represent collections; individual
  items are addressed by identifier:
  ```
  GET    /api/v1/orders          # list orders
  POST   /api/v1/orders          # create an order
  GET    /api/v1/orders/{id}     # get a specific order
  PUT    /api/v1/orders/{id}     # replace an order
  PATCH  /api/v1/orders/{id}     # partially update an order
  DELETE /api/v1/orders/{id}     # delete an order
  ```
- **HTTP method semantics** must be respected:
  - `GET` is safe and idempotent. It must not produce side effects.
  - `PUT` is idempotent. Sending the same request twice yields the same state.
  - `DELETE` is idempotent. Deleting an already-deleted resource returns 204 or 404
    consistently -- pick one and be consistent.
  - `POST` is neither safe nor idempotent by default (see idempotency section).
  - `PATCH` applies a partial update. Use JSON Merge Patch (RFC 7396) or JSON Patch
    (RFC 6902) with the appropriate `Content-Type`.
- **Nest resources to express relationships**, but limit nesting to one level:
  ```
  GET /api/v1/orders/{orderId}/items          # items within an order
  GET /api/v1/orders/{orderId}/items/{itemId} # specific item

  # Avoid deep nesting:
  # BAD: /api/v1/customers/{cid}/orders/{oid}/items/{iid}/reviews
  # GOOD: /api/v1/item-reviews/{reviewId}
  ```
- **Use query parameters for filtering, sorting, and searching**:
  ```
  GET /api/v1/orders?status=shipped&sort=-createdAt&q=widget
  ```
- **Do not use verbs in URLs** for standard CRUD. For non-CRUD actions that do not
  map cleanly to a resource, use a sub-resource or action endpoint:
  ```
  POST /api/v1/orders/{id}/cancel     # action on a resource
  POST /api/v1/orders/{id}/refund     # action on a resource
  ```

> **Reference**: [RFC 9110 -- HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110),
> [RFC 7231 -- HTTP/1.1 Semantics and Content](https://www.rfc-editor.org/rfc/rfc7231)

## 2. HTTP Status Codes

- **Use the correct status code for every response.** Common mappings:

  | Status | Meaning | When to Use |
  |--------|---------|-------------|
  | `200`  | OK | Successful GET, PUT, PATCH |
  | `201`  | Created | Successful POST that creates a resource (include `Location` header) |
  | `204`  | No Content | Successful DELETE, or PUT/PATCH with no response body |
  | `301`  | Moved Permanently | Resource URL has permanently changed |
  | `304`  | Not Modified | Conditional GET with `ETag`/`If-None-Match` |
  | `400`  | Bad Request | Malformed syntax, missing required fields |
  | `401`  | Unauthorized | Missing or invalid authentication credentials |
  | `403`  | Forbidden | Authenticated but not authorized for this action |
  | `404`  | Not Found | Resource does not exist |
  | `409`  | Conflict | Duplicate creation, concurrent modification conflict |
  | `422`  | Unprocessable Entity | Syntactically valid but semantically invalid (business rule violation) |
  | `429`  | Too Many Requests | Rate limit exceeded (include `Retry-After` header) |
  | `500`  | Internal Server Error | Unexpected server failure |
  | `502`  | Bad Gateway | Upstream service returned an invalid response |
  | `503`  | Service Unavailable | Server temporarily unable to handle requests |

- **Never return `200` for errors.** The status code is the primary signal for
  clients to determine success or failure.
- **Distinguish 400 from 422.** Use 400 for malformed requests (bad JSON, wrong
  content type). Use 422 for requests that are syntactically correct but violate
  business rules.

> **Reference**: [IANA HTTP Status Code Registry](https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml)

## 3. Error Responses

- **Use RFC 7807 Problem Details** format for all error responses. This provides
  a machine-readable, extensible structure:
  ```json
  {
      "type": "https://api.example.com/errors/insufficient-funds",
      "title": "Insufficient Funds",
      "status": 422,
      "detail": "Account balance ($12.50) is less than the withdrawal amount ($50.00).",
      "instance": "/api/v1/accounts/acc-123/withdraw",
      "accountId": "acc-123",
      "balance": 12.50,
      "requestedAmount": 50.00
  }
  ```
- **Required fields**: `type` (URI identifying the error type), `title` (short
  human-readable summary), `status` (HTTP status code).
- **Validation errors** should include per-field details:
  ```json
  {
      "type": "https://api.example.com/errors/validation",
      "title": "Validation Failed",
      "status": 400,
      "errors": [
          { "field": "email", "message": "Must be a valid email address" },
          { "field": "items", "message": "Must contain at least one item" }
      ]
  }
  ```
- **Use the `Content-Type: application/problem+json`** header for Problem Details
  responses.
- **Error messages must be safe for end users.** Never expose stack traces, internal
  class names, or database error messages in API responses. Log the full details
  server-side.

> **Reference**: [RFC 7807 -- Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc7807),
> [RFC 9457 -- Problem Details (updated)](https://www.rfc-editor.org/rfc/rfc9457)

## 4. Versioning

- **Version APIs in the URL path** for major versions. This is the most explicit,
  cacheable, and debuggable approach:
  ```
  /api/v1/orders
  /api/v2/orders
  ```
- **Use request headers for minor/non-breaking changes** when you need clients to
  opt into new behavior without a new URL path:
  ```
  Accept: application/vnd.example.v1.2+json
  ```
- **Avoid query parameter versioning** (`?version=2`). It complicates caching and
  is easy to forget.
- **Versioning policy**:
  - A new major version is required for breaking changes (removing fields, changing
    field types, changing response structure).
  - Additive changes (new optional fields, new endpoints) are backward-compatible
    and do not require a new version.
  - Deprecate old versions with a timeline. Return `Sunset` and `Deprecation`
    headers on deprecated endpoints.
- **Run old and new versions simultaneously** during migration periods. Do not
  force all clients to upgrade at once.

> **Reference**: [API Versioning Best Practices](https://cloud.google.com/apis/design/versioning),
> [Sunset Header RFC draft](https://www.rfc-editor.org/rfc/rfc8594)

## 5. Pagination

- **Cursor-based pagination** is preferred for most use cases. It handles real-time
  data changes gracefully and performs well on large datasets:
  ```json
  // Request
  GET /api/v1/orders?limit=20&cursor=eyJpZCI6MTAwfQ

  // Response
  {
      "data": [ /* ... 20 orders ... */ ],
      "pagination": {
          "next_cursor": "eyJpZCI6MTIwfQ",
          "has_more": true
      }
  }
  ```
- **Offset/limit pagination** is acceptable for simple cases where the total count
  is useful and data does not change frequently:
  ```json
  // Request
  GET /api/v1/products?offset=40&limit=20

  // Response
  {
      "data": [ /* ... 20 products ... */ ],
      "pagination": {
          "offset": 40,
          "limit": 20,
          "total": 523
      }
  }
  ```
- **Default and maximum page sizes.** Always enforce a maximum (e.g., 100). Provide
  a sensible default (e.g., 20). Never allow unbounded result sets.
- **Include pagination metadata** in the response body or `Link` headers. Provide
  `next` and `prev` links so clients do not need to construct URLs.

> **Reference**: [Slack API Pagination](https://api.slack.com/docs/pagination),
> [Stripe API Pagination](https://docs.stripe.com/api/pagination)

## 6. Idempotency

- **PUT and DELETE are naturally idempotent.** Sending the same request multiple
  times produces the same server state.
- **POST requires explicit idempotency handling.** Use an `Idempotency-Key` header
  for operations that create resources or trigger side effects:
  ```
  POST /api/v1/payments
  Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
  Content-Type: application/json

  { "amount": 100.00, "currency": "USD", "recipient": "acct-456" }
  ```
- **Server-side implementation**:
  1. On first request: process normally, store the response keyed by the
     idempotency key with a TTL (e.g., 24 hours).
  2. On duplicate request: return the stored response without re-processing.
  3. If a request with the same key but different body arrives, return `422
     Unprocessable Entity`.
- **Clients should generate idempotency keys** as UUIDs. The server should not
  generate them.
- **PATCH idempotency**: PATCH is not inherently idempotent. Use conditional
  requests (`If-Match` with ETags) to prevent lost updates.

> **Reference**: [Stripe Idempotent Requests](https://docs.stripe.com/api/idempotent_requests),
> [IETF Idempotency-Key Header](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)

## 7. Rate Limiting

- **Return `429 Too Many Requests`** when a client exceeds their rate limit.
  Include the `Retry-After` header (in seconds) so clients know when to retry:
  ```
  HTTP/1.1 429 Too Many Requests
  Retry-After: 30
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1710000000
  ```
- **Sliding window algorithm** is recommended for most use cases. Fixed windows
  allow burst traffic at window boundaries; sliding windows spread the limit
  evenly.
- **Rate limit headers** on every response so clients can self-regulate:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: UTC epoch timestamp when the window resets
- **Differentiate rate limits** by authentication level (anonymous < authenticated <
  premium), endpoint sensitivity, and HTTP method (writes should have stricter
  limits than reads).
- **Document rate limits** in your API documentation. Include the limits, the
  window duration, and what headers to check.

> **Reference**: [IETF RateLimit Header Fields](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/),
> [RFC 6585 Section 4 (429)](https://www.rfc-editor.org/rfc/rfc6585#section-4)

## 8. HATEOAS

- **Use HATEOAS when it adds genuine value**: multi-step workflows, state machines,
  APIs consumed by generic clients that discover actions dynamically.
  ```json
  {
      "id": "order-123",
      "status": "pending",
      "_links": {
          "self": { "href": "/api/v1/orders/order-123" },
          "cancel": { "href": "/api/v1/orders/order-123/cancel", "method": "POST" },
          "payment": { "href": "/api/v1/orders/order-123/payment", "method": "POST" }
      }
  }
  ```
- **Skip HATEOAS when clients are tightly coupled** to the API (single SPA frontend,
  mobile apps with versioned clients). In these cases, HATEOAS adds payload size
  without practical benefit because clients already know the URL structure.
- **When using HATEOAS**: include only the actions that are valid for the current
  resource state. An order that is already shipped should not include a `cancel`
  link.

> **Reference**: [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html),
> [JSON:API Specification](https://jsonapi.org/)

## 9. GraphQL

- **When to use GraphQL**: GraphQL adds value when clients have significantly
  different data needs from the same backend (mobile vs web vs third-party), or
  when over-fetching and under-fetching are measurable problems. It adds complexity;
  do not use it by default.
- **Schema design**: Design the schema around client use cases, not database tables.
  Use domain-specific types and connections:
  ```graphql
  type Order {
      id: ID!
      status: OrderStatus!
      items: [OrderItem!]!
      customer: Customer!
      total: Money!
      createdAt: DateTime!
  }

  type Query {
      order(id: ID!): Order
      orders(filter: OrderFilter, first: Int, after: String): OrderConnection!
  }

  type Mutation {
      createOrder(input: CreateOrderInput!): CreateOrderPayload!
      cancelOrder(id: ID!): CancelOrderPayload!
  }
  ```
- **N+1 problem and DataLoader**: Every field resolver that hits a data source can
  cause N+1 queries when nested. Use the DataLoader pattern to batch and deduplicate
  requests within a single GraphQL execution:
  ```typescript
  const customerLoader = new DataLoader<string, Customer>(async (ids) => {
      const customers = await customerRepo.findByIds(ids);
      return ids.map(id => customers.find(c => c.id === id)!);
  });

  const resolvers = {
      Order: {
          customer: (order) => customerLoader.load(order.customerId),
      },
  };
  ```
- **Limit query complexity.** Deeply nested queries can cause exponential load.
  Implement query depth limiting, complexity analysis, or persisted queries to
  prevent abuse.
- **Use the `Relay` connection specification** for paginated fields. It provides
  `edges`, `nodes`, `pageInfo`, and cursor-based pagination that clients and tools
  understand.

> **Reference**: [GraphQL Specification](https://spec.graphql.org/),
> [DataLoader GitHub](https://github.com/graphql/dataloader),
> [Relay Cursor Connections](https://relay.dev/graphql/connections.htm)

## 10. Authentication and Authorization

- **Bearer tokens** (JWT or opaque tokens) for stateless API authentication.
  Include the token in the `Authorization` header:
  ```
  Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
  ```
- **API keys** for server-to-server or third-party integrations. API keys identify
  the client; they should not be the sole mechanism for user authentication. Pass
  them in a header, not in query parameters (query parameters appear in logs and
  browser history):
  ```
  X-API-Key: sk_live_abcdef123456
  ```
- **OAuth 2.0 flows**: Use the appropriate flow for the client type:
  - **Authorization Code + PKCE**: Web apps, mobile apps, SPAs
  - **Client Credentials**: Server-to-server (machine-to-machine)
  - **Device Authorization**: Smart TVs, CLI tools, IoT devices
  - **Never use** the Implicit flow or Resource Owner Password Credentials flow
    (both are deprecated in OAuth 2.1)
- **Token validation**: Validate JWT signatures on every request. Check `exp`
  (expiration), `iss` (issuer), `aud` (audience), and relevant custom claims.
  Use a well-maintained library; do not implement JWT parsing manually.
- **Scope-based authorization**: Use OAuth scopes or JWT claims to enforce
  fine-grained access control at the API level:
  ```
  scope: "orders:read orders:write payments:read"
  ```

> **Reference**: [RFC 6749 -- OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749),
> [RFC 7519 -- JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519),
> [OAuth 2.1 Draft](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)

## 11. API Documentation

- **Use OpenAPI 3.x** (Swagger) for REST API documentation. Generate it from code
  annotations or maintain it as a source-of-truth specification.
- **Every endpoint must document**: HTTP method, URL, request body schema, response
  schemas (success and error), authentication requirements, and example
  request/response pairs.
- **Keep documentation in sync with the API.** Use CI checks that validate the
  OpenAPI spec against the implementation (e.g., contract testing).
- **For GraphQL**: The schema is the documentation. Ensure every type, field, and
  argument has a description string in the schema definition.

> **Reference**: [OpenAPI Specification](https://spec.openapis.org/oas/latest.html),
> [Swagger Editor](https://editor.swagger.io/)
