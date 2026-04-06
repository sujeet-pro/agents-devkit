# Issue Operations

Jira REST API v3 — `${JIRA_URL}/rest/api/3`

## Get Issue

```
GET /rest/api/3/issue/{issueIdOrKey}
```

Query parameters:
- `expand` — comma-separated: `renderedFields`, `changelog`, `transitions`, `editmeta`
- `fields` — comma-separated field keys to return (default: all)

Response includes: `key`, `fields.summary`, `fields.status`, `fields.assignee`, `fields.priority`, `fields.issuetype`, `fields.description`, `fields.issuelinks`, `fields.comment`, `fields.created`, `fields.updated`

Script: `bash scripts/issues.sh get --key PROJ-123 [--expand renderedFields,changelog]`

## Create Issue

```
POST /rest/api/3/issue
```

Body:
```json
{
  "fields": {
    "project": {"key": "PROJ"},
    "summary": "Issue title",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "Description text here"}]
        }
      ]
    },
    "issuetype": {"name": "Task"},
    "priority": {"name": "Medium"},
    "assignee": {"accountId": "5b10a2844c20165700ede21g"},
    "labels": ["backend", "api"]
  }
}
```

### ADF (Atlassian Document Format)

The v3 API requires description in ADF format:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Paragraph text"}]
    }
  ]
}
```

Multi-paragraph:
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "First paragraph"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "Second paragraph"}]}
  ]
}
```

For simple text, some Jira instances accept plain strings in the `description` field, but ADF is the standard for API v3.

Response: `{"id": "10001", "key": "PROJ-123", "self": "https://..."}`

Script: `bash scripts/issues.sh create --project PROJ --type Task --summary "Title" [--description "Text"] [--priority Medium] [--assignee accountId] [--labels "label1,label2"]`

## Update Issue

```
PUT /rest/api/3/issue/{issueIdOrKey}
```

Body (fields style):
```json
{
  "fields": {
    "summary": "Updated title",
    "priority": {"name": "High"}
  }
}
```

Body (update style — for array fields):
```json
{
  "update": {
    "labels": [{"add": "new-label"}],
    "summary": [{"set": "New summary"}]
  }
}
```

Returns 204 No Content on success.

Script: `bash scripts/issues.sh update --key PROJ-123 [--summary "New title"] [--description "Text"] [--priority High] [--assignee accountId] [--labels "label1,label2"]`

## Delete Issue

```
DELETE /rest/api/3/issue/{issueIdOrKey}
```

Query parameters:
- `deleteSubtasks` — `true` to delete subtasks (default: false)

Returns 204 No Content on success.

Script: `bash scripts/issues.sh delete --key PROJ-123`

## List Transitions

```
GET /rest/api/3/issue/{issueIdOrKey}/transitions
```

Response: `{"transitions": [{"id": "11", "name": "To Do"}, {"id": "21", "name": "In Progress"}, ...]}`

Script: `bash scripts/issues.sh transitions --key PROJ-123`

## Transition Issue

```
POST /rest/api/3/issue/{issueIdOrKey}/transitions
```

Body:
```json
{
  "transition": {"id": "21"},
  "fields": {
    "resolution": {"name": "Done"}
  },
  "update": {
    "comment": [
      {
        "add": {
          "body": {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Closing comment"}]}]
          }
        }
      }
    ]
  }
}
```

Returns 204 No Content on success.

Script: `bash scripts/issues.sh transition --key PROJ-123 --transition-id 21 [--comment "Closing comment"] [--resolution Done]`

## Assign Issue

```
PUT /rest/api/3/issue/{issueIdOrKey}/assignee
```

Body:
```json
{"accountId": "5b10a2844c20165700ede21g"}
```

Use `{"accountId": null}` to unassign.

Returns 204 No Content on success.

Script: `bash scripts/issues.sh assign --key PROJ-123 --account-id 5b10a2844c20165700ede21g`

## Link Issues

```
POST /rest/api/3/issueLink
```

Body:
```json
{
  "type": {"name": "Blocks"},
  "inwardIssue": {"key": "PROJ-123"},
  "outwardIssue": {"key": "PROJ-456"}
}
```

Common link types: `Blocks`, `Cloners`, `Duplicate`, `Relates`

Returns 201 Created on success.

Script: `bash scripts/issues.sh link --from PROJ-123 --to PROJ-456 --type "Blocks"`

## Get Watchers

```
GET /rest/api/3/issue/{issueIdOrKey}/watchers
```

Response: `{"watchCount": 2, "watchers": [{"accountId": "...", "displayName": "..."}]}`

Script: `bash scripts/issues.sh watchers --key PROJ-123`

## Add Watcher

```
POST /rest/api/3/issue/{issueIdOrKey}/watchers
```

Body: `"accountId"` (JSON string, not object)

Returns 204 No Content on success.

Script: `bash scripts/issues.sh add-watcher --key PROJ-123 --account-id 5b10a2844c20165700ede21g`

## Get Worklogs

```
GET /rest/api/3/issue/{issueIdOrKey}/worklog
```

Response: `{"worklogs": [{"timeSpent": "2h", "author": {...}, "comment": {...}}]}`

Script: `bash scripts/issues.sh worklog --key PROJ-123`

## Add Worklog

```
POST /rest/api/3/issue/{issueIdOrKey}/worklog
```

Body:
```json
{
  "timeSpent": "2h 30m",
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Worked on API integration"}]}]
  }
}
```

Returns 201 Created on success.

Script: `bash scripts/issues.sh add-worklog --key PROJ-123 --time-spent "2h" [--comment "What was done"]`
