# Comment Operations

Jira REST API v3 — `${JIRA_URL}/rest/api/3`

## List Comments

```
GET /rest/api/3/issue/{issueIdOrKey}/comment
```

Query parameters:
- `startAt` — pagination offset (default: 0)
- `maxResults` — page size (default: 50)
- `orderBy` — `created` or `-created` (descending)
- `expand` — `renderedBody` for HTML-rendered content

Response:
```json
{
  "startAt": 0,
  "maxResults": 50,
  "total": 3,
  "comments": [
    {
      "id": "10001",
      "author": {"accountId": "...", "displayName": "..."},
      "body": {"type": "doc", "version": 1, "content": [...]},
      "created": "2024-01-15T10:00:00.000+0000",
      "updated": "2024-01-15T10:00:00.000+0000"
    }
  ]
}
```

Script: `bash scripts/comments.sh list --key PROJ-123`

## Get Comment

```
GET /rest/api/3/issue/{issueIdOrKey}/comment/{id}
```

Returns single comment object.

Script: `bash scripts/comments.sh get --key PROJ-123 --comment-id 10001`

## Add Comment

```
POST /rest/api/3/issue/{issueIdOrKey}/comment
```

Body (ADF format):
```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Comment text here"}]
      }
    ]
  }
}
```

Returns 201 Created with comment object.

Script: `bash scripts/comments.sh add --key PROJ-123 --body "Comment text"`

The script converts plain text `--body` to ADF format internally. Multi-line text is split into separate paragraph nodes.

## Update Comment

```
PUT /rest/api/3/issue/{issueIdOrKey}/comment/{id}
```

Body: same ADF format as add.

Returns updated comment object.

Script: `bash scripts/comments.sh update --key PROJ-123 --comment-id 10001 --body "Updated text"`

## Delete Comment

```
DELETE /rest/api/3/issue/{issueIdOrKey}/comment/{id}
```

Returns 204 No Content on success.

Script: `bash scripts/comments.sh delete --key PROJ-123 --comment-id 10001`
