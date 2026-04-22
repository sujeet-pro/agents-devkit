# MCP fallback: Google Drive

If the `google-drive` MCP server is configured, prefer it for creating and updating Google Docs from markdown.

## When the server is missing
Print: `Warning: google-drive MCP server not configured. Output the document locally as markdown and ask the user to upload it.`

The skill must still produce the final markdown.

## Install pointer
Follow https://github.com/piotr-agier/google-drive-mcp to obtain OAuth credentials and run the bootstrap once. Defaults to `~/.config/google-drive-mcp/`. Then `adk-install` and pick `google-drive`.
