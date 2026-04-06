# PR Operations

## Get PR Details

```bash
gh pr view <number> --json title,body,author,state,headRefName,baseRefName,mergeable,additions,deletions,changedFiles,number,url,labels,reviewDecision,statusCheckRollup
```

Extract specific fields:

```bash
gh pr view <number> --json title,state --jq '{title: .title, state: .state}'
```

## Get PR Diff

```bash
gh pr diff <number>
```

Diff for a specific file:

```bash
gh pr diff <number> -- path/to/file.ts
```

## Get PR Files

Via `gh pr view`:

```bash
gh pr view <number> --json files --jq '.files[].path'
```

Via API (includes patch, status, additions, deletions per file):

```bash
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate
```

Extract paths only:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/files --paginate --jq '.[].filename'
```

## List PRs

```bash
gh pr list --json number,title,author,state,headRefName,baseRefName,url --limit 30
```

Filter by state:

```bash
gh pr list --state open --json number,title
gh pr list --state closed --json number,title
gh pr list --state merged --json number,title
```

Filter by author:

```bash
gh pr list --author "@me" --json number,title
```

## Create PR

```bash
gh pr create --title "Add feature X" --body "$(cat <<'EOF'
## Summary
Description here.

## Test Plan
- [ ] Unit tests pass
EOF
)"
```

With base branch:

```bash
gh pr create --title "..." --body "..." --base main
```

As draft:

```bash
gh pr create --title "..." --body "..." --draft
```

## Update PR

```bash
gh api repos/{owner}/{repo}/pulls/{number} -X PATCH \
  -f title="Updated title" \
  -f body="Updated body"
```

Update only the body:

```bash
gh api repos/{owner}/{repo}/pulls/{number} -X PATCH -f body="New body content"
```

## Merge PR

```bash
gh pr merge <number> --merge
gh pr merge <number> --squash
gh pr merge <number> --rebase
```

With auto-merge (waits for checks):

```bash
gh pr merge <number> --squash --auto
```

Delete branch after merge:

```bash
gh pr merge <number> --squash --delete-branch
```

## Close PR

```bash
gh pr close <number>
```

With comment:

```bash
gh pr close <number> --comment "Closing because..."
```

## Get PR Commits

```bash
gh api repos/{owner}/{repo}/pulls/{number}/commits --paginate --jq '.[].sha'
```

With message:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/commits --paginate --jq '.[] | {sha: .sha, message: .commit.message}'
```

## Get PR Checks

```bash
gh pr checks <number>
```

JSON output:

```bash
gh pr checks <number> --json name,state,conclusion
```
