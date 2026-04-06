# Stage: API Documentation

Use this stage when the agent should create or revise API reference documentation from codebase scanning or an existing OpenAPI spec.

## Type-Specific Phase Guidance

### Exploration
- Scan the codebase for route definitions, controllers, handlers, and OpenAPI/Swagger specs
- Identify all endpoints, request/response schemas, authentication mechanisms, and error codes
- Check for existing API documentation and its completeness

### Execute
- Write comprehensive API reference following the document structure below
- Ground all examples in real code from the repository
- Validate that documented endpoints match the actual codebase

## Document Structure

### Overview
- API name, version, and base URL
- Authentication requirements
- Rate limiting and quotas
- Common headers and conventions

### Endpoints
For each endpoint:
- HTTP method and path
- Description of what it does
- Request parameters (path, query, header, body) with types and constraints
- Request body schema with example
- Response schema with example for each status code
- Error responses with error codes and descriptions
- Authentication requirements specific to this endpoint
- Example request/response pair (curl or language-specific)

### Authentication
- Supported auth methods (API key, OAuth2, JWT, etc.)
- How to obtain credentials
- Token lifecycle and refresh flow

### Error Handling
- Standard error response format
- Error code catalog with descriptions and resolution steps
- Rate limit error handling

### Pagination
- Pagination strategy (cursor, offset, keyset)
- Pagination parameters and response metadata

### Versioning
- API versioning strategy
- Deprecation policy
- Migration paths between versions

### SDKs and Client Libraries
- Available SDKs with installation instructions
- Quick-start code examples per language

## Child Agent Team

- `endpoint-scanner` for discovering and cataloging all API endpoints from code
- `schema-extractor` for extracting request/response schemas
- `example-generator` for creating realistic request/response examples
- `doc-reviewer` for completeness and accuracy checking

## Type-Specific Output Format

Markdown reference documentation. If an OpenAPI spec exists, also update or generate the OpenAPI YAML/JSON.

## Validation Checklist

- Every endpoint in the codebase is documented
- All request/response schemas match actual code
- Examples are runnable and produce the documented responses
- Authentication flow is complete and accurate
- Error codes are exhaustive
