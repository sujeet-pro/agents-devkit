# adk-bitbucket

Manage Bitbucket pull requests, repositories, pipelines, and code reviews via MCP.

## Quick Start

```
npx adk-bitbucket "create a PR from feature/payments to develop"
```

Or as a slash command:

```
/adk-bitbucket create a PR from feature/payments to develop in acme/checkout
```

## What This Skill Does

Manages the full Bitbucket lifecycle: pull request creation through merge, batch code review with pending comments, pipeline monitoring and triggering, and repository/branching model management. All operations go through the Bitbucket MCP server for structured input/output and reliable error handling.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What should be done on Bitbucket |
| `--action` | `pr`, `review`, `pipeline`, `repo` | auto-detected | Narrow the operation category |
| `--target` | `workspace/repo-slug` | auto-detected from git remote | Bitbucket workspace and repository |
| `--auto` | flag | off | Skip confirmations for non-destructive operations |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required | Notes |
| --- | --- | --- | --- |
| `git` | command | yes | Must be on PATH |
| `python3` | command | yes | Must be on PATH |
| Bitbucket MCP server | MCP server | yes | Required for all operations |

### MCP Setup

To configure the Bitbucket MCP server, add the following to your Claude settings file (`.claude/settings.json` or `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "bitbucket": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-bitbucket"],
      "env": {
        "BITBUCKET_USERNAME": "<your-username>",
        "BITBUCKET_APP_PASSWORD": "<your-app-password>"
      }
    }
  }
}
```

Generate an app password at: `https://bitbucket.org/account/settings/app-passwords/` with the following permissions: Repositories (read/write), Pull requests (read/write), Pipelines (read/write).

## Skill Layout

```
adk-bitbucket/
  SKILL.md                                # Skill definition
  README.md                               # This file
  scripts/
    preflight.py                          # Pre-flight checks
  references/
    workflow.md                           # Workflow guidance
    persona.md                            # Persona guidance
    _shared/
      ai-guidelines-overview.md           # Shared AI guidelines
      constitution.md                     # Shared constitution
      research-protocol.md                # Shared research protocol
      output-format.md                    # Shared output format
```

## Workflow

1. Run preflight to verify MCP server availability and CLI dependencies.
2. Detect the target workspace and repository from `--target` or from the current git remote.
3. Confirm the requested action and any destructive consequences with the user.
4. Execute the operation via the appropriate Bitbucket MCP tool.
5. Validate the result by reading back the affected resource (PR state, pipeline status, comment thread).
6. Report the outcome with links, status, and next steps.

## Interaction Protocol

- Confirm before merge, decline, stop-pipeline, or branching model changes even with `--auto`.
- Present PR status clearly: title, state, reviewers, approval status, and pipeline check results.
- Non-destructive reads (listing PRs, reading diffs, fetching logs) proceed immediately.
- Batch review workflow: stage all comments as pending, present summary, then publish in one batch.
- Errors include remediation guidance (permissions, missing config, invalid target).

## Output Format

Each response includes:
- **Action**: what was performed
- **Target**: workspace/repo, PR number, or pipeline UUID
- **Result**: confirmation link or status
- **Next steps**: remaining work or follow-up actions

## Examples

Create a pull request:
```
/adk-bitbucket create a PR from feature/payments to develop in acme/checkout
```

Check pipeline status:
```
/adk-bitbucket show pipeline status for the latest run on main --target acme/checkout
```

Approve and merge:
```
/adk-bitbucket approve PR #42 and merge if all checks pass --target acme/checkout
```

## What Success Looks Like

- [ ] Every MCP operation produces a verifiable result (PR URL, pipeline UUID, comment ID)
- [ ] After creating or merging a PR, the PR state is read back to confirm
- [ ] After triggering a pipeline, the run status is read back
- [ ] Destructive operations (merge, decline, stop) are confirmed with the user
- [ ] Batch review comments are staged and published in one operation
- [ ] Errors include clear remediation steps
