---
title: Documentation
description: Create, update, review, and publish engineering documentation
order: 3
---

# Documentation

Start with the `docs` router when you want ADK to choose the documentation workflow, then move to the specific skill once you know whether the job is page lifecycle work, formal document authoring, review, repository docs, or Confluence sync.

> **Quick start:** `/adk:docs <prompt-text>` is the simplest way to tell ADK what documentation outcome you want and let it choose the right skill.

## Scenarios

- [Create Or Update A Page](#create-or-update-a-page)
- [Write A Formal Engineering Document](#write-a-formal-engineering-document)
- [Review Documentation Quality](#review-documentation-quality)
- [Generate Repository Documentation](#generate-repository-documentation)
- [Work With Confluence](#work-with-confluence)

---

## Create Or Update A Page

Use `docs-crud` when the job is the lifecycle of one page or one document target: create it, refresh it, improve it, or reply to comments on it.

```text
/adk:docs-crud <action> <path>
/adk:docs-crud create <path> --type adr
/adk:docs-crud create docs/decisions/caching-strategy.md --type adr
/adk:docs-crud update <path>
/adk:docs-crud improve <path>
/adk:docs-crud comment-reply <path>
```

Use `--type` when you want one of the built-in document skeletons. Use `update` when the source-of-truth has changed, `improve` when the content is mostly right but not easy enough to read, and `comment-reply` when the review queue is the real input.

---

## Write A Formal Engineering Document

Use `docs-write` when the output needs to be a durable engineering artifact such as an ADR, RFC, runbook, system design, or similar formal document.

```text
/adk:docs-write --type adr <prompt-text>
/adk:docs-write --type runbook <prompt-text>
/adk:docs-write --audience executives --type system-design <prompt-text>
/adk:docs-write --publish both --publish-space <name> --publish-parent <name> --type adr <prompt-text>
/adk:docs-write --output-dir <path> --type system-design <prompt-text>
```

`--type` controls the document family, `--audience` helps ADK tune depth and tone, and the publish flags are for cases where the destination is Confluence rather than a local markdown file.

---

## Review Documentation Quality

Use `docs-review` when you want findings first instead of edits first.

```text
/adk:docs-review <path>
/adk:docs-review ./docs/api-reference.md
/adk:docs-review <path> --focus accuracy
/adk:docs-review <path> --mode interactive
```

Start with the plain file or directory path, then add `--focus` when you care most about one dimension such as accuracy or completeness. Interactive mode is the best fit when you want to triage findings as you go.

---

## Generate Repository Documentation

Use `docs-repo` when the target is the repository as a whole rather than one page.

```text
/adk:docs-repo
/adk:docs-repo --init
/adk:docs-repo --scope package <name>
/adk:docs-repo --format pagesmith
```

`--init` bootstraps the doc structure, `--scope` narrows generation to a package, and `--format` lets you choose the target doc system.

---

## Work With Confluence

Use `docs-confluence` when the source or destination is Confluence and you want a skill that understands that platform directly.

```text
/adk:docs-confluence read <url>
/adk:docs-confluence write <path> --space <name> --parent <name>
/adk:docs-confluence sync <url>
```

This is the right path when the local markdown flow is not enough and the important part of the job is platform-aware publishing or synchronization.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the documentation path | `docs` | `<prompt-text>` |
| Create, update, improve, or reply on one page | `docs-crud` | `<action>`, `<path>`, `--type` |
| Write a formal engineering document | `docs-write` | `--type`, `--audience`, `--publish`, `--output-dir` |
| Review docs without editing | `docs-review` | `<path>`, `--focus`, `--mode` |
| Generate repo docs | `docs-repo` | `--init`, `--scope`, `--format` |
| Read, write, or sync Confluence content | `docs-confluence` | `read|write|sync`, `--space`, `--parent` |

## Related Skills

- **[`spec`](/reference/skill-spec/)** when the missing artifact is a formal specification rather than general documentation.
- **[`diagram`](/reference/skill-diagram/)** when the document needs diagrams as part of the explanation.
- **[`research`](/reference/skill-research/)** when the document needs cited source material before it can be written well.
