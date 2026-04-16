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
| `/adk-audit-repo` | Audit a repository for correctness risks, maintainability issues, and validation gaps. Use when you need a prioritized improvement list instead of a line-by-line PR review | [Details](../../reference/skill-adk-audit-repo.md) |
| `/adk-audit-site` | Audit a live site or webapp for SEO, performance, accessibility, security signals, metadata, and broken-user-flow issues. Use when the job is site health rather than repo health | [Details](../../reference/skill-adk-audit-site.md) |
| `/adk-test` | Verify behavior through acceptance, regression, or webapp-focused testing with explicit pass criteria and fresh evidence. Use when validation itself is the main task | [Details](../../reference/skill-adk-test.md) |

## Example Invocations

```text
/adk-audit-repo
/adk-audit-site <url>
/adk-test <target>
```

## How To Use This Guide

Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.
