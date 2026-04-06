# Review Operations

## Create a Review

Submit a review with inline comments:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  -f body="Overall review summary" \
  -f event="COMMENT" \
  -f 'comments=[{"path":"src/main.ts","line":10,"body":"Consider using const here."}]'
```

Event values: `COMMENT`, `APPROVE`, `REQUEST_CHANGES`.

### Inline Comment JSON Format

Single-line comment:

```json
{
  "path": "src/main.ts",
  "line": 10,
  "body": "**suggestion (performance, low):** Use `Map` instead of object for frequent lookups."
}
```

Multi-line comment (highlights lines 5–10):

```json
{
  "path": "src/main.ts",
  "start_line": 5,
  "line": 10,
  "body": "This block should be extracted into a helper function."
}
```

### `position` vs `line` vs `start_line`+`line`

- **`line`** — absolute line number in the file (preferred). Refers to the line in the diff's new version of the file.
- **`start_line` + `line`** — defines a multi-line comment range. `start_line` is the first line, `line` is the last.
- **`position`** — legacy field, refers to the line's position within the diff hunk (1-indexed from hunk header). Avoid unless working with older API consumers.
- **`side`** — use `RIGHT` for new code (default), `LEFT` for deleted code.

### Submitting from a File

Write comments to a JSON file, then submit:

```bash
cat > /tmp/review-comments.json << 'EOF'
[
  {"path": "src/main.ts", "line": 10, "body": "Use const."},
  {"path": "src/utils.ts", "start_line": 20, "line": 25, "body": "Extract this block."}
]
EOF

gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  -f body="Review summary" \
  -f event="COMMENT" \
  --input /tmp/review-comments.json
```

Note: `--input` sends the JSON file as the request body. To combine with `-f` flags, construct the full JSON body manually:

```bash
jq -n --argjson comments "$(cat /tmp/review-comments.json)" \
  '{body: "Review summary", event: "COMMENT", comments: $comments}' | \
  gh api repos/{owner}/{repo}/pulls/{number}/reviews --input -
```

## List Reviews

```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews --jq '.[] | {id: .id, user: .user.login, state: .state, body: .body}'
```

## List Review Comments

All comments on a PR:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
```

Key fields per comment:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate \
  --jq '.[] | {id: .id, node_id: .node_id, path: .path, line: .line, body: .body, user: .user.login, in_reply_to_id: .in_reply_to_id}'
```

## Reply to a Comment

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies \
  -f body="Thanks, fixed in the latest push."
```

## Create a Standalone Comment

Requires the latest commit SHA on the PR head:

```bash
HEAD_SHA=$(gh api repos/{owner}/{repo}/pulls/{number} --jq '.head.sha')

gh api repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="This needs a nil check." \
  -f path="src/handler.go" \
  -F line=42 \
  -f commit_id="$HEAD_SHA"
```

Multi-line standalone comment:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="Extract this block." \
  -f path="src/handler.go" \
  -F start_line=35 \
  -F line=42 \
  -f commit_id="$HEAD_SHA"
```

## Resolve a Thread

Resolving requires the thread's GraphQL `node_id`. Get it from the comment's `node_id`:

### Step 1: Get the Review Thread ID

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            comments(first: 1) {
              nodes { body path line }
            }
          }
        }
      }
    }
  }
' -f owner="{owner}" -f repo="{repo}" -F number={number}
```

### Step 2: Resolve

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread { isResolved }
    }
  }
' -f threadId="THREAD_NODE_ID"
```

## Unresolve a Thread

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    unresolveReviewThread(input: {threadId: $threadId}) {
      thread { isResolved }
    }
  }
' -f threadId="THREAD_NODE_ID"
```

## Comment Metadata Format

Review comments use a metadata prefix to encode severity, principle, and confidence:

```
**<severity> (<category>, <confidence>):** <message>
```

Example:

```
**suggestion (performance, medium):** Use a Set for O(1) lookups instead of Array.includes().
```

Severity levels: `critical`, `warning`, `suggestion`, `nitpick`, `praise`.

## Idempotency

Before posting comments, check for existing ones to avoid duplicates.

### Step 1: List Existing Comments by Current User

```bash
CURRENT_USER=$(gh api user --jq '.login')

gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate \
  --jq "[.[] | select(.user.login == \"$CURRENT_USER\") | {id: .id, path: .path, line: .line, body: .body}]"
```

### Step 2: Detect Duplicates

A comment is a duplicate if all of these match an existing comment:
- Same `path`
- Same `line` (or overlapping `start_line`–`line` range)
- Same severity prefix (first bold word in the body)

### Step 3: Skip or Update

- **Skip**: Drop the comment from the review submission.
- **Update in-place**: PATCH the existing comment:

```bash
gh api repos/{owner}/{repo}/pulls/comments/{comment_id} -X PATCH -f body="Updated comment body"
```
