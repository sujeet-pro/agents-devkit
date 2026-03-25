---
name: write-api-docs
description: Use when you need to draft or directly revise professional API reference documentation from codebase scanning or an existing OpenAPI spec
user_invocable: true
arguments:
  - name: source
    description: "Source for API discovery: 'codebase' to scan for endpoints, or a path to an OpenAPI/Swagger spec file"
    required: true
  - name: target
    description: "Existing API document to revise in place"
    required: false
  - name: format
    description: "Output format: markdown, openapi, confluence (default: markdown)"
    required: false
---

# API Documentation

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should improve the API docs directly. If you only want review findings on an existing API document, use `/devkit:review-doc`.

## Preflight

Before scanning for endpoints or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-api-docs`

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/coding/general.md`
- `skills/_references/guidelines/coding/backend-general.md`

## Required Child Agents

Run at least these child agents in parallel:

- Endpoint scanner: discovers all API endpoints by scanning route definitions, controller files, handler registrations, and decorator-based routing. For each endpoint, extracts HTTP method, path, path parameters, query parameters, headers, and middleware. When `source` is an OpenAPI spec, parses it directly instead of scanning code.
- Schema extractor: for each endpoint, traces request and response types through the codebase. Extracts TypeScript interfaces, Java DTOs, Go structs, Python Pydantic models, or equivalent type definitions. Identifies required vs. optional fields, validation rules, and default values.
- Example generator: produces realistic request and response examples for each endpoint. Generates cURL commands, request bodies, and response payloads based on the extracted schemas. Includes examples for success cases and common error responses.
- Writer: assembles the final documentation with consistent formatting, cross-references between related endpoints, and navigation structure.

## Workflow

1. Discover endpoints from `source`.
2. Extract request and response schemas.
3. Generate accurate examples.
4. Organize the documentation so it is professional, navigable, and consistent.
5. If `target` is provided, revise that document directly instead of creating a detached replacement.

Save intermediary artifacts to `.temp/write-api-docs/`.
