---
title: "docs-write"
description: Create or update formal engineering documents — auto-detects type, loads the right stage, optional Confluence/Google Docs publishing
skill_name: docs-write
category: task
workflow_tier: full
user_invocable: true
---

# docs-write

Single entry point for formal engineering document creation. Auto-detects the document type from the prompt or an explicit `--type` flag, loads the matching stage file for type-specific guidance, and runs the Standard Task workflow (confirm → research → execute → validate). Supports publishing to Confluence or Google Docs.

## When to Use

- Write a formal engineering document (ADR, RFC, TDD, HLD, LLD, PRD, runbook, etc.)
- Create a blog post, changelog, article, or tech radar entry
- Publish a local markdown document to Confluence or Google Docs
- Fix review comments on an existing document
- Write using a custom template from a local file or URL

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<topic>` | text | required | The subject or title of the document |
| `--type` | `adr` \| `rfc` \| `api` \| `blog` \| `article` \| `changelog` \| `runbook` \| `migration` \| `onboarding` \| `project` \| `proposal` \| `system-design` \| `tech-radar` \| `tool-eval` \| `fix` \| `general` | auto-detect | Explicit document type. HLD and LLD are sections within `system-design`. PRD maps to `proposal` |
| `--format` | `markdown` \| `confluence` \| `google-doc` \| `pdf` | `markdown` | Output format |
| `--publish` | `markdown` \| `source` \| `both` | `markdown` | Publish target. `source` publishes to Confluence/Google Docs; `both` writes local file and publishes |
| `--publish-space` | space key | none | Confluence space key (required when `--publish` includes `source`) |
| `--publish-parent` | page title or ID | space root | Parent page in Confluence |
| `--publish-update` | page ID | none | Confluence page ID to update in-place instead of creating new |
| `--publish-title` | text | document H1 | Override the published page title |
| `--output-dir` | directory path | current directory | Directory for the output file |
| `--frontmatter` | `yes` \| `no` | `yes` for formal docs | Include YAML frontmatter |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--audience` | text | none | Target audience (e.g., `senior-engineers`, `new-hires`, `external`) |
| `--tone` | text | none | Writing tone (e.g., `formal`, `conversational`, `technical`) |
| `--depth` | text | none | Content depth (e.g., `overview`, `detailed`, `comprehensive`) |
| `--weight` | `lightweight` \| `heavyweight` | none | For system-design documents |
| `--template` | path or URL | none | Template document. Supports local markdown, Confluence URLs, Google Doc URLs |
| `--auto-apply` | flag | off | For doc-fix: skip interactive loop and apply all fixes directly |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **New document** | Full 6-phase workflow. Creates the document from scratch |
| **Revise existing** | Reads existing content, proposes targeted edits |
| **Fix comments** (`--type fix`) | Abbreviated workflow. Reads review comments, proposes fixes, applies after approval |
| **Publish only** (`--publish source` with existing file) | Converts and publishes an existing markdown file without rewriting |
| **Write and publish** (`--publish both`) | Full writing workflow followed by publishing to the target platform |
| **Template-based** (`--template`) | Reads the template, extracts structure (headings, placeholders, tables), generates content to match |
| **Formal doc types** (RFC, ADR, TDD/system-design) | Loads document-metadata guidelines and formal structure templates with YAML frontmatter |
| **Informal doc types** (article, blog, runbook) | Lighter structure, narrative-focused |

## Stage Selection

The skill selects a stage file based on `--type` or keyword detection from the prompt:

| Keywords / Type Flag | Stage | Description |
|---|---|---|
| ADR, architecture decision | `adr` | Architecture Decision Record |
| RFC, request for comments | `rfc` | Request for Comments |
| API docs, endpoint reference | `api-docs` | API reference documentation |
| Blog, release notes, announcement | `blog` | Blog post or announcement |
| Article, deep dive, technical writing | `article` | Deep technical article |
| Changelog, release history | `changelog` | Changelog from git history |
| Runbook, incident response, ops guide | `runbook` | Operational runbook |
| Migration guide, upgrade path | `migration-guide` | Migration or upgrade guide |
| Onboarding, new hire guide | `onboarding` | Onboarding guide |
| Project docs, README, setup guide | `project-docs` | Project documentation |
| Proposal, PRD | `proposal` | Decision proposal or PRD |
| System design, tech spec, TDD, HLD, LLD | `system-design` | Tech Spec / Technical Design Document |
| Tech radar | `tech-radar` | Technology radar |
| Tool evaluation, comparison | `tool-eval` | Tool/technology evaluation |
| Fix existing docs | `doc-fix` | Fix review comments on docs |
| Generic or unclear | `general` | General document writing |

