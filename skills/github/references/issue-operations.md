# Issue Operations

## Get Issue

```bash
gh issue view <number> --json number,title,body,author,state,labels,assignees,milestone,url,comments
```

Extract specific fields:

```bash
gh issue view <number> --json title,state,labels --jq '{title: .title, state: .state, labels: [.labels[].name]}'
```

## Create Issue

```bash
gh issue create --title "Bug: login fails on Safari" --body "Steps to reproduce..."
```

With labels and assignee:

```bash
gh issue create \
  --title "Bug: login fails on Safari" \
  --body "Steps to reproduce..." \
  --label "bug" \
  --label "priority:high" \
  --assignee "username"
```

With milestone:

```bash
gh issue create --title "..." --body "..." --milestone "v2.0"
```

## Update Issue

```bash
gh api repos/{owner}/{repo}/issues/{number} -X PATCH \
  -f title="Updated title" \
  -f body="Updated body"
```

Update state:

```bash
gh api repos/{owner}/{repo}/issues/{number} -X PATCH -f state="closed"
```

## Close Issue

```bash
gh issue close <number>
```

With comment:

```bash
gh issue close <number> --comment "Fixed in #123"
```

As not-planned:

```bash
gh issue close <number> --reason "not planned"
```

## List Issues

```bash
gh issue list --json number,title,state,labels,assignees --limit 30
```

Filter by label:

```bash
gh issue list --label "bug" --json number,title
```

Filter by state:

```bash
gh issue list --state closed --json number,title
gh issue list --state all --json number,title
```

Filter by assignee:

```bash
gh issue list --assignee "@me" --json number,title
```

Filter by milestone:

```bash
gh issue list --milestone "v2.0" --json number,title
```

## Add Comment

```bash
gh issue comment <number> --body "This is fixed in the latest release."
```

## List Comments

```bash
gh api repos/{owner}/{repo}/issues/{number}/comments --jq '.[] | {id: .id, user: .user.login, body: .body, created_at: .created_at}'
```

With pagination:

```bash
gh api repos/{owner}/{repo}/issues/{number}/comments --paginate --jq '.[].body'
```

## Add Labels

```bash
gh api repos/{owner}/{repo}/issues/{number}/labels -f "labels[]=bug" -f "labels[]=priority:high"
```

## Remove Label

```bash
gh api repos/{owner}/{repo}/issues/{number}/labels/{label_name} -X DELETE
```

URL-encode label names with special characters:

```bash
gh api repos/{owner}/{repo}/issues/{number}/labels/priority%3Ahigh -X DELETE
```

## Assign

```bash
gh api repos/{owner}/{repo}/issues/{number}/assignees -f "assignees[]=username1" -f "assignees[]=username2"
```

Remove assignees:

```bash
gh api repos/{owner}/{repo}/issues/{number}/assignees -X DELETE -f "assignees[]=username1"
```

## List Milestones

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | {number: .number, title: .title, state: .state, due_on: .due_on}'
```

Open milestones only:

```bash
gh api "repos/{owner}/{repo}/milestones?state=open" --jq '.[] | {number: .number, title: .title}'
```
