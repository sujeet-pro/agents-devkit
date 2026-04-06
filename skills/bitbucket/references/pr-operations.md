# PR Operations

All operations use script `scripts/pr.sh`.

## get

Fetch a single pull request.

```bash
bash scripts/pr.sh get <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}`

**Response fields**: `id`, `title`, `description`, `state` (OPEN|MERGED|DECLINED|SUPERSEDED), `author.display_name`, `source.branch.name`, `destination.branch.name`, `created_on`, `updated_on`, `comment_count`, `task_count`

## list

List pull requests filtered by state.

```bash
bash scripts/pr.sh list <workspace> <repo> [--state OPEN|MERGED|DECLINED|SUPERSEDED]
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests?state={state}`

Default state: `OPEN`. Returns paginated `values` array.

## diff

Get the full text diff for a PR.

```bash
bash scripts/pr.sh diff <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diff`

Returns raw unified diff text (not JSON). The script outputs the diff directly to stdout.

## diffstat

Get file-level change summary.

```bash
bash scripts/pr.sh diffstat <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diffstat`

**Response fields per file**: `status` (added|removed|modified|renamed), `old.path`, `new.path`, `lines_added`, `lines_removed`

## create

Create a new pull request.

```bash
bash scripts/pr.sh create <workspace> <repo> \
  --title "PR title" \
  --source-branch feature-branch \
  [--dest-branch main] \
  [--description "PR description"]
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests`

**Request body**:
```json
{
  "title": "PR title",
  "source": {"branch": {"name": "feature-branch"}},
  "destination": {"branch": {"name": "main"}},
  "description": "PR description"
}
```

## update

Update a PR's title or description.

```bash
bash scripts/pr.sh update <workspace> <repo> <pr-id> \
  [--title "New title"] \
  [--description "New description"]
```

**Endpoint**: `PUT /2.0/repositories/{workspace}/{repo}/pullrequests/{id}`

Sends only the fields specified.

## merge

Merge a pull request.

```bash
bash scripts/pr.sh merge <workspace> <repo> <pr-id> \
  [--strategy merge_commit|squash|fast_forward] \
  [--close-source true|false]
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/merge`

**Request body**:
```json
{
  "merge_strategy": "squash",
  "close_source_branch": true
}
```

Default strategy: `merge_commit`. Default close_source: `true`.

## decline

Decline a pull request.

```bash
bash scripts/pr.sh decline <workspace> <repo> <pr-id>
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/decline`

## approve

Approve a pull request.

```bash
bash scripts/pr.sh approve <workspace> <repo> <pr-id>
```

**Endpoint**: `POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/approve`

## unapprove

Remove approval from a pull request.

```bash
bash scripts/pr.sh unapprove <workspace> <repo> <pr-id>
```

**Endpoint**: `DELETE /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/approve`

## commits

List commits in a pull request.

```bash
bash scripts/pr.sh commits <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/commits`

**Response fields per commit**: `hash`, `message`, `author.raw`, `date`

## statuses

Get build/pipeline statuses for a PR.

```bash
bash scripts/pr.sh statuses <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/statuses`

**Response fields per status**: `state` (SUCCESSFUL|FAILED|INPROGRESS|STOPPED), `name`, `url`, `created_on`

## activity

Get the activity feed for a PR (comments, approvals, updates, status changes).

```bash
bash scripts/pr.sh activity <workspace> <repo> <pr-id>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/activity`
