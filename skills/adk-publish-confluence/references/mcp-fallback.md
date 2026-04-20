# MCP fallback: Confluence

If the `confluence` MCP server is configured, prefer it for reading and writing Confluence pages. Direct REST is awkward; the MCP wrapper handles attachments and rich text.

## When the server is missing
Print: `Warning: confluence MCP server not configured. Output the page locally as markdown and ask the user to paste it.`

The skill must still produce the final markdown the user can publish manually.

## Install pointer
Use the same Atlassian API token as Jira (https://id.atlassian.com/manage-profile/security/api-tokens). Run `adk-install` and pick `confluence`; it will prompt for `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` and persist them to `~/.zshenv`.
