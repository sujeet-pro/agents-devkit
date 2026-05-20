---
title: 'adk-mcp-rag'
description: 'Optional company RAG MCP. Only loads if RAG_MCP_URL is set. Generic stub — swap the URL + auth header for your company''s RAG endpoint. Skills query it during Phase 0 (context-gather) when overrides.yaml.rag.enabled...'
mcp: 'adk-mcp-rag'
source: 'mcp/adk-mcp-rag.json'
group: 'mcp'
order: 3007
---
# adk-mcp-rag

Optional company RAG MCP. Only loads if RAG_MCP_URL is set. Generic stub — swap the URL + auth header for your company's RAG endpoint. Skills query it during Phase 0 (context-gather) when overrides.yaml.rag.enabled is true AND the prompt matches rag.trigger_keywords or the user explicitly says 'check our internal docs'. Results merged into context.md with `[source: rag]` tag. See SETUP.md.

## Source

`mcp/adk-mcp-rag.json`

## Environment variables referenced

- `RAG_MCP_TOKEN`
- `RAG_MCP_URL`

## Configuration

```json
{
  "name": "adk-mcp-rag",
  "type": "http",
  "url": "${RAG_MCP_URL}",
  "headers": {
    "Authorization": "Bearer ${RAG_MCP_TOKEN}"
  },
  "description": "Optional company RAG MCP. Only loads if RAG_MCP_URL is set. Generic stub — swap the URL + auth header for your company's RAG endpoint. Skills query it during Phase 0 (context-gather) when overrides.yaml.rag.enabled is true AND the prompt matches rag.trigger_keywords or the user explicitly says 'check our internal docs'. Results merged into context.md with `[source: rag]` tag. See SETUP.md."
}
```
