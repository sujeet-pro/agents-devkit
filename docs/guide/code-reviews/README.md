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
| `/adk-review-pr` | Review a remote pull request with severity-tiered findings, evidence per finding, and posted-back comments via the appropriate provider (GitHub, Bitbucket). Use when a PR URL is the target and the deliverable is a structured review (findings + optional posted comments). Do not use for local uncommitted changes (use adk-review-local), addressing existing reviewer feedback (use adk-review-feedback), or auditing the whole repo (use adk-audit-repo) | [Details](../../reference/skill-adk-review-pr.md) |

## Example Invocations

```text
/adk-review-pr
```

## How To Use This Guide

Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.
