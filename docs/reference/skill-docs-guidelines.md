---
title: 'docs-guidelines'
description: 'Detects the document type being written and loads matching document guidelines — invoked by docs-write and docs-review'
skill_name: docs-guidelines
category: guideline
workflow_tier: helper
user_invocable: false
---

# docs-guidelines

`docs-guidelines` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`docs-guidelines` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `rfc`, `adr`, `tdd`, `hld`, `lld`, `prd`, `article`, `blog`, `changelog`, `runbook`, etc. | auto-detect | Force a specific document type |

### Parameter Notes

- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.

## How It Works

Helper skills do not usually own the top-level conversation. The calling skill decides when to load them, passes just enough context to resolve the right rules or references, and then consumes the returned guidance inside its own execution flow.

The important developer contract is therefore: when the helper is loaded, what context it reads, what rules or artifacts it returns, and how that changes the calling skill's behavior.

### Workflow

This is a helper skill invoked by other skills, not directly by users. It does not own the workflow — the invoking skill does.

### Guideline Loading

### Always Load

These apply to every document:

- `${CLAUDE_SKILL_DIR}/references/doc-guidelines/general.md`

### Formal Documents

For structured, formal document types (RFC, TDD, ADR, HLD, LLD, PRD), also load:

- `${CLAUDE_SKILL_DIR}/references/doc-guidelines/document-metadata.md`

### Type-Specific

Load the guideline matching the detected document type:

| Document Type | Guideline File |
|---------------|---------------|
| rfc | `rfc.md` |
| tdd | `tdd.md` |
| adr | `adr.md` |
| hld | `hld.md` |
| lld | `lld.md` |
| prd | `prd.md` |
| project | `project.md` |
| article | `article.md` |
| blog | `blog.md` |
| changelog | `changelog.md` |
| runbook | `runbook.md` |
| system-design-article | `system-design-article.md` |
| coding-guidelines-doc | `coding-guidelines-doc.md` |
| community-guidelines | `community-guidelines.md` |
| deep-dive | `deep-dive.md` |
| erd | `erd.md` |
| feedback | `feedback.md` |
| appraisal-review | `appraisal-review.md` |
| tool-evaluation | `tool-evaluation.md` |
| api-reference | `api-reference.md` |
| incident-report | `${CLAUDE_SKILL_DIR}/references/doc-guidelines/incident-report.md` |
| release-notes | `${CLAUDE_SKILL_DIR}/references/doc-guidelines/release-notes.md` |
| status-report | `${CLAUDE_SKILL_DIR}/references/doc-guidelines/status-report.md` |

### Research-Heavy Documents

For document types that involve technical claims, vendor comparisons, or data-driven arguments, also load:

- `${CLAUDE_SKILL_DIR}/references/doc-guidelines/research-and-fact-checking.md`

Applies to: RFC, TDD, HLD, LLD, system-design, tool-evaluation, article, deep-dive, and any document the calling skill flags as research-heavy.

## Modes & Variations

Most helpers do not have end-user modes in the same sense as task skills, but they still vary by scope, invoking context, selected family, or fallback behavior.


### Behavior Variations

- **Auto-detect** (default): infers document type from calling skill context, user request, or file content
- **`--type <type>`**: overrides auto-detection and loads guidelines for the specified type
- Always loads `general.md` writing guidelines
- For formal documents (RFC, TDD, ADR, HLD, LLD, PRD): also loads `document-metadata.md`
- For research-heavy documents: also loads `research-and-fact-checking.md`
- Falls back to `general.md` only when type cannot be determined

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


### Output

Produce a list of guideline file paths to load. The calling skill reads these files and incorporates the guidelines into its writing or review context.

```text

## Additional Reference

### Document Type Detection

Determine the document type from the calling skill's context, the user's request, or the target file's content.

### Keyword / Flag Mapping

| Keyword or Flag | Document Type |
|-----------------|---------------|
| RFC | rfc |
| ADR, decision record | adr |
| tech-spec, TDD, technical design | tdd |
| HLD, high-level design | hld |
| LLD, low-level design | lld |
| PRD, product requirements | prd |
| project, project doc | project |
| article, tech article | article |
| blog, blog post | blog |
| changelog, release notes | changelog |
| runbook, playbook | runbook |
| system-design | system-design-article |
| coding-guidelines | coding-guidelines-doc |
| community-guidelines | community-guidelines |
| deep-dive | deep-dive |
| ERD, entity-relationship | erd |
| feedback, review feedback | feedback |
| appraisal, performance review | appraisal-review |
| tool-evaluation, tool eval | tool-evaluation |
| API reference, API docs | api-reference |
| onboarding | general (no type-specific file) |
| migration guide | general (no type-specific file) |

### Fallback

When the document type cannot be determined, load only `general.md` and let the calling skill decide.

### Document Guidelines Loaded

Always:
- general.md

Formal:
- document-metadata.md

Type-specific:
- rfc.md

Research:
- research-and-fact-checking.md
```

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
(invoked automatically by /adk:docs-write, /adk:docs-review)
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:docs-guidelines --type rfc
/adk:docs-guidelines --type changelog
/adk:docs-guidelines --type article
```
