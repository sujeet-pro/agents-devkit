# MCP fallback: GitHub

If the `github` MCP server is configured, prefer it for fetching PR diffs, listing issues, posting review comments, and creating PRs. It is faster and more reliable than the `gh` CLI for read-heavy work.

## When the server is missing
Fall back to the `gh` CLI:
- `gh pr view <n> --json ...`
- `gh pr diff <n>`
- `gh pr review <n> --body ...`

Print this warning once: `Warning: github MCP server not configured; using gh CLI.`

## Install pointer
Generate a Personal Access Token (classic, with `repo`, `read:org`, `gist` scopes) at https://github.com/settings/tokens. Run `adk-install` and pick `github` in the MCP step; it will prompt for `GITHUB_PAT` and persist it to `~/.zshenv`.
