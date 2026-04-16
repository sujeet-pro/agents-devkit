---
title: Code Reviews
description: Review PRs, fix comments, and self-review local changes before merge
order: 1
---

# Code Reviews

Review PRs, fix comments, and self-review local changes before merge.

> **Quick start:** `/adk-review-pr` is the simplest entrypoint for this category.

## Included Skills

| Skill | Purpose | Reference |
| --- | --- | --- |
| `/adk-review-pr` | Review a pull request for correctness, regression risk, and missing validation. Use when reviewing a branch or hosted pull request before merge | [Details](../../reference/skill-adk-review-pr.md) |
| `/adk-review-local-changes` | Review local uncommitted or local branch changes before commit or PR. Use when the work exists locally and needs a pre-submit review | [Details](../../reference/skill-adk-review-local-changes.md) |
| `/adk-address-review-feedback` | Fix review feedback, update the code, and confirm the comments are addressed. Use when a PR or local review already produced actionable feedback | [Details](../../reference/skill-adk-address-review-feedback.md) |

## Example Invocations

```text
/adk-review-pr <branch-name>
/adk-review-local-changes
/adk-address-review-feedback <source>
```

## How To Use This Guide

Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.
