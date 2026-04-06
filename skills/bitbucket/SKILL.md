---
name: adk-bitbucket
description: "adk - [helper] [connector] Bitbucket REST API operations — PR reviews, comments, repository access, and pipeline status"
user-invocable: false
workflow-tier: helper
dependencies:
  commands: [curl, jq]
---

# Bitbucket

Platform connector for Bitbucket Cloud. Uses the Bitbucket REST API v2.0 via `curl`.

## Auth

Requires environment variables in `~/.zshenv`:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_TOKEN="your-app-password"
```

Generate an app password at: https://bitbucket.org/account/settings/app-passwords/
Required scopes: `repository:read`, `pullrequest:read`, `pullrequest:write`

### Validation

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/auth.sh
```

If auth fails or token is expired, tell the user:
> Add or update your Bitbucket credentials in `~/.zshenv`:
> ```bash
> export BITBUCKET_USERNAME="your-username"
> export BITBUCKET_TOKEN="your-app-password"
> ```
> Then run `source ~/.zshenv` and retry.

## MCP Connector Detection

Before using scripts, check if a Bitbucket MCP connector is available:

1. Look for tools matching `mcp__bitbucket__*` pattern
2. If available, prefer MCP tools for supported operations
3. Fall back to scripts for operations not covered by the MCP

## API Base

All endpoints use: `https://api.bitbucket.org/2.0`

## Routing

Load `${CLAUDE_SKILL_DIR}/references/routing.md` to determine which reference and script to use.

## Operation References

| Domain | Reference | Script | Common Use Cases |
|--------|-----------|--------|-----------------|
| PR Management | `${CLAUDE_SKILL_DIR}/references/pr-operations.md` | `scripts/pr.sh` | Get PR, diff, diffstat, create, update, merge, approve |
| Comments | `${CLAUDE_SKILL_DIR}/references/comment-operations.md` | `scripts/comments.sh` | List, create inline, reply, update, delete |
| Repository | `${CLAUDE_SKILL_DIR}/references/repo-operations.md` | `scripts/repo.sh` | File contents, branches, commits |

## Script Usage

All scripts accept subcommands:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/pr.sh <action> <workspace> <repo> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/comments.sh <action> <workspace> <repo> <pr-id> [args...]
bash ${CLAUDE_SKILL_DIR}/scripts/repo.sh <action> <workspace> <repo> [args...]
```

Scripts output JSON to stdout. Errors go to stderr. Non-zero exit on failure.
