# MCP fallback: Bitbucket

If the `bitbucket` MCP server is configured, prefer it for PR diffs, comments, and reviews. Bitbucket Cloud's REST API is verbose; the MCP server makes it manageable.

## When the server is missing
Fall back to direct `curl` calls against the Bitbucket REST API with the user's app password.

Print this warning once: `Warning: bitbucket MCP server not configured; using direct REST calls.`

## Install pointer
Create an app password at https://bitbucket.org/account/settings/app-passwords/ with `repository:read` and `pullrequest:read` (and `:write` for posting). Run `adk-install` and pick `bitbucket`; it will prompt for `BITBUCKET_USERNAME` and `BITBUCKET_APP_PASSWORD` and persist them to `~/.zshenv`.
