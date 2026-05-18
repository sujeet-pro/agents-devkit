---
title: 'input-classifiers/github-pr'
description: '```'
source: 'shared/input-classifiers/github-pr.md'
group: 'shared-input-classifiers'
order: 6203
---
# shared/input-classifiers/github-pr

> Source: `shared/input-classifiers/github-pr.md`

# input classifier: GitHub PR URL

## Pattern

```
https?://github.com/<owner>/<repo>/pull/<number>
```

## Fetch via

1. `adk-mcp-github` (preferred) — full PR object + diff.
2. `gh pr view <url> --json …` (fallback).
3. Direct REST with `GITHUB_PAT_CLASSIC` (last resort).

## gh fallback command

```bash
gh pr view "$URL" --json number,title,state,body,author,baseRefName,headRefName,isDraft,mergeable,reviews,reviewRequests,labels,commits,additions,deletions,changedFiles,files,statusCheckRollup,createdAt,updatedAt,url
```

For the diff:

```bash
gh pr diff "$URL"  # or --patch for full patches
```

## Extract into context.md

```markdown
### [github-pr] #<num> — <title>
url: <full URL>
state: open | merged | closed
author: <login>
base ← head: <base>...<head>
draft: yes | no
mergeable: yes | no | conflicting
diff: +<add>/-<del> across <N> files
labels: [...]
status checks: <green / red / pending counts>
reviewers requested: [...]
reviews: <count by state>
key files (top 5 by changes):
  - <path> (+X/-Y)
description (first 80 words): <quote>
linked issues: [...]
linked Jira: [...]
```

## Hints for downstream skills

- `/adk-review`: this is the primary specialized sub-flow (`review-pr`).
- `/adk-implement --fix`: load reviewer comments + apply.
- `/adk-document --type pr-body`: if state=open and body is empty/stale.
- `/adk-investigate`: if PR is implicated in an incident.