**Type aliases**: HLD and LLD are sections within a Tech Spec, not separate document types. PRD maps to the `proposal` stage.

## Key Behaviors

- **Auto-detection**: infers document type from prompt keywords when `--type` is not set
- **Type aliases**: HLD/LLD map to `system-design`; PRD maps to `proposal`
- **Template merging**: when both `--template` and `--type` are set, uses the template for structure and the stage file for quality rules
- **Confluence publish pipeline**: parallel child agents for markdown conversion, attachment upload, and page review
- **Diagram and chart integration**: invokes `/adk:diagram` and `/adk:chart` when the document needs visual aids
- **Code-aware writing**: inspects the repository before describing code or architecture

## Workflow

Follows the Standard Task workflow (confirm → research → execute → validate). The `doc-fix` stage uses abbreviated Quick Action workflow (confirm → execute → verify).

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, assumptions, tools, and success criteria |
| 1. Research & Options | yes | Research topic, scan related docs and code |
| 2. Approach Selection | skipped | Standard Task workflow proceeds directly to execution |
| 3. Planning | skipped | Standard Task workflow proceeds directly to execution |
| 4. Execute | yes | Write document using child agents for research, writing, fact-checking |
| 5. Validate & Learn | yes | Self-review for accuracy, completeness, readability, guidelines compliance |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | Standard Task: confirm → research → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct writing roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `chart` | doc needs data charts | Generate data charts from CSV/JSON data |
| `coding` | doc describes code or architecture | Detect repo stack, load coding guidelines |
| `diagram` | doc needs diagrams | Auto-detect best diagram engine and render |

## Output Format

All output is markdown by default. Structure varies by document type (see stage files). Supports markdown, Confluence, Google Docs, and PDF as output targets.

Every document includes:

- Document structure matching the selected type
- YAML frontmatter for formal document types
- Diagrams and charts rendered as embedded images
- Cross-references to related documents
- Source attribution and research citations

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:docs-review` | Comment-only review of documents (no source edits) |
| `/adk:docs-crud` | Template-driven CRUD for 14 built-in doc types |
| `/adk:diagram` | Standalone architecture diagrams |
| `/adk:chart` | Standalone data charts |
| `/adk:coding` | Coding guidelines detection |
| `/adk:docs-guidelines` | Document writing guidelines |

## Examples

```
/adk:docs-write "Authentication service migration to OAuth2" --type rfc
/adk:docs-write "ADR for choosing PostgreSQL over DynamoDB"
/adk:docs-write changelog --since v2.1.0
/adk:docs-write runbook "Incident response for payment service"
/adk:docs-write "API reference for user service" --type api --format confluence
/adk:docs-write --type fix https://docs.google.com/document/d/abc123
/adk:docs-write "New hire onboarding guide" --audience new-hires --depth comprehensive
/adk:docs-write "Q1 Architecture Review" --publish both --publish-space ENG
/adk:docs-write "Cache Strategy" --type system-design --verbosity detailed --output-dir docs/
/adk:docs-write docs/architecture.md --publish source --publish-space ENG --publish-parent "RFCs"
/adk:docs-write docs/runbook.md --publish source --publish-space OPS --publish-title "Deploy Runbook v2"
/adk:docs-write docs/design.md --publish source --publish-space ENG --publish-update 12345
/adk:docs-write "Onboarding guide" --template docs/templates/onboarding-template.md
/adk:docs-write "Q2 RFC" --template https://company.atlassian.net/wiki/spaces/ENG/pages/99999
```
