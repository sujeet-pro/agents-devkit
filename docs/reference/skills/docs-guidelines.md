---
title: "docs-guidelines"
description: Detects document type and loads matching writing guidelines
skill_name: docs-guidelines
category: guideline
workflow_tier: helper
user_invocable: false
---

# docs-guidelines

Detects the type of document being written and loads the matching writing guidelines from a shared library of 24 guideline files.

## Purpose

Provides document-type-specific writing standards. Ensures RFCs read like RFCs, runbooks follow operational conventions, etc.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `rfc`, `adr`, `tdd`, `hld`, `lld`, `prd`, `runbook`, `api-reference`, `incident-report`, `onboarding`, `release-notes`, `status-report`, `erd`, `project`, `blog`, `changelog` | auto-detect | Document type |

## Guidelines Loaded

Always loads `general.md`. Conditionally loads:
- Formal docs add `document-metadata.md`
- Research-heavy types add `research-and-fact-checking.md`
- Type-specific files (e.g., `rfc.md`, `adr.md`, `runbook.md`)

## Output

Produces a "Document Guidelines Loaded" list for the parent skill to consume.

## Invoked By

`docs-write`, `docs-review`, `docs-crud`, `spec`.
