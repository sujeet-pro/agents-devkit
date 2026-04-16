# adk-github

Manage GitHub pull requests, issues, releases, and repository operations via MCP or gh CLI.

## Quick Start

```
npx adk-github "create a PR from feature/auth to main"
```

Or as a slash command:

```
/adk-github create a PR from feature/auth to main with title "Add OAuth2 flow"
```

## What This Skill Does

Executes pull request, issue, release, branch, and repository operations against the GitHub API. Uses an MCP-first approach: when the GitHub MCP server is configured, all operations route through MCP tools. When MCP is unavailable, the skill falls back to the `gh` CLI. Both paths produce the same observable results (URLs, IDs, status confirmations).

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What GitHub operation to perform |
| `--action` | `pr`, `issue`, `release`, `search`, `repo` | auto-detect | Narrow the operation domain when ambiguous |
| `--target` | `owner/repo` | detect from git remote | Repository to operate against |
| `--auto` | flag | off | Skip confirmations for non-destructive operations |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required | Notes |
| --- | --- | --- | --- |
| `git` | command | yes | Must be on PATH |
| `python3` | command | yes | Must be on PATH |
| `gh` | command | no | Fallback when MCP is unavailable; must be authenticated via `gh auth login` |
| GitHub MCP server | MCP server | no | Primary integration path; falls back to `gh` if missing |

### MCP Setup

To configure the GitHub MCP server, add the following to your Claude settings file (`.claude/settings.json` or `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

If MCP is not configured, ensure `gh` is installed and authenticated:

```bash
gh auth login
gh auth status
```

## Skill Layout

```
adk-github/
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

1. Run preflight to detect MCP server availability and gh CLI fallback.
2. Detect the target repository from `--target`, git remote origin, or ask the user.
3. Confirm the action scope, target repository, and any destructive implications.
4. Execute the operation using MCP tools when available, falling back to gh CLI.
5. Validate the result by checking for a confirmable artifact (URL, ID, status).
6. Report the outcome with direct links, identifiers, and suggested next steps.

## Interaction Protocol

- Confirm before destructive operations (merge, close, delete, force-push) even with `--auto`.
- Non-destructive reads (list, search, fetch) proceed immediately.
- Every response includes direct URLs to the affected GitHub resource.
- Errors include remediation guidance (permissions, 404, rate limit).
- Batch results are presented as concise tables with drill-down offered.

## Output Format

Each response includes:
- **Action**: what was performed (e.g., "created pull request", "closed issue")
- **Target**: repository and resource identifier (e.g., `owner/repo#42`)
- **Result**: direct URL or ID of the created/modified resource
- **Next steps**: follow-up actions the user may want

## Examples

Create a pull request:
```
/adk-github create a PR from feature/auth to main with title "Add OAuth2 flow"
```

Search issues:
```
/adk-github search issues labeled "bug" in acme/backend that mention "timeout"
```

List releases:
```
/adk-github list releases for acme/frontend --target acme/frontend
```

## What Success Looks Like

- [ ] Every mutating operation produces a confirmable artifact (URL, ID, or SHA)
- [ ] Read operations return non-empty data or an explicit "not found" status
- [ ] Destructive operations are confirmed with the user before execution
- [ ] Results include direct links to the affected GitHub resources
- [ ] Errors include clear remediation steps
- [ ] MCP is used when available; gh CLI fallback works seamlessly
