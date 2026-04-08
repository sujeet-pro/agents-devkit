# API Reference Documentation Guidelines

Guidelines for writing and reviewing API reference documentation. An API reference is the contract between your service and its consumers. It must be precise, complete, and structured so that a developer can integrate without reading source code or asking questions.

**Audience**: Backend and frontend engineers, third-party integrators, and developer relations teams who need to understand every endpoint, parameter, error, and constraint of the API.

**Reference**: Aligned with [OpenAPI Specification 3.1](https://spec.openapis.org/oas/v3.1.0) and [JSON:API Specification 1.1](https://jsonapi.org/format/).

---

## 1. Required Sections

Every API reference must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Overview | What the API does, who it is for, and how to get started |
| 2 | Authentication | How to authenticate, token formats, scopes |
| 3 | Base URL & Environments | Production, staging, sandbox URLs and versioning |
| 4 | Common Conventions | Shared patterns: pagination, filtering, sorting, rate limiting |
| 5 | Endpoints | Complete reference for every endpoint |
| 6 | Error Handling | Error object format and exhaustive error code catalog |
| 7 | Rate Limits | Limits, headers, and backoff strategy |
| 8 | Webhooks | Webhook events, payloads, verification (if applicable) |
| 9 | SDKs & Client Libraries | Official and community SDK references |
| 10 | Changelog | Version history of API changes |

---

## 2. Content Standards

### Overview

- State what the API does in one paragraph. Be specific about the domain.
  - **Weak**: "The API lets you manage resources."
  - **Strong**: "The Payments API lets you create charges, manage subscriptions, issue refunds, and handle disputes for credit card and ACH payments. It supports idempotent requests, webhook-driven event notifications, and PCI-compliant tokenized card storage."
- Include a quick-start example that demonstrates the most common operation (e.g., "Create a payment" for a payments API). The example should go from zero to a successful API call in under 10 lines:

```bash
curl -X POST https://api.example.com/v1/charges \
  -H "Authorization: Bearer sk_test_abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "source": "tok_visa",
    "description": "Order #1234"
  }'
```

- Link to the authentication section, SDKs, and changelog.

### Authentication

- Document every supported authentication method:

| Method | Use Case | Token Lifetime | Refresh Mechanism |
|--------|----------|----------------|-------------------|
| API Key (Bearer token) | Server-to-server | No expiry (revokable) | Generate new key in dashboard |
| OAuth 2.0 (Authorization Code) | User-delegated access | 1 hour | Refresh token (30 days) |
| OAuth 2.0 (Client Credentials) | Machine-to-machine | 1 hour | Re-request with client_id/secret |

- For each method, provide:
  - How to obtain credentials.
  - How to include them in requests (header format, query parameter, etc.).
  - Scopes/permissions and what each scope grants.
  - What happens when a token expires or is revoked (HTTP status, error code).
- Include a complete authentication example for each method.
- State which environments accept which credentials (test keys for sandbox, live keys for production).
- Show what happens when authentication fails. Include the exact error response:
  ```json
  {
      "error": {
          "type": "authentication_error",
          "code": "invalid_api_key",
          "message": "The API key provided is invalid or has been revoked.",
          "doc_url": "https://docs.example.com/errors#invalid_api_key"
      }
  }
  ```
- Distinguish between test/sandbox credentials and production credentials. Make it obvious which environment a key belongs to (e.g., `sk_test_` vs `sk_live_` prefixes, following the Stripe convention).

### Base URL & Environments

- List all environments with their base URLs:

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| Production | `https://api.example.com/v1` | Live data, real charges |
| Sandbox | `https://sandbox.api.example.com/v1` | Test data, no real charges |
| Staging | `https://staging.api.example.com/v1` | Pre-release testing (internal) |

- Document the versioning strategy:
  - URL-based (`/v1/`, `/v2/`) or header-based (`Accept: application/vnd.example.v1+json`).
  - Deprecation policy: how much notice before a version is sunset.
  - Which version each endpoint belongs to.
- State content type requirements: `Content-Type: application/json` for requests, `Accept` header behavior.
- Specify whether sandbox and production use the same credentials or separate ones.
- Document any behavioral differences between environments (e.g., sandbox always returns success for payments, rate limits are relaxed in sandbox).

### Common Conventions

Document patterns that apply across all endpoints:

**Pagination**:
- Describe the pagination mechanism (cursor-based, offset-based, keyset).
- Show the request parameters and response structure:

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```

- State the default and maximum page size.
- Explain how to detect the last page (e.g., `has_more: false` or empty `next_cursor`).
- Cite: cursor-based pagination is preferred for large datasets per [Slack API pagination](https://api.slack.com/docs/pagination) and [Stripe's pagination design](https://stripe.com/docs/api/pagination).

**Filtering & Sorting**:
- Document the query parameter syntax for filtering: `?status=active&created_after=2024-01-01`.
- Document sorting: `?sort=created_at&order=desc`.
- State which fields are filterable and sortable per endpoint.

**Idempotency**:
- If supported, document the idempotency key header: `Idempotency-Key: <unique-key>`.
- State the idempotency window (e.g., "keys are stored for 24 hours").
- Explain behavior on duplicate requests: same response returned, no side effects.
- Document what happens when the same key is used with a different request body.

**Rate Limiting** (summary; detailed in Section 7):
- State global and per-endpoint limits.
- Document rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

### Endpoints

Every endpoint must include the following fields, structured consistently:

```markdown
#### Create a Charge

`POST /v1/charges`

Creates a new charge for a payment method.

**Authentication**: Bearer token with `charges:write` scope.

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | integer | Yes | Amount in smallest currency unit (cents for USD) |
| `currency` | string | Yes | Three-letter ISO 4217 currency code |
| `source` | string | Yes | Payment source token |
| `description` | string | No | Arbitrary string for your records (max 500 chars) |
| `metadata` | object | No | Key-value pairs for custom data (max 50 keys) |
| `idempotency_key` | string | No | Unique key for idempotent requests |

**Request Body Example**:

​```json
{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa",
  "description": "Order #1234",
  "metadata": {
    "order_id": "1234"
  }
}
​```

**Response** (`201 Created`):

​```json
{
  "id": "ch_1abc234def",
  "object": "charge",
  "amount": 2000,
  "currency": "usd",
  "status": "succeeded",
  "source": "tok_visa",
  "description": "Order #1234",
  "metadata": {
    "order_id": "1234"
  },
  "created_at": "2024-09-15T14:30:00Z"
}
​```

**Error Responses**:

| Status | Error Code | Description |
|--------|------------|-------------|
| 400 | `invalid_amount` | Amount must be a positive integer |
| 401 | `authentication_required` | Missing or invalid Bearer token |
| 402 | `card_declined` | The card was declined by the issuer |
| 422 | `invalid_currency` | Currency code not supported |
| 429 | `rate_limit_exceeded` | Too many requests |
```

- Request and response examples must be complete and copy-pasteable. No truncated JSON with `...`.
- Include all HTTP status codes the endpoint can return, not just 200.
- Document every field in the response object, including nested objects.
- State constraints: max lengths, allowed values, format requirements (ISO 8601 dates, UUID format, etc.).
- Document which fields are always present vs conditionally present. Use "nullable" and "optional" explicitly.
- Include curl examples for common use cases, not just the minimal happy path.

### Error Handling

- Define a consistent error response object used across all endpoints:

```json
{
  "error": {
    "type": "invalid_request_error",
    "code": "invalid_amount",
    "message": "Amount must be a positive integer greater than zero.",
    "param": "amount",
    "doc_url": "https://docs.example.com/errors#invalid_amount"
  }
}
```

- Document every error type and code in a master table:

| Type | Code | HTTP Status | Description | Resolution |
|------|------|-------------|-------------|------------|
| `invalid_request_error` | `invalid_amount` | 400 | Amount is missing, negative, or not an integer | Check the `amount` field value |
| `invalid_request_error` | `missing_required_field` | 400 | A required field is missing from the request body | Check the `param` field for which field is missing |
| `authentication_error` | `invalid_api_key` | 401 | API key is malformed or revoked | Generate a new API key in the dashboard |
| `authorization_error` | `insufficient_permissions` | 403 | Token lacks required scopes | Request the appropriate scope during OAuth flow |
| `not_found_error` | `resource_not_found` | 404 | The requested resource does not exist | Verify the resource ID; it may have been deleted |
| `rate_limit_error` | `rate_limit_exceeded` | 429 | Request rate exceeds plan limits | Implement exponential backoff; consider upgrading plan |
| `api_error` | `internal_error` | 500 | An unexpected error occurred on the server | Retry with exponential backoff; contact support if persistent |

- For each error, include a resolution hint -- what the developer should do to fix it.
- Document validation error sub-structure (per-field error details):
  ```json
  {
      "error": {
          "type": "invalid_request_error",
          "code": "validation_error",
          "message": "Request body failed validation.",
          "errors": [
              { "field": "email", "message": "Must be a valid email address" },
              { "field": "items", "message": "Must contain at least one item" }
          ]
      }
  }
  ```
- Reference the [RFC 9457 Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457) standard for structured error responses.

### Rate Limits

- Document limits per authentication level and per endpoint:

| Plan | Rate Limit | Burst Limit |
|------|-----------|-------------|
| Free | 100 requests/minute | 20 requests/second |
| Pro | 1,000 requests/minute | 100 requests/second |
| Enterprise | 10,000 requests/minute | 1,000 requests/second |

- Document the rate limit response headers:
  - `X-RateLimit-Limit`: Maximum requests per window.
  - `X-RateLimit-Remaining`: Remaining requests in current window.
  - `X-RateLimit-Reset`: Unix timestamp when the window resets.
- Document the 429 response body and recommended backoff strategy:
  - Exponential backoff with jitter.
  - Respect the `Retry-After` header if present.
- Specify whether rate limits are per API key, per IP, per user, or per endpoint.
- Reference [IETF RFC 6585 Section 4](https://www.rfc-editor.org/rfc/rfc6585#section-4) for the 429 status code specification and [IETF RateLimit Header Fields](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/) for the header convention.

### Webhooks (if applicable)

- List all webhook event types with payload examples.
- Document the webhook signature verification mechanism (HMAC-SHA256, etc.) with code examples in at least two languages.
- State the retry policy: how many retries, backoff interval, timeout threshold.
- Document the expected response from the consumer (e.g., 2xx within 5 seconds).
- Explain how to register and manage webhook endpoints.

### SDKs & Client Libraries

- List official SDKs with installation instructions and quick-start examples:

| Language | Package | Install | Docs |
|----------|---------|---------|------|
| Python | `example-sdk` | `pip install example-sdk` | [docs link] |
| Node.js | `@example/sdk` | `npm install @example/sdk` | [docs link] |
| Go | `github.com/example/sdk-go` | `go get github.com/example/sdk-go` | [docs link] |
| Java | `com.example:sdk` | Maven/Gradle coordinates | [docs link] |

- Include a language-specific example alongside every curl example for the most common endpoints.
- List community-maintained SDKs separately with a disclaimer about support level.

### Changelog

- Follow the Keep a Changelog format (see [changelog.md guidelines](changelog.md) for detailed formatting rules).
- Document breaking changes prominently with migration instructions.
- Include dates in ISO 8601 format and link to comparison diffs.

---

## 3. OpenAPI Alignment

- Structure your API reference to align with [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0) even if you do not generate it from an OpenAPI spec.
- This means: consistent operation IDs, parameter locations (`path`, `query`, `header`, `cookie`), request/response media types, and schema definitions.
- If you maintain an OpenAPI spec file, ensure the human-readable reference and the spec file are in sync. Discrepancies between the two erode trust.
- Consider generating the reference from the OpenAPI spec to ensure consistency. Tools: [Redoc](https://github.com/Redocly/redoc), [Swagger UI](https://swagger.io/tools/swagger-ui/), [Stoplight](https://stoplight.io/).
- Use `$ref` for reusable schemas. Define common objects (error responses, pagination, standard headers) once and reference them across endpoints.
- Include `examples` in the OpenAPI spec. The spec supports inline examples that can be used to generate documentation and power API explorers.
- Validate the OpenAPI spec in CI. Use `spectral` or `openapi-generator validate` to catch schema errors, missing descriptions, and style violations.

> **Reference**: [OpenAPI Specification 3.1](https://spec.openapis.org/oas/v3.1.0),
> [JSON:API Specification](https://jsonapi.org/),
> [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457),
> [Spectral API Linter](https://stoplight.io/open-source/spectral)

---

## 4. Common Issues

- **Incomplete error documentation**: Only documenting the happy path (200 OK). Every possible error status and code must be documented.
- **Truncated examples**: Response examples with `...` or `// more fields`. Show the complete object.
- **Missing authentication context**: Not stating which authentication method and scope each endpoint requires.
- **Stale examples**: Code examples that use deprecated parameters or return outdated response shapes. Test examples against the live API.
- **No SDK examples**: Curl-only documentation forces every developer to translate to their language. Include at least one SDK example per endpoint.
- **Inconsistent error format**: Different endpoints returning different error structures. Use a single error object format across the entire API.
- **Undocumented rate limits**: Developers discover rate limits by hitting them. Document limits upfront.
- **Missing pagination details**: Not stating the default page size, maximum page size, or how to detect the last page.
- **No resolution guidance for errors**: Error codes without "how to fix it" guidance generate support tickets.
- **Inconsistent naming**: `customer_id` in one endpoint, `customerId` in another, `CustomerID` in a third. Pick a convention (snake_case is most common for JSON APIs) and enforce it.
- **No sandbox environment**: Developers cannot test integrations without affecting production data.

---

## 5. Review Checklist

- [ ] Overview includes a quick-start example that works out of the box
- [ ] Every authentication method is documented with examples and scope descriptions
- [ ] Authentication failure response is shown
- [ ] All environments and base URLs are listed
- [ ] Versioning strategy and deprecation policy are documented
- [ ] Common conventions (pagination, filtering, sorting, idempotency) are documented
- [ ] Every endpoint includes: method, path, description, auth requirements, parameters, request body, response body, and error responses
- [ ] Request and response examples are complete and copy-pasteable
- [ ] All response fields are documented, including nested objects
- [ ] Nullable and optional fields are explicitly marked
- [ ] Error response format is consistent across all endpoints
- [ ] Every possible error code is documented with resolution hints
- [ ] Validation errors include per-field detail structure
- [ ] Rate limits are documented per plan and per endpoint with response headers
- [ ] Webhooks include event types, payload examples, signature verification, and retry policy
- [ ] At least one SDK language example per major endpoint
- [ ] API reference aligns with OpenAPI 3.1 structure
- [ ] OpenAPI spec is validated in CI
- [ ] Field naming convention is consistent across all endpoints
- [ ] No TODO/TBD placeholders remain
- [ ] Examples have been tested against the live or sandbox API
