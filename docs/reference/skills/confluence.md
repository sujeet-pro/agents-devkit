---
title: "confluence"
description: Confluence REST API operations — page CRUD, comments, attachments, spaces
skill_name: confluence
category: connector
workflow_tier: helper
user_invocable: false
---

# confluence

Connector skill for Confluence Cloud operations. Uses REST API via `curl`/scripts, with MCP for common page operations.

## Purpose

Provides Confluence page CRUD, comment management, attachment handling, and space operations to documentation skills.

## Operations

| Operation | Method |
|-----------|--------|
| Read page content | MCP (preferred) or REST API |
| Create page | MCP or REST API |
| Update page | MCP or REST API |
| Delete page | REST API (direct) |
| Manage comments | REST API |
| Upload attachments | REST API |
| Space operations | REST API |

## Dependencies

- `curl` (required)
- `CONFLUENCE_TOKEN` + `CONFLUENCE_URL` environment variables
- Confluence MCP (optional, preferred for page CRUD)

## Invoked By

`docs-confluence`, `docs-review`, `docs-crud`, `docs-write` (when publishing to Confluence).
