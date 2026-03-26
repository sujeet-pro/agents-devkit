---
name: manage-validate
description: Validate the MCP servers used by DevKit's code and document workflows, with emphasis on GitHub, Bitbucket, Confluence, and Google Drive
user_invocable: true
arguments:
  - name: server
    description: "Specific server to validate: github, bitbucket, confluence, google-drive, all (default: all)"
    required: false
---

# Validate MCP

Use `skills/_references/preflight-validations.md` and `skills/_references/source-routing.md`.

## Preflight

Run config validation first:

`zsh scripts/check-skill-deps.zsh manage-validate server=<server>`

## Workflow

### Stage 1: Configuration Check

For each requested server, verify the MCP configuration exists in the settings:

- **GitHub**: `mcp__github__*` tools are available
- **Bitbucket**: `mcp__bitbucket__*` tools are available
- **Confluence**: `mcp__atlassian-confluence__*` tools are available
- **Google Drive**: `mcp__google-drive__*` tools are available

### Stage 2: Connectivity Test

Run lightweight live reads in parallel for each configured server:

- **GitHub**: `mcp__github__get_me` to verify authentication
- **Bitbucket**: `mcp__bitbucket__listRepositories` with limit 1
- **Confluence**: `mcp__atlassian-confluence__confluence_search` with a simple query
- **Google Drive**: `mcp__google-drive__authGetStatus` to verify OAuth

### Stage 3: Dependency Mapping

For each validated server, list the DevKit skills that depend on it:

- GitHub: `review-code-pr`, `pr-describe`, `pr-finalize`, `pr-fix-comments`
- Bitbucket: `review-code-pr`, `pr-describe`, `pr-finalize`, `pr-fix-comments`
- Confluence: `publish-confluence`, `review-doc`, `review-doc-interactive`, `doc-fix`
- Google Drive: `review-doc`, `review-doc-interactive`, `doc-fix`, `write-doc`

## Output

```
## MCP Validation Results

| Server       | Config | Auth   | Status  | Dependent Skills |
|-------------|--------|--------|---------|-----------------|
| GitHub       | <ok/missing> | <ok/failed> | <ready/blocked> | <list> |
| Bitbucket    | <ok/missing> | <ok/failed> | <ready/blocked> | <list> |
| Confluence   | <ok/missing> | <ok/failed> | <ready/blocked> | <list> |
| Google Drive | <ok/missing> | <ok/failed> | <ready/blocked> | <list> |

### Issues
- <server>: <specific auth or config issue and resolution steps>
```

Prefer the source-specific server that matches the real input instead of checking unrelated MCPs first.

## Adjacent Skills

- `/devkit:manage-setup` for installing tools and configuring MCP servers
- `/devkit:manage-improve` for a full DevKit audit
