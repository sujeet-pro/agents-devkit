# Board & Sprint Operations

Jira Agile REST API v1 — `${JIRA_URL}/rest/agile/1.0`

## List Boards

```
GET /rest/agile/1.0/board
```

Query parameters:
- `projectKeyOrId` — filter by project
- `type` — `scrum`, `kanban`, or `simple`
- `startAt`, `maxResults` — pagination

Response:
```json
{
  "maxResults": 50,
  "startAt": 0,
  "total": 5,
  "values": [
    {"id": 1, "name": "PROJ board", "type": "scrum", "location": {"projectKey": "PROJ"}}
  ]
}
```

Script: `bash scripts/boards.sh list [--project PROJ]`

## Get Board

```
GET /rest/agile/1.0/board/{boardId}
```

Script: `bash scripts/boards.sh get --board-id 1`

## Board Configuration

```
GET /rest/agile/1.0/board/{boardId}/configuration
```

Returns column mappings, estimation field, ranking, filter.

Script: `bash scripts/boards.sh config --board-id 1`

## List Sprints

```
GET /rest/agile/1.0/board/{boardId}/sprint
```

Query parameters:
- `state` — comma-separated: `active`, `future`, `closed`
- `startAt`, `maxResults` — pagination

Response:
```json
{
  "values": [
    {
      "id": 100,
      "name": "Sprint 42",
      "state": "active",
      "startDate": "2024-01-15T00:00:00.000Z",
      "endDate": "2024-01-29T00:00:00.000Z",
      "originBoardId": 1
    }
  ]
}
```

Script: `bash scripts/boards.sh sprints --board-id 1 [--state active,future]`

## Get Sprint

```
GET /rest/agile/1.0/sprint/{sprintId}
```

Script: uses the sprints list endpoint filtered by ID.

## Sprint Issues

```
GET /rest/agile/1.0/sprint/{sprintId}/issue
```

Query parameters:
- `fields` — comma-separated fields to return
- `startAt`, `maxResults` — pagination

Script: `bash scripts/boards.sh sprint-issues --sprint-id 100`

## Move Issues to Sprint

```
POST /rest/agile/1.0/sprint/{sprintId}/issue
```

Body:
```json
{
  "issues": ["PROJ-1", "PROJ-2", "PROJ-3"]
}
```

Returns 204 No Content on success.

Script: `bash scripts/boards.sh move-to-sprint --sprint-id 100 --issues "PROJ-1,PROJ-2"`

## Get Backlog

```
GET /rest/agile/1.0/board/{boardId}/backlog
```

Query parameters:
- `fields` — comma-separated fields
- `startAt`, `maxResults` — pagination

Script: `bash scripts/boards.sh backlog --board-id 1`

## Move Issues to Backlog

```
POST /rest/agile/1.0/backlog/issue
```

Body:
```json
{
  "issues": ["PROJ-1"]
}
```

Returns 204 No Content on success.

Script: `bash scripts/boards.sh move-to-backlog --issues "PROJ-1,PROJ-2"`

## Rank Issues

```
PUT /rest/agile/1.0/issue/rank
```

Body:
```json
{
  "issues": ["PROJ-1"],
  "rankBeforeIssue": "PROJ-2"
}
```

Returns 204 No Content on success.

Script: `bash scripts/boards.sh rank --issues "PROJ-1" --rank-before "PROJ-2"`
