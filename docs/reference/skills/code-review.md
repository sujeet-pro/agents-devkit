---
title: "code-review"
description: Code review router — detects review type and routes to the right sub-skill
skill_name: code-review
category: routing
workflow_tier: orchestrator
---

# code-review

Router that detects the type of code review needed and forwards to the correct sub-skill. Does not perform review work itself.

## Routing Rules

| Signal | Routes To |
|--------|-----------|
| PR URL (GitHub/Bitbucket) | `code-review-pr` |
| "fix", "address", "resolve comments" | `code-review-fix` |
| "repo", "codebase", "whole repository" | `code-review-repo` |
| Ambiguous | Asks the user to clarify |

## Parameters

All parameters are forwarded to the target skill.

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<target>` | PR URL, description, or empty | — | Review target |
| `--help` | flag | — | Show routing rules |

## Examples

```text
/adk:code-review https://github.com/org/repo/pull/42
/adk:code-review fix the comments on my PR
/adk:code-review review this repository
```

## Sub-Skills

- [`code-review-pr`](./code-review-pr.md) — PR, local, or branch review
- [`code-review-repo`](./code-review-repo.md) — Whole-repository review
- [`code-review-fix`](./code-review-fix.md) — Fix PR review comments
