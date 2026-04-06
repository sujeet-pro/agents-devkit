# Comment Operations

All comment operations use script `scripts/comments.sh`.

## list

List all comments on a pull request.

```bash
bash scripts/comments.sh list <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments`

**Response fields per comment**: `id`, `content.raw`, `user.display_name`, `inline` (if inline comment: `inline.path`, `inline.from`, `inline.to`), `parent.id` (if reply), `created_on`, `updated_on`

## get

Get a single comment.

```bash
bash scripts/comments.sh get <workspace> <repo> <pr-id> --comment-id <id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments/{comment_id}`

## create

Post a new comment on a PR.

**General comment**:
```bash
bash scripts/comments.sh create <workspace> <repo> <pr-id> --body "Review looks good"
```

**Inline comment** (on a specific file and line):
```bash
bash scripts/comments.sh create <workspace> <repo> <pr-id> \
  --body "Consider extracting this" --file src/main.py --line 42
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments`

**Request body (general)**:
```json
{"content": {"raw": "Review looks good"}}
```

**Request body (inline)**:
```json
{
  "content": {"raw": "Consider extracting this"},
  "inline": {"path": "src/main.py", "to": 42}
}
```

## reply

Reply to an existing comment.

```bash
bash scripts/comments.sh reply <workspace> <repo> <pr-id> \
  --parent-id 123 --body "Agreed, will fix"
```

**Request body**:
```json
{
  "content": {"raw": "Agreed, will fix"},
  "parent": {"id": 123}
}
```

## update

Update an existing comment.

```bash
bash scripts/comments.sh update <workspace> <repo> <pr-id> \
  --comment-id 456 --body "Updated review comment"
```

**Endpoint**: `PUT /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments/{comment_id}`

## delete

Delete a comment.

```bash
bash scripts/comments.sh delete <workspace> <repo> <pr-id> --comment-id 456
```

**Endpoint**: `DELETE /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments/{comment_id}`

## Idempotency

Before posting comments, check for existing comments to avoid duplicates:

1. List existing comments: `comments.sh list <ws> <repo> <pr-id>`
2. Filter by `user.display_name` or `content.raw` to find your previous comments
3. If a matching comment exists, use `update` instead of `create`
4. For inline comments, also match on `inline.path` and `inline.to`

Pattern:
```bash
existing=$(bash scripts/comments.sh list ws repo 42 | jq '[.values[] | select(.content.raw | contains("MARKER"))]')
if [[ $(echo "$existing" | jq 'length') -gt 0 ]]; then
  comment_id=$(echo "$existing" | jq '.[0].id')
  bash scripts/comments.sh update ws repo 42 --comment-id "$comment_id" --body "updated text"
else
  bash scripts/comments.sh create ws repo 42 --body "new text"
fi
```

## Tasks

Bitbucket tasks track action items attached to PR comments.

### list-tasks

```bash
bash scripts/comments.sh list-tasks <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/tasks`

**Response fields per task**: `id`, `state` (OPEN|RESOLVED), `content.raw`, `comment.id`, `creator.display_name`

### create-task

```bash
bash scripts/comments.sh create-task <workspace> <repo> <pr-id> \
  --body "Fix the null check" [--comment-id 123]
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/tasks`

**Request body**:
```json
{
  "content": {"raw": "Fix the null check"},
  "comment": {"id": 123}
}
```

### resolve-task

```bash
bash scripts/comments.sh resolve-task <workspace> <repo> <pr-id> \
  --task-id 789 --state RESOLVED
```

**Endpoint**: `PUT /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/tasks/{task_id}`

**Request body**:
```json
{"state": "RESOLVED"}
```

Valid states: `OPEN`, `RESOLVED`.
