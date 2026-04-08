---
title: "preflight-check"
description: "Preflight validation for dependencies, MCP servers, and tool readiness"
skill_name: preflight-check
category: guideline
workflow_tier: helper
user_invocable: false
---

# preflight-check

Preflight validation skill that checks dependencies, MCP server configuration, and tool readiness before skills launch child agents, start reviews, or publish to external sources. Prevents failures by catching missing tools and misconfigured integrations early.

## Purpose

- Validate that required CLI tools, MCP servers, and dependencies are available before work begins
- Route to the correct source-native MCP based on input URL or destination
- Stop with actionable install/setup instructions when a dependency is missing
- Ensure diagram rendering tools are ready before generation starts

## Key Behaviors

### Preflight Script

Skills run `python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}` before the main workflow, passing real input parameters so the check can infer the right dependency:

| Parameter | Purpose |
|-----------|---------|
| `pr=<url-or-number>` | Detect PR source (GitHub or Bitbucket) |
| `source=<url-or-path>` | Detect source type |
| `target=<url-or-path>` | Detect target type |
| `format=<svg\|png\|jpeg\|webp\|markdown\|google-doc\|confluence\|pdf>` | Detect output format dependencies |
| `publish=<markdown\|source\|both>` | Detect publishing destination |
| `provider=<github\|bitbucket\|confluence\|google-drive>` | Explicit provider specification |

### Missing Dependency Handling

When a required dependency is missing:

1. Stop before analysis — do not proceed with degraded functionality
2. Show the exact install or setup command
3. Give the user two paths: run the command manually, or (if the host supports command approval) explicitly ask for approval and run it for them

### MCP Source Routing

The preflight validates MCP configuration and routes to the correct source-native MCP:

| Input | MCP |
|-------|-----|
| GitHub PR or repo URL | GitHub MCP (`mcp__github__*`) |
| Bitbucket PR or repo URL | Bitbucket MCP (`mcp__bitbucket__*`) |
| `atlassian.net/wiki` or Confluence publishing | Atlassian Confluence MCP (`mcp__atlassian-confluence__confluence_*`) |
| Google Docs or Drive URL, or `format=google-doc` | Google Drive MCP (`mcp__google-drive__*`) |
| Local markdown or docs path | Read locally, optionally publish later |
| Local repo path | Treat as codebase review or documentation generation |

If the required MCP is missing, stop and inform the user which MCP server needs to be configured instead of falling back to the wrong source.

### Diagram Preflight

For `diagramkit` and engine-specific diagram skills:

1. Validate global npm install: `npm install -g diagramkit`
2. Validate Playwright Chromium readiness: `diagramkit warmup`
3. If raster output requested (`png`, `jpeg`, `jpg`, `webp`), validate `sharp`: `npm install -g sharp`
4. Do not start generation or rendering until these checks pass

### Output Actions

| Destination | Action |
|-------------|--------|
| Markdown | Always supported, always produced first |
| GitHub PR comments | Post via GitHub MCP review or comment tools |
| Bitbucket PR comments | Post via Bitbucket MCP PR comment tools |
| Confluence | Add comments, update pages, upload attachments |
| Google Docs | Add comments or write through Google Drive MCP |

### Free-Only Rule

- Prefer open-source CLIs and MCP servers
- Do not require paid SaaS reviewers or proprietary review backends
- If a destination requires credentials, use the user's existing account through the relevant MCP

## What It Provides

- Pre-work validation that catches missing tools and misconfigured MCPs before wasted effort
- Source routing logic that maps input URLs to the correct MCP
- Diagram dependency validation chain
- Actionable install commands when dependencies are missing
- Two-path resolution: manual install or agent-assisted install with user approval

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | before work (validates source MCP and CLI tools) |
| `code-review-repo` | before work |
| `code-review-fix` | before work |
| `audit` | before work |
| `docs-write` | before work (validates publishing destination MCP) |
| `docs-review` | before work |
| `docs-repo` | before work |
| `docs-crud` | before work |
| `docs-confluence` | before work (validates Confluence MCP) |
| `diagram-mermaid` | before work (validates diagramkit) |
| `diagram-excalidraw` | before work (validates diagramkit) |
| `diagram-drawio` | before work (validates diagramkit) |
| `diagram-graphviz` | before work (validates diagramkit) |
| `design` | before work |
| `dev-build` | before work |
| `workflow` (always loaded) | before main workflow |
