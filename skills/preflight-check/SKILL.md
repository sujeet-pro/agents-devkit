---
name: preflight-check
description: "adk - [helper] [guideline] Preflight validation for dependencies, MCP servers, and tool readiness. Run before launching child agents, reviews, or publishing."
user-invocable: false
allowed-tools: [Read, Bash]
dependencies:
  commands: [python3]
workflow-tier: helper
maturity: stable
---

# Preflight Validations

Run preflight checks before launching child agents, starting reviews, or publishing back to a source.

## Shared Rule

- Run `python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}` before the main workflow.
- Pass the real input so the check can infer the right dependency or MCP:
  - `pr=<url-or-number>`
  - `source=<url-or-path>`
  - `target=<url-or-path>`
  - `format=<svg|png|jpeg|webp|markdown|google-doc|confluence|pdf>`
  - `publish=<markdown|source|both>`
  - `provider=<github|bitbucket|confluence|google-drive>`
- If a required dependency is missing, stop before analysis and show the exact install or setup command.
- Give the user two paths:
  - run the command manually
  - or, if the current host supports command approval, explicitly ask for approval and run it for them

## Diagram Preflight

For `diagramkit` and the engine-specific diagram skills (`diagram-mermaid`, `diagram-excalidraw`, `diagram-drawio`, `diagram-graphviz`):

- validate the global npm install: `npm install -g diagramkit`
- validate Playwright Chromium readiness: `diagramkit warmup`
- if the requested output is raster (`png`, `jpeg`, `jpg`, `webp`), also validate `sharp`: `npm install -g sharp`
- do not start generation or rendering until these checks pass

## MCP Preflight

For MCP-backed skills:

- use the input URL or requested destination to choose the right MCP before analysis
- the preflight script (`scripts/preflight.py`) validates MCP configuration from `~/.claude.json` or `mcp-config.json`
- then do a lightweight source-native read with the matching MCP before launching the full team

Source mapping:

- GitHub PR or repo URL -> GitHub MCP
- Bitbucket PR or repo URL -> Bitbucket MCP
- `atlassian.net/wiki` or Confluence publishing -> Atlassian Confluence MCP
- Google Docs or Drive URL, or `format=google-doc` -> Google Drive MCP

If the required MCP is missing, stop and inform the user which MCP server needs to be configured instead of falling back to the wrong source.

## Source Routing

Use the source-native MCP first when it exists.

### Preferred MCPs

- **GitHub**: `mcp__github__*`, `mcp__plugin-adk-github__*`
- **Bitbucket**: `mcp__bitbucket__*`, `mcp__plugin-adk-atlassian__*`, `mcp__plugin-atlassian-atlassian__*`
- **Confluence**: `mcp__atlassian-confluence__confluence_*`, `mcp__plugin-adk-atlassian__confluence_*`, `mcp__plugin-atlassian-atlassian__confluence_*`
- **Google Docs / Drive / Sheets / Slides**: `mcp__google-drive__*`

### Input Detection

- GitHub PR URL or repo with PR identifier: use GitHub MCP.
- Bitbucket PR URL or repo with PR identifier: use Bitbucket MCP.
- `atlassian.net/wiki` URL: use Confluence MCP.
- Google Docs/Drive URL: use Google Drive MCP.
- Local markdown or docs path: read locally and optionally publish later.
- Local repo path: treat as codebase review or documentation generation.

### Output Actions

- **Markdown**: always supported and always produced first.
- **GitHub PR comments**: post via GitHub MCP review or comment tools.
- **Bitbucket PR comments**: post via Bitbucket MCP PR comment tools.
- **Confluence**: add comments, update pages, and upload rendered diagrams and source attachments.
- **Google Docs**: add comments or write the generated document through Google Drive MCP.

### Free-Only Rule

- Prefer open-source CLIs and MCP servers.
- Do not require paid SaaS reviewers or proprietary review backends.
- If a destination requires credentials, use the user's existing account through the relevant MCP instead of adding a third-party service.
