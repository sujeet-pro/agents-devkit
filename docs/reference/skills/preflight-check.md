---
title: "preflight-check"
description: Tool dependency and MCP readiness validation before work begins
skill_name: preflight-check
category: guideline
workflow_tier: helper
user_invocable: false
---

# preflight-check

Validates tool dependencies, MCP server availability, and diagram rendering readiness before work begins. Fails fast with install instructions instead of partial runs.

## Purpose

Runs `preflight.py` to check CLI tools, MCP configurations, diagram tooling, and source routing. Ensures the environment is ready before launching child agents, reviews, or publishing.

## Checks Performed

| Category | What It Checks |
|----------|----------------|
| **CLI tools** | git, python3, node, npm, jq, curl, gh, graphviz, uv |
| **Diagram tools** | diagramkit, Playwright (for rendering), sharp (for raster) |
| **MCP servers** | GitHub, Bitbucket, Confluence, Google Drive |
| **Source routing** | Detects PR source type and routes to correct MCP/connector |

## Script Parameters

| Parameter | Description |
|-----------|-------------|
| `pr=<url>` | PR URL for source detection |
| `source=<type>` | Source type override |
| `target=<type>` | Target platform |
| `format=<type>` | Output format |
| `publish=<bool>` | Whether publishing is needed |
| `provider=<name>` | Provider override |

## Invoked By

Loaded by the workflow helper set ("Always" tier). Any skill that needs tools, MCP, child agents, reviews, or publishing.
