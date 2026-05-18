---
title: 'input-classifiers/github-issue'
description: '```'
source: 'shared/input-classifiers/github-issue.md'
group: 'shared-input-classifiers'
order: 6202
---
# shared/input-classifiers/github-issue

> Source: `shared/input-classifiers/github-issue.md`

# input classifier: GitHub issue URL

## Pattern

```
https?://github.com/<owner>/<repo>/issues/<number>
```

## Fetch via

1. `adk-mcp-github` (preferred).
2. `gh issue view <url> --json …` (fallback).

```bash
gh issue view "$URL" --json number,title,state,body,author,labels,assignees,comments,createdAt,updatedAt,url
```

## Extract into context.md

```markdown
### [github-issue] #<num> — <title>
url: <full URL>
state: open | closed
author: <login>
labels: [bug, frontend, p1]
assignees: [...]
body (first 80 words): <quote>
key comments (last 3 substantive): <quoted ≤15 words each>
linked PRs: [...]
linked Jira: [...]
```

## Hints

- `/adk-implement`: issue body → spec; comments may contain refinement.
- `/adk-review`: link from PR to issue for context.
- `/adk-document --type bug-report`: write up a structured version.
