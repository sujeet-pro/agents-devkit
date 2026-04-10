---
name: docs-guidelines
description: "adk - [helper] [docs] Detects the document type being written and loads matching document guidelines — invoked by docs-write and docs-review"
user-invocable: false
argument-hint: "[--type <doc-type>] [--help]"
allowed-tools: [Glob, Grep, Read, Bash]
dependencies:
  commands: [git]
workflow-tier: helper
maturity: stable
---

# Document Writing Guidelines Loader

This skill detects the document type and loads the matching writing guidelines from `${CLAUDE_SKILL_DIR}/references/doc-guidelines/`. Other skills invoke this before writing, reviewing, or fixing documents.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `rfc`, `adr`, `tdd`, `hld`, `lld`, `prd`, `article`, `blog`, `changelog`, `runbook`, etc. | auto-detect | Force a specific document type |

### Behavior Variations

- **Auto-detect** (default): infers document type from calling skill context, user request, or file content
- **`--type <type>`**: overrides auto-detection and loads guidelines for the specified type
- Always loads `general.md` writing guidelines
- For formal documents (RFC, TDD, ADR, HLD, LLD, PRD): also loads `document-metadata.md`
- For research-heavy documents: also loads `research-and-fact-checking.md`
- Falls back to `general.md` only when type cannot be determined

### Examples

```
(invoked automatically by /adk:docs-write, /adk:docs-review)
/adk:docs-guidelines --type rfc
/adk:docs-guidelines --type changelog
/adk:docs-guidelines --type article
```

---



Invoke `/adk:communication` for tone consistency with the invoking skill.


## Workflow

This is a helper skill invoked by other skills, not directly by users. It does not own the workflow — the invoking skill does.

## Document Type Detection

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

## Guideline Loading

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

## Output

Produce a list of guideline file paths to load. The calling skill reads these files and incorporates the guidelines into its writing or review context.

```text
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
