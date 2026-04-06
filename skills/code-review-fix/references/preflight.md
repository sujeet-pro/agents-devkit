# DevKit Preflight Validations

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
- the preflight script (`scripts/preflight.py`) validates MCP configuration from `~/.claude.json` or `.mcp.json`
- then do a lightweight source-native read with the matching MCP before launching the full team

Source mapping:

- GitHub PR or repo URL -> GitHub MCP
- Bitbucket PR or repo URL -> Bitbucket MCP
- `atlassian.net/wiki` or Confluence publishing -> Atlassian Confluence MCP
- Google Docs or Drive URL, or `format=google-doc` -> Google Drive MCP

If the required MCP is missing, stop and inform the user which MCP server needs to be configured instead of falling back to the wrong source.
