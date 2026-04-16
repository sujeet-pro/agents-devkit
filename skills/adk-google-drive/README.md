# adk-google-drive

Manage Google Docs, Sheets, Slides, and Drive files via MCP.

## Quick Start

```bash
npx adk-google-drive "create a project brief" --type doc
```

## What This Skill Does

Platform connector for Google Workspace. Creates, reads, updates, searches, and shares Google Docs, Sheets, Slides, and Drive files through the Google Drive MCP server. All operations route through `mcp__google-drive__*` tools for structured input/output and reliable error handling. Verifies OAuth authentication status before executing operations and produces confirmable artifacts (document URLs, file IDs, sharing status) for every mutating action.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What Google Drive operation to perform |
| `--action` | `create`, `read`, `update`, `share`, `search` | auto-detect | Narrow the operation domain when ambiguous |
| `--type` | `doc`, `sheet`, `slides`, `file` | auto-detect | Target document type |
| `--target` | file ID or name | none | Specific file to operate on |
| `--auto` | flag | off | Skip confirmations for non-destructive operations |
| `--help` | flag | off | Show this skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | CLI command | yes |
| `python3` | CLI command | yes |
| `google-drive` MCP server | MCP server | yes |
| OAuth credentials | authentication | yes |

### MCP Setup

The Google Drive MCP server must be configured in your Claude settings. Add it to `.claude/settings.json` or `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@anthropic/google-drive-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "<your-client-id>",
        "GOOGLE_CLIENT_SECRET": "<your-client-secret>"
      }
    }
  }
}
```

OAuth scopes required: Google Drive read/write, Google Docs, Google Sheets, Google Slides. The preflight script checks for MCP server configuration and provides setup instructions if missing.

## Skill Layout

```
skills/adk-google-drive/
  SKILL.md                              # Skill definition and frontmatter
  README.md                             # This file
  scripts/
    preflight.py                        # MCP server and auth verification
  references/
    persona.md                          # Skill-specific persona
    workflow.md                         # Skill-specific workflow detail
    _shared/
      ai-guidelines-overview.md         # Shared ADK guidance
      constitution.md                   # Shared constitution
      output-format.md                  # Shared output format
      research-protocol.md              # Shared research protocol
```

## Workflow

1. Run preflight to verify auth status and MCP server availability.
2. Identify the target document or folder from `--target`, search results, or user input.
3. Confirm the action scope, target document, and any destructive implications.
4. Execute the operation using the appropriate `mcp__google-drive__*` tools.
5. Validate the result by checking for a confirmable artifact (URL, file ID, status).
6. Report the outcome with direct links, identifiers, and suggested next steps.

## Interaction Protocol

- **Confirm action and target document** -- before executing, confirm which operation will be performed and on which document or folder.
- **Present content preview before writing** -- for create and update operations, show a preview and wait for approval.
- **Report document URL** -- every response includes a direct link to the affected resource.
- **Confirm before destructive operations** -- always ask before delete, overwrite, or permission-removal, even with `--auto`.
- **Surface errors with remediation** -- if an operation fails (auth expired, permission denied), explain why and suggest a fix.

## Output Format

- **action**: what was performed (e.g., "created Google Doc", "shared spreadsheet")
- **target**: document name and file ID
- **result**: direct URL to the document or folder
- **sharing**: current sharing status when relevant
- **remaining items**: follow-up actions the user may want

## Examples

Create a new Google Doc:
```
/adk-google-drive create a project brief document titled "Q3 Planning" --type doc
```

Read data from a Google Sheet:
```
/adk-google-drive read sales data from the Q2 Revenue sheet --action read --type sheet --target "Q2 Revenue"
```

Update Google Slides:
```
/adk-google-drive update the team standup slides with this week's agenda --action update --type slides --target "Weekly Standup"
```

## What Success Looks Like

- [ ] MCP server is configured and authenticated before operations
- [ ] Action and target are confirmed before execution
- [ ] Content preview is shown before create/update operations
- [ ] Every mutating operation produces a confirmable artifact (URL or file ID)
- [ ] Destructive operations require explicit confirmation
- [ ] Read operations return content or explicit "not found" status
- [ ] Direct document URLs are included in every response
