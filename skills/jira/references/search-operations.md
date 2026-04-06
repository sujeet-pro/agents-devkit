# Search Operations

Jira REST API v3 — `${JIRA_URL}/rest/api/3`

## JQL Search

### POST (preferred for complex queries)

```
POST /rest/api/3/search
```

Body:
```json
{
  "jql": "project = PROJ AND status = 'In Progress' ORDER BY priority DESC",
  "maxResults": 50,
  "startAt": 0,
  "fields": ["summary", "status", "assignee", "priority", "issuetype", "created", "updated"]
}
```

### GET (simpler queries)

```
GET /rest/api/3/search?jql=project%20%3D%20PROJ&maxResults=50&startAt=0&fields=summary,status,assignee
```

### Response

```json
{
  "startAt": 0,
  "maxResults": 50,
  "total": 125,
  "issues": [
    {
      "key": "PROJ-123",
      "fields": {
        "summary": "Issue title",
        "status": {"name": "In Progress"},
        "assignee": {"displayName": "User", "accountId": "..."},
        "priority": {"name": "High"},
        "issuetype": {"name": "Task"}
      }
    }
  ]
}
```

Script: `bash scripts/search.sh "project = PROJ AND status = 'In Progress'" [--max-results 50] [--start-at 0] [--fields "summary,status,assignee"]`

## Common JQL Patterns

### By Project
```
project = PROJ
project in (PROJ1, PROJ2)
```

### By Assignee
```
assignee = currentUser()
assignee = "5b10a2844c20165700ede21g"
assignee is EMPTY
assignee was currentUser()
```

### By Status
```
status = "In Progress"
status in ("To Do", "In Progress")
statusCategory = "In Progress"
statusCategory != Done
```

### By Type
```
issuetype = Bug
issuetype in (Bug, Task)
issuetype = Epic
```

### By Priority
```
priority = High
priority in (Highest, High)
```

### By Sprint
```
sprint in openSprints()
sprint in futureSprints()
sprint in closedSprints()
sprint = "Sprint 42"
```

### By Date
```
created >= -7d
created >= "2024-01-01"
updated >= -1d
due <= endOfWeek()
due < now()
```

### Text Search
```
text ~ "search term"
summary ~ "search term"
description ~ "search term"
comment ~ "search term"
```

### By Label
```
labels = "backend"
labels in ("backend", "api")
```

### By Component
```
component = "API"
component in ("API", "Frontend")
```

### By Epic
```
"Epic Link" = PROJ-100
```

### Combined Examples

My open work:
```
assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Sprint bugs:
```
sprint in openSprints() AND issuetype = Bug AND project = PROJ ORDER BY priority DESC
```

Unassigned high priority:
```
assignee is EMPTY AND priority in (Highest, High) AND statusCategory != Done AND project = PROJ
```

Recently created:
```
project = PROJ AND created >= -7d ORDER BY created DESC
```

Stale in progress:
```
status = "In Progress" AND updated <= -14d AND project = PROJ
```

Overdue:
```
due < now() AND statusCategory != Done AND project = PROJ ORDER BY due ASC
```

## Pagination

Use `startAt` + `maxResults` to paginate through results. Loop until `startAt + maxResults >= total`.

```
Page 1: startAt=0, maxResults=50 → get issues 0-49
Page 2: startAt=50, maxResults=50 → get issues 50-99
...continue until startAt >= total
```

## Ordering

Append `ORDER BY` to JQL:
```
ORDER BY priority DESC
ORDER BY created DESC
ORDER BY updated ASC
ORDER BY priority DESC, created DESC
```
