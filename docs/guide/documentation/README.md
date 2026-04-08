---
title: Documentation
description: Create, update, review, and publish engineering documentation
order: 3
---

# Documentation

ADK offers a suite of documentation skills for the full doc lifecycle — creating new documents from templates, updating existing ones, reviewing quality, generating repo docs, and publishing to Confluence. The `docs` router picks the right sub-skill, or invoke each directly.

> **Quick start:** `/adk:docs <describe what you need>` — the router picks the right skill.

## Scenarios

- [Create a new document](#create-a-new-document)
- [Use document templates](#use-document-templates)
- [Update an existing document](#update-an-existing-document)
- [Improve document quality](#improve-document-quality)
- [Write formal engineering docs](#write-formal-engineering-docs)
- [Review documentation](#review-documentation)
- [Generate repository documentation](#generate-repository-documentation)
- [Work with Confluence](#work-with-confluence)
- [Respond to document comments](#respond-to-document-comments)

---

## Create a New Document

Use `docs-crud` with the `create` action to create a document:

```text
/adk:docs-crud create ./docs/api-reference.md
```

### Specify a document type

ADK has built-in templates for common engineering document types. Use `--type` to load the right structure:

```text
/adk:docs-crud create ./docs/decisions/caching-strategy.md --type adr
/adk:docs-crud create ./docs/specs/auth-tdd.md --type tdd
/adk:docs-crud create ./docs/specs/payment-hld.md --type hld
```

Available types: `adr`, `api-reference`, `erd`, `hld`, `incident-report`, `lld`, `onboarding`, `prd`, `project`, `release-notes`, `rfc`, `runbook`, `status-report`, `tdd`.

### Using a custom template

Point to any markdown file as a template:

```text
/adk:docs-crud create ./docs/new-doc.md --template ./templates/team-template.md
```

---

## Use Document Templates

ADK includes templates for 14 document types under `skills/docs-crud/references/doc-templates/`. When you specify `--type`, the matching template is loaded and populated.

| Type | Template | Use When |
|------|----------|----------|
| `adr` | Architecture Decision Record | Recording architectural decisions with context, options, and rationale |
| `rfc` | Request for Comments | Proposing significant changes that need team input |
| `tdd` | Technical Design Document | Detailed technical design for a feature or system |
| `hld` | High-Level Design | Architecture overview for a system or major feature |
| `lld` | Low-Level Design | Detailed module/component design with interfaces and algorithms |
| `prd` | Product Requirements Document | Product requirements with user stories and success metrics |
| `api-reference` | API Reference | REST/GraphQL/RPC API documentation |
| `erd` | Entity Relationship Diagram | Database schema and relationships |
| `runbook` | Operational Runbook | Step-by-step procedures for operations and incidents |
| `incident-report` | Incident Report | Post-incident analysis with timeline and action items |
| `onboarding` | Onboarding Guide | New team member onboarding documentation |
| `release-notes` | Release Notes | Version release notes with changes and migration steps |
| `status-report` | Status Report | Project progress and status updates |
| `project` | Project Document | General project documentation |

---

## Update an Existing Document

Update a document with new information while preserving its structure:

```text
/adk:docs-crud update ./docs/api-reference.md
```

ADK reads the existing document, detects its type, and applies updates while maintaining formatting and structure.

---

## Improve Document Quality

Use `improve` to enhance an existing document without changing its core content:

```text
/adk:docs-crud improve ./docs/architecture/overview.md
```

This fixes grammar, improves clarity, adds missing sections, and enhances formatting.

---

## Write Formal Engineering Documents

For documents that need formal structure and rigorous content, use `docs-write`:

```text
/adk:docs-write --type adr caching strategy decision for the API layer
/adk:docs-write --type rfc migration from REST to gRPC for inter-service communication
/adk:docs-write --type system-design user authentication service technical design
```

### Controlling the audience and tone

```text
/adk:docs-write --type system-design --audience executives --tone formal system architecture overview
/adk:docs-write --type runbook --audience on-call-engineers --tone procedural database failover procedure
```

### Publishing directly

Publish to Confluence during creation:

```text
/adk:docs-write --type adr --publish --publish-space ENG --publish-parent "Architecture Decisions" caching strategy
```

### Output location

```text
/adk:docs-write --type system-design --output-dir ./docs/designs/ payment processing design
```

---

## Review Documentation

Use `docs-review` to analyze documentation quality across multiple dimensions:

```text
/adk:docs-review ./docs/api-reference.md
/adk:docs-review ./docs/architecture/
```

### Focus on specific aspects

```text
/adk:docs-review ./docs/api-reference.md --focus accuracy
/adk:docs-review ./docs/api-reference.md --focus completeness
/adk:docs-review ./docs/api-reference.md --focus clarity
/adk:docs-review ./docs/api-reference.md --focus style
```

### Interactive review

Walk through findings one by one, accepting or rejecting each:

```text
/adk:docs-review ./docs/api-reference.md --mode interactive
```

### Review Confluence pages

```text
/adk:docs-review https://company.atlassian.net/wiki/spaces/ENG/pages/12345
```

---

## Generate Repository Documentation

Use `docs-repo` to auto-generate documentation for an entire repository:

```text
/adk:docs-repo
```

### Initialize documentation structure

```text
/adk:docs-repo --init
```

### Scope to a specific package

```text
/adk:docs-repo --scope package my-library
```

### Format selection

```text
/adk:docs-repo --format pagesmith
/adk:docs-repo --format markdown
```

---

## Work with Confluence

Use `docs-confluence` for Confluence-specific operations:

### Read a Confluence page

```text
/adk:docs-confluence read https://company.atlassian.net/wiki/spaces/ENG/pages/12345
```

### Write to Confluence

```text
/adk:docs-confluence write ./docs/api-reference.md --space ENG --parent "API Documentation"
```

### Sync between local and Confluence

```text
/adk:docs-confluence sync https://company.atlassian.net/wiki/spaces/ENG/pages/12345
```

---

## Respond to Document Comments

When collaborators leave comments on your document:

```text
/adk:docs-crud comment-reply ./docs/api-reference.md
```

This reads comments (from Confluence or inline), generates responses, and optionally applies suggested changes.

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Create a doc from template | `docs-crud` | `create`, `--type`, `--template` |
| Update existing doc | `docs-crud` | `update` |
| Improve doc quality | `docs-crud` | `improve` |
| Reply to doc comments | `docs-crud` | `comment-reply` |
| Write formal engineering doc | `docs-write` | `--type`, `--audience`, `--publish` |
| Review doc quality | `docs-review` | `--focus`, `--mode interactive` |
| Generate repo docs | `docs-repo` | `--init`, `--scope`, `--format` |
| Read/write Confluence | `docs-confluence` | `read/write/sync`, `--space` |

## Related Skills

- **[`spec`](/reference/skill-spec/)** — write specifications (a specialized form of documentation)
- **[`diagram`](/reference/skill-diagram/)** — create diagrams to include in docs
- **[`research`](/reference/skill-research/)** — research a topic before documenting it
