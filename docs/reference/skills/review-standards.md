---
title: "review-standards"
description: Review pipeline, comment templates, and source routing for review skills
skill_name: review-standards
category: guideline
workflow_tier: helper
user_invocable: false
---

# review-standards

End-to-end review pipeline and comment standards used by all review-oriented skills.

## Purpose

Defines the review stages, canonical comment format, severity labels, and postback rules for GitHub/Bitbucket comments.

## Review Pipeline

1. **Intake** — determine review type and source
2. **Source Ingestion** — fetch diff, comments, context; build comment ledger
3. **Parallel Review** — launch review team via `agentic-teams`
4. **Consolidation** — merge findings, deduplicate, assign severity
5. **Output** — format per `output-format` rules
6. **Postback** — post comments to PR platform (if `--publish`)

## Comment Format

Every review comment must answer:
- **What** is the issue?
- **When** does it matter? (always, edge case, at scale)
- **Why** does the standard require this?
- **Fix** — concrete suggestion

## Severity Labels

| Label | Meaning |
|-------|---------|
| Must Fix | Blocking issue |
| Suggestion | Improvement recommendation |
| Note | Informational observation |
| Praise | Positive callout |
| Question | Clarification request |

## Invoked By

All review-oriented skills: `code-review-pr`, `code-review-repo`, `code-review-fix`, `docs-review`, `audit`.
