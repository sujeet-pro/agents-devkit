---
title: Audits & Quality
description: Run repository audits, live site audits, and explicit testing workflows
order: 6
---

# Audits & Quality

Run repository audits, live site audits, and explicit testing workflows.

> **Quick start:** `/adk-audit-repo` is the simplest entrypoint for this category.

## Included Skills

| Skill | Purpose | Reference |
| --- | --- | --- |
| `/adk-audit-repo` | Audit a code repository across security, performance, code quality, dependencies, test coverage, and architecture - producing a single severity-tiered report with file-anchored evidence per finding. Use when the deliverable is a multi-dimensional health report on a checked-out repo, not a single-PR review or a doc review. Do not use to audit a deployed website (use adk-audit-site) or to fix the issues found (use adk-build-* skills) | [Details](../../reference/skill-adk-audit-repo.md) |
| `/adk-audit-site` | Audit a publicly reachable website or web app across performance, accessibility, SEO, UX, and basic security headers - producing a single severity-tiered report with URL/selector evidence per finding. Use when the deliverable is a multi-dimensional health report on a deployed site, not a code repo. Do not use to audit a checked-out repo (use adk-audit-repo) or to fix the issues found (use adk-build-* / adk-frontend-* skills) | [Details](../../reference/skill-adk-audit-site.md) |

## Example Invocations

```text
/adk-audit-repo
/adk-audit-site
```

## How To Use This Guide

Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.
