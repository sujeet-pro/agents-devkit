---
title: Guidelines Reference
description: Coding, documentation, and architecture guidelines auto-loaded by skills
order: 4
---

# Guidelines Reference

Skills automatically load relevant guidelines based on repository type and task context. Guidelines are lazy-loaded — only the files matching the detected stack or document type are read.

## Coding Guidelines

**Location:** `skills/coding/references/coding-guidelines/`

16 guideline files covering different aspects of software development. The `/adk:coding` skill detects the repo's tech stack and loads only the relevant files.

| Guideline | Focus |
|-----------|-------|
| `general.md` | Universal coding principles |
| `architecture.md` | Architecture patterns and boundaries |
| `frontend.md` | Frontend-specific patterns (React, Vue, etc.) |
| `backend-java.md` | Java backend patterns |
| `backend-kotlin.md` | Kotlin backend patterns |
| `backend-nodejs.md` | Node.js backend patterns |
| `backend-python.md` | Python backend patterns |
| `design-system.md` | Design system and component library patterns |
| `js-ts-library.md` | JavaScript/TypeScript library patterns |
| `scripts.md` | Script and automation patterns |
| `api-design.md` | API design and REST/GraphQL conventions |
| `testing.md` | Testing strategy and patterns |
| `observability.md` | Logging, metrics, and tracing |
| `security.md` | Security practices and vulnerability prevention |
| `expressive-code.md` | Code readability and expressiveness |

## Document Guidelines

**Location:** `skills/docs-guidelines/references/doc-guidelines/`

24 guideline files for different document types. The `/adk:docs-guidelines` skill detects the document type and loads the matching guidelines.

| Guideline | Focus |
|-----------|-------|
| `general.md` | Universal documentation principles |
| `rfc.md` | Request for Comments format |
| `adr.md` | Architecture Decision Records |
| `article.md` | Technical articles |
| `blog.md` | Blog post writing |
| `changelog.md` | Changelog and release notes |
| `runbook.md` | Operational runbooks |
| `system-design.md` | System design documents |
| `tool-evaluation.md` | Tool/technology evaluations |
| `research.md` | Research documents |
| `deep-dive.md` | Deep-dive technical analysis |
| ... and 13 more specialized formats |

## Architecture Guidelines

**Location:** `skills/architecture/`

The `/adk:architecture` skill provides patterns, principles, and anti-pattern detection for different architecture types:

- **Frontend architecture** — component hierarchy, state management, routing, rendering strategies
- **Backend architecture** — service boundaries, data flow, API design, scaling patterns
- **Fullstack architecture** — end-to-end patterns, BFF, shared types, deployment
- **Infrastructure architecture** — cloud patterns, containerization, CI/CD, observability

## How Guidelines Are Used

1. **Task skills** (e.g., `code-review-pr`, `dev-build`) invoke guideline skills during execution
2. The guideline skill **detects context** (repo stack, doc type, architecture pattern)
3. Only the **matching guideline files** are loaded (e.g., Python backend + testing, not all 16)
4. If the guideline skill is **not installed**, the task skill falls back to its one-line inline summary

This lazy-loading approach keeps token usage low while providing deep, relevant guidance for each task.
