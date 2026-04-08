# API Reference: [Service/API Name]

## Metadata

| Field | Value |
|-------|-------|
| Document Type | API Reference |
| API Version | [v1 / v2] |
| Base URL | [https://api.example.com/v1] |
| Authentication | [Bearer token / API key / OAuth2] |
| Rate Limits | [X requests/minute per client] |
| Owner | [team name] |
| Last Updated | YYYY-MM-DD |

## Overview

[One paragraph: what this API does, who uses it, and common use cases.]

## Authentication

### [Auth Method — e.g., Bearer Token]

[How to obtain credentials and include them in requests.]

```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/v1/resource
```

### Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 401 | UNAUTHORIZED | Missing or invalid authentication token |
| 403 | FORBIDDEN | Valid token but insufficient permissions |

## Common Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Authentication token |
| `Content-Type` | Yes (POST/PUT) | `application/json` |
| `Accept` | No | Response format (default: `application/json`) |
| `X-Request-Id` | No | Client-generated request ID for tracing |

## Common Error Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

## Endpoints

### [Resource Group — e.g., Users]

#### Create [Resource]

`POST /[resource]`

[Description of what this endpoint does.]

**Request Body**:

```json
{
  "field_name": "string (required) — description",
  "optional_field": "number (optional, default: 0) — description"
}
```

**Response 201**:

```json
{
  "id": "uuid",
  "field_name": "string",
  "created_at": "ISO 8601 timestamp"
}
```

**Errors**:

| Status | Code | Condition |
|--------|------|-----------|
| 400 | VALIDATION_ERROR | Invalid request body |
| 409 | CONFLICT | Resource already exists |

**Example**:

```bash
curl -X POST https://api.example.com/v1/[resource] \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"field_name": "value"}'
```

---

#### List [Resources]

`GET /[resource]`

[Description. Supports pagination and filtering.]

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number |
| `per_page` | integer | No | 20 | Items per page (max 100) |
| `sort` | string | No | `created_at` | Sort field |
| `order` | string | No | `desc` | Sort order: `asc` or `desc` |
| `filter` | string | No | -- | Filter expression |

**Response 200**:

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

#### Get [Resource]

`GET /[resource]/{id}`

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Resource identifier |

**Response 200**:

```json
{
  "id": "uuid",
  "field_name": "string",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Errors**:

| Status | Code | Condition |
|--------|------|-----------|
| 404 | NOT_FOUND | Resource does not exist |

---

#### Update [Resource]

`PUT /[resource]/{id}`

**Request Body**: Same as Create, all fields optional.

**Response 200**: Updated resource object.

**Errors**:

| Status | Code | Condition |
|--------|------|-----------|
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Concurrent modification (ETag mismatch) |

---

#### Delete [Resource]

`DELETE /[resource]/{id}`

**Response 204**: No content.

**Errors**:

| Status | Code | Condition |
|--------|------|-----------|
| 404 | NOT_FOUND | Resource does not exist |

## Pagination

[Describe pagination approach — offset-based, cursor-based, or keyset.]

## Rate Limiting

| Tier | Limit | Window | Headers |
|------|-------|--------|---------|
| Standard | [X] requests | per minute | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| Burst | [Y] requests | per second | Same headers |

When rate limited, the API returns `429 Too Many Requests` with a `Retry-After` header.

## Versioning

[API versioning strategy — URL path, header, or query parameter.]

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | YYYY-MM-DD | Initial release |
