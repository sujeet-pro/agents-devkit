# input classifier: Jira URL

## Pattern

```
https?://<site>.atlassian.net/browse/<KEY>-<NUM>
https?://<site>.atlassian.net/jira/.../browse/<KEY>-<NUM>
```

## Fetch via

`adk-mcp-atlassian` → `getJiraIssue(cloudId, issueIdOrKey)` (the `mcp-atlassian` tool exposes the call directly).

Fallback (if MCP unreachable): direct REST.

```bash
curl -sS -u "$ATLASSIAN_USERNAME:$ATLASSIAN_API_TOKEN_CRED" \
  "https://$ATLASSIAN_SITE/rest/api/3/issue/$KEY" \
  | jq '{key, summary: .fields.summary, status: .fields.status.name, type: .fields.issuetype.name,
         assignee: .fields.assignee.displayName, description: .fields.description,
         sprint: .fields.customfield_10020}'
```

## Extract into context.md

```markdown
### [jira] <KEY> — <summary>
url: <full URL>
status: <In Progress | Done | …>
type: <Story | Bug | Spike | …>
assignee: <name>
sprint: <name if any>
summary: <one paragraph from description, ≤80 words>
acceptance criteria:
  - <bullet>
  - <bullet>
linked issues:
  - blocks: <KEY>
  - blocked-by: <KEY>
attachments: <count, names>
key comments: <last 3 if substantive>
```

## Hints for downstream skills

- `/adk-implement`: acceptance criteria → success criteria in plan.md.
- `/adk-review`: if linked PR exists, fetch it.
- `/adk-investigate`: if linked incident/RCA, fetch.
- `/adk-document --type pr-body`: cite the ticket key as the trailer.
