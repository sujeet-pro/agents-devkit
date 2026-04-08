---
title: "docs-guidelines"
description: Detects the document type being written and loads matching document guidelines
skill_name: docs-guidelines
category: helper
workflow_tier: helper
user_invocable: false
---

# docs-guidelines

Detects the document type and loads the matching writing guidelines from its reference library. Other skills invoke this before writing, reviewing, or fixing documents to ensure type-appropriate quality standards are applied.

## Purpose

- Provide type-specific writing guidelines for document creation and review
- Auto-detect the document type from calling skill context, user request, or file content
- Load the correct combination of general, formal, type-specific, and research guidelines
- Supply a consistent quality baseline across all documentation skills

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--type` | `rfc` \| `adr` \| `tdd` \| `hld` \| `lld` \| `prd` \| `article` \| `blog` \| `changelog` \| `runbook` \| `system-design-article` \| `coding-guidelines-doc` \| `community-guidelines` \| `deep-dive` \| `erd` \| `feedback` \| `appraisal-review` \| `tool-evaluation` \| `api-reference` \| `project` | auto-detect | Force a specific document type |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Auto-detect (default)** | Infers document type from calling skill context, user request, or file content |
| **`--type <type>`** | Overrides auto-detection and loads guidelines for the specified type |
| **Any document** | Always loads `general.md` writing guidelines |
| **Formal documents** (RFC, TDD, ADR, HLD, LLD, PRD) | Also loads `document-metadata.md` for structured metadata rules |
| **Research-heavy documents** (RFC, TDD, HLD, LLD, system-design, tool-evaluation, article, deep-dive) | Also loads `research-and-fact-checking.md` |
| **Unknown type** | Falls back to `general.md` only |

## Document Type Detection

### Keyword / Flag Mapping

| Keyword or Flag | Document Type |
|-----------------|---------------|
| RFC | `rfc` |
| ADR, decision record | `adr` |
| tech-spec, TDD, technical design | `tdd` |
| HLD, high-level design | `hld` |
| LLD, low-level design | `lld` |
| PRD, product requirements | `prd` |
| project, project doc | `project` |
| article, tech article | `article` |
| blog, blog post | `blog` |
| changelog, release notes | `changelog` |
| runbook, playbook | `runbook` |
| system-design | `system-design-article` |
| coding-guidelines | `coding-guidelines-doc` |
| community-guidelines | `community-guidelines` |
| deep-dive | `deep-dive` |
| ERD, entity-relationship | `erd` |
| feedback, review feedback | `feedback` |
| appraisal, performance review | `appraisal-review` |
| tool-evaluation, tool eval | `tool-evaluation` |
| API reference, API docs | `api-reference` |
| onboarding | general (no type-specific file) |
| migration guide | general (no type-specific file) |

## Guideline Loading Rules

### Always Loaded

- `general.md` — applies to every document

### Formal Documents

For structured, formal document types (RFC, TDD, ADR, HLD, LLD, PRD):

- `document-metadata.md` — metadata block standards, versioning, status tracking

### Type-Specific

| Document Type | Guideline File |
|---------------|---------------|
| `rfc` | `rfc.md` |
| `tdd` | `tdd.md` |
| `adr` | `adr.md` |
| `hld` | `hld.md` |
| `lld` | `lld.md` |
| `prd` | `prd.md` |
| `project` | `project.md` |
| `article` | `article.md` |
| `blog` | `blog.md` |
| `changelog` | `changelog.md` |
| `runbook` | `runbook.md` |
| `system-design-article` | `system-design-article.md` |
| `coding-guidelines-doc` | `coding-guidelines-doc.md` |
| `community-guidelines` | `community-guidelines.md` |
| `deep-dive` | `deep-dive.md` |
| `erd` | `erd.md` |
| `feedback` | `feedback.md` |
| `appraisal-review` | `appraisal-review.md` |
| `tool-evaluation` | `tool-evaluation.md` |
| `api-reference` | `api-reference.md` |

### Research-Heavy Documents

For types involving technical claims, vendor comparisons, or data-driven arguments:

- `research-and-fact-checking.md`
- Applies to: RFC, TDD, HLD, LLD, system-design, tool-evaluation, article, deep-dive

## Key Behaviors

- **Layered loading**: always loads general guidelines, then conditionally adds formal metadata, type-specific, and research guidelines
- **Minimal token usage**: only loads the guideline files actually needed for the detected type
- **Fallback-safe**: when the document type cannot be determined, loads `general.md` and lets the calling skill decide
- **No workflow ownership**: this is a helper skill — the invoking skill owns the 6-phase workflow

## Output Format

Produces a list of guideline file paths for the calling skill to load:

```
## Document Guidelines Loaded

Always:
- general.md

Formal:
- document-metadata.md

Type-specific:
- rfc.md

Research:
- research-and-fact-checking.md
```

## Invoked By

| Skill | Context |
|-------|---------|
| `/adk:docs-write` | Before writing any formal or informal document |
| `/adk:docs-review` | Before reviewing documentation for quality |
| `/adk:docs-crud` | When `--type` is set during document creation |

## Examples

```
(invoked automatically by /adk:docs-write, /adk:docs-review, /adk:docs-crud)
/adk:docs-guidelines --type rfc
/adk:docs-guidelines --type changelog
/adk:docs-guidelines --type article
```
