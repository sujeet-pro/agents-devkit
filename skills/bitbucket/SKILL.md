---
name: bitbucket
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

## API-First Approach

Always prefer direct REST API calls (via `curl`) over MCP tools. The bundled scripts under `scripts/` wrap the Bitbucket REST API and work in any environment (Claude Code, Codex, etc.) without MCP dependencies. If the scripts are not accessible via `${CLAUDE_SKILL_DIR}`, construct `curl` commands directly from the reference docs below — do NOT create new shell scripts.

MCP tools (`mcp__bitbucket__*`) may be used as a secondary option when available, but fall back to direct API calls for any operation not covered or if MCP fails.

## Comments

By default, "comments" means **inline comments** — comments attached to a specific file and line in a PR. Use the `--file` and `--line` flags with `comments.sh create`, or the `inline` field in the REST API body. General (non-inline) comments are only used for PR-level summaries.

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
