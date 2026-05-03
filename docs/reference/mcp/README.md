---
title: 'MCP Servers'
description: 'Generated reference pages for shipped plugin-local MCP servers.'
---
# MCP Servers

Generated reference pages for shipped plugin-local MCP servers.

## adk-review

- [`github`](adk-review-github.md) - GitHub MCP via Docker (ghcr.io/github/github-mcp-server pinned to v1.0.3). Requires GITHUB_PAT (fine-grained PAT, repo+pull-request+actions+read:org). Read-only by default; flip GITHUB_READ_ONLY=0 only for approved...

## adk-investigate

- [`datadog`](adk-investigate-datadog.md) - Datadog hosted MCP (Preview). Auth via DD_API_KEY + DD_APP_KEY (App key needs scope `mcp_read`; add `mcp_write` only if you actually need to mute/silence monitors). Override DD_MCP_URL for non-US1 sites:...
- [`statsig`](adk-investigate-statsig.md) - Statsig hosted MCP. Header auth via STATSIG_CONSOLE_API_KEY (https://console.statsig.com/api_keys → type=Console → scope=omni_read_only). For browser-based OAuth, omit headers. Use omni_write only for skills that...
