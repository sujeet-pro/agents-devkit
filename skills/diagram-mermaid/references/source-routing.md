# DevKit Source Routing

Use the source-native MCP first when it exists.

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}` before source-side work so the correct MCP is validated from the real input, not from a hard-coded global list.

## Preferred MCPs

- **GitHub**: `mcp__github__*`
- **Bitbucket**: `mcp__bitbucket__*`
- **Confluence**: `mcp__atlassian-confluence__confluence_*`
- **Google Docs / Drive / Sheets / Slides**: `mcp__google-drive__*`

## Input Detection

- GitHub PR URL or repo with PR identifier: use GitHub MCP.
- Bitbucket PR URL or repo with PR identifier: use Bitbucket MCP.
- `atlassian.net/wiki` URL: use Confluence MCP.
- Google Docs/Drive URL: use Google Drive MCP.
- Local markdown or docs path: read locally and optionally publish later.
- Local repo path: treat as codebase review or documentation generation.

## Output Actions

- **Markdown**: always supported and always produced first.
- **GitHub PR comments**: post via GitHub MCP review or comment tools.
- **Bitbucket PR comments**: post via Bitbucket MCP PR comment tools.
- **Confluence**: add comments, update pages, and upload rendered diagrams and source attachments.
- **Google Docs**: add comments or write the generated document through Google Drive MCP.
- **PDF**: export locally with a free tool already on the machine such as browser print-to-PDF, `pandoc`, or `wkhtmltopdf` when available.

## Existing Interaction Rule

When the source already has review comments or a discussion thread:

- read it first
- do not duplicate resolved or clearly addressed feedback
- verify handled comments before resolving or skipping them
- resolve handled-but-open comments when the source supports it
- if a critical issue was marked outdated but is still present, reopen the thread or restate the issue with fresh evidence
- keep new comments aligned with the source's tone and threading model

## Free-Only Rule

- Prefer open-source CLIs and MCP servers.
- Do not require paid SaaS reviewers or proprietary review backends.
- If a destination requires credentials, use the user's existing account through the relevant MCP instead of adding a third-party service.
