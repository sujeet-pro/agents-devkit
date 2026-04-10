---
title: 'docs-write'
description: 'Create or update formal engineering documents — auto-detects type, loads the right stage, optional Confluence/Google Docs publishing'
skill_name: docs-write
category: task
workflow_tier: full
user_invocable: true
---

# docs-write

Use `docs-write` to create or update formal engineering documents — auto-detects type, loads the right stage, optional Confluence/Google Docs publishing. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`docs-write` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `<topic>` | Required. The subject or title of the document. |
| `--type` | Explicit document type. One of: `adr`, `rfc`, `api`, `blog`, `article`, `changelog`, `runbook`, `migration`, `onboarding`, `project`, `proposal`, `system-design`, `tech-radar`, `tool-eval`, `fix`, `general`. If omitted, auto-detected from keywords. HLD and LLD are sections within `system-design`, not separate types -- use `--type system-design` for those. PRD maps to `proposal`. |
| `--format` | Output format: `markdown` (default), `confluence`, `google-doc`, `pdf`. |
| `--publish` | Publish target: `markdown` (local file only, default), `source` (publish to Confluence/Google Docs), `both` (local file + publish). |
| `--publish-space` | Confluence space key for publishing (e.g., `ENG`, `OPS`). Required when `--publish` includes `source`. |
| `--publish-parent` | Parent page title or ID in Confluence. Defaults to space root. |
| `--publish-update` | Confluence page ID to update in-place instead of creating a new page. |
| `--publish-title` | Override the published page title (defaults to document H1). |
| `--output-dir` | Directory path for the output file (defaults to current directory or type-specific location). |
| `--frontmatter` | Include YAML frontmatter: `yes` (default for formal docs like ADR/RFC/TDD), `no`. |
| `--verbosity` | Output verbosity: `short`, `standard` (default), `detailed`. |
| `--audience` | Target audience (e.g., `senior-engineers`, `new-hires`, `external`). |
| `--tone` | Writing tone (e.g., `formal`, `conversational`, `technical`). |
| `--depth` | Content depth (e.g., `overview`, `detailed`, `comprehensive`). |
| `--weight` | For system-design: `lightweight` or `heavyweight`. |
| `--template` | Path or URL to a template document. The output follows the template's structure, headings, and placeholders. Supports local markdown files, Confluence page URLs, and Google Doc URLs. |
| `--auto-apply` | For doc-fix: skip interactive loop and apply all fixes directly. |
| `--help` | Show this help section and exit. |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--publish` adds a delivery step after generation so the result ends up in an external document destination.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |
| `/adk:chart` | when doc needs data charts | Generate data charts (bar, line, pie, scatter, etc.) from CSV/JSON data. Render to SVG/PNG for embedding in documents. |
| `/adk:coding` | when doc describes code or architecture | Detect repo languages, frameworks, and tools. Load matching coding guidelines for accurate technical writing. |
| `/adk:docs-guidelines` | when writing any doc type | Load doc-type-specific writing guidelines (ADR, RFC, runbook, etc.). |
| `/adk:confluence` | when publishing to Confluence | Auth validation, page CRUD, space operations. Inline: check CONFLUENCE_* env vars, use curl/jq scripts. |
| `/adk:docs-md` | when writing markdown | Markdown formatting: headings, lists, code blocks, tables, links. |
| `/adk:diagram` | when doc needs diagrams | Auto-detect best diagram engine (Mermaid, Excalidraw, draw.io, Graphviz) and route to the matching diagram skill. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

Before research, drafting, revision, or publishing setup, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team:

- For Confluence (`--publish source` or `--format confluence`): verify access via `mcp__atlassian-confluence__confluence_search` or `mcp__plugin-adk-atlassian__confluence_search` with the space key. If `--publish-update` is provided, verify the page exists via `mcp__atlassian-confluence__confluence_get_page` or `mcp__plugin-adk-atlassian__confluence_get_page`.
- For Google Docs (`--format google-doc`): verify Google Drive MCP connectivity.

If the document needs diagrams, inherit the `/adk:diagram` preflight before rendering assets.

### Guideline Loading

Invoke the `/adk:coding` helper skill to detect the repo stack and load the appropriate coding guidelines when the document describes real code or architecture.

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **New document**: Standard Task workflow. Creates the document from scratch.
- **Revise existing**: Reads existing content, proposes targeted edits.
- **Fix comments** (`--type fix`): Uses Quick Action workflow (confirm → execute → verify) for this mode. Reads review comments, proposes fixes, applies after approval.
- **Publish only** (`--publish source` with an existing file): Converts and publishes an existing markdown file to Confluence or Google Docs without rewriting.
- **Write and publish** (`--publish both`): Full writing workflow followed by publishing to the target platform.
- **Template-based** (`--template <path-or-url>`): Reads the template, extracts its structure (headings, sections, placeholders), and generates the document to match. The user can edit sections during Phase 4 via an interactive approval loop.
- **Formal doc types** (RFC, ADR, TDD/system-design): Loads document-metadata guidelines and formal structure templates with YAML frontmatter.
- **Informal doc types** (article, blog, runbook): Lighter structure, narrative-focused.

### Stage Selection

Classify by explicit `--type` flag first. If absent, detect from keywords in the prompt.

| Keywords / Type Flag | Stage File | Description |
|---|---|---|
| ADR, architecture decision | `stages/adr.md` | Architecture Decision Record |
| RFC, request for comments | `stages/rfc.md` | Request for Comments |
| API docs, endpoint reference | `stages/api-docs.md` | API reference documentation |
| Blog, release notes, announcement | `stages/blog.md` | Blog post or announcement |
| Article, deep dive, technical writing | `stages/article.md` | Deep technical article |
| Changelog, release history | `stages/changelog.md` | Changelog from git history |
| Runbook, incident response, ops guide | `stages/runbook.md` | Operational runbook |
| Migration guide, upgrade path | `stages/migration-guide.md` | Migration or upgrade guide |
| Onboarding, new hire guide | `stages/onboarding.md` | Onboarding guide |
| Project docs, README, setup guide | `stages/project-docs.md` | Project documentation |
| Proposal, PRD | `stages/proposal.md` | Decision proposal or Product Requirements Document |
| System design, tech spec, TDD, HLD, LLD | `stages/system-design.md` | Tech Spec / Technical Design Document |
| Tech radar | `stages/tech-radar.md` | Technology radar |
| Tool evaluation, comparison | `stages/tool-eval.md` | Tool/technology evaluation |
| Fix existing docs, typo, correction | `stages/doc-fix.md` | Fix review comments on docs |
| Generic or unclear | `stages/general.md` | General document writing |

**Type aliases**: HLD and LLD are sections within a Tech Spec, not separate document types. If the user requests an HLD or LLD, route to the `system-design` stage. PRD maps to the `proposal` stage.

**Disambiguation**: If multiple types match, prefer the more specific type. When genuinely ambiguous, ask the user to clarify before proceeding. If the user says "write" without enough context to classify, default to `general`.

**Load the selected stage file** before proceeding to Phase 1. The stage file contains the document structure, type-specific phase guidance, output format, and child agent team composition for that document type.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

All output is markdown by default. Structure varies by document type -- see the loaded stage file for the exact format. Support markdown, Confluence, Google Docs, and PDF as output targets (see `/adk:output-format`).

## Related Skills

### Adjacent Skills

- `/adk:docs-review` for comment-only review of documents (no source edits)
- `/adk:diagram` for standalone architecture diagrams
- `/adk:chart` for data charts (bar, line, pie, scatter, etc.) to embed in documents
- `/adk:coding` for coding guidelines detection
- `/adk:docs-guidelines` for document writing guidelines
- `/adk:docs-crud` for template-driven document creation with 14 built-in doc types

## Additional Reference

### Template Handling

When `--template` is provided, read the template before Phase 1 and use it as the structural backbone:

1. **Read the template** — local file via `Read`, Confluence page via MCP or API, Google Doc via MCP.
2. **Extract structure** — headings, section order, placeholder text (e.g. `[TODO: ...]`, `<describe ...>`), tables, and boilerplate.
3. **Merge with type guidance** — if `--type` is also set, use the stage file for content quality rules but the template for structure. If `--type` is not set, infer the type from the template's structure.
4. **Generate section-by-section** — during Phase 4, produce each section following the template's layout. Present each completed section to the user for review before proceeding to the next.
5. **Preserve boilerplate** — keep any template content that is not a placeholder (legal disclaimers, standard headers, org-specific formatting).

Template sources:
- **Local path**: read the file directly.
- **Confluence URL**: read via `mcp__atlassian-confluence__confluence_get_page` or API fallback.
- **Google Docs URL**: read via `mcp__google-drive__getDocument` or API fallback.

### Common Workflow

### 1. Confirm

- restate the document goal, audience, and deliverable
- surface assumptions, source requirements, and publishing constraints
- identify which helpers or connectors are needed
- get approval early before deep research or drafting

### 2. Research

- research the topic using official docs, existing repo content, and relevant source material
- scan for existing documents, patterns, and conventions in the repo
- identify constraints, dependencies, and integration points
- end with 2-3 viable approaches when structure, scope, or publishing strategy is not obvious

### 3. Execute

- write or revise the document using the child agent team from the loaded stage file
- follow type-specific execution guidance from the stage file
- update progress when the work spans multiple checkpoints or publishing steps

### 4. Validate

- run an internal review loop with the doc-review team
- verify accuracy, completeness, readability, and guideline compliance
- fix all critical issues that block handoff
- end with a concise summary of what changed, what was validated, and what the reader should understand

### Default Child Agent Team

Unless the stage file specifies a different composition, run at least these child agents in parallel:

- `adk-doc-writer` for document drafting and content generation
- `adk-research-agent` for official docs, standards, and migration notes
- `adk-code-snippet-agent` for examples grounded in the repository or ecosystem
- `adk-doc-reviewer` for structure and clarity
- a diagram pass through `/adk:diagram` when the topic benefits from visuals
- `adk-source-publisher` if the final output is Confluence or Google Docs (see Confluence Publish Workflow below)

### Confluence Publish Workflow

When `--publish source` or `--publish both` is specified with a Confluence target, run the following after the document is written (or directly if publishing an existing file):

### Publish Child Agents

Run at least these child agents in parallel:

- **Markdown converter**: reads the markdown source and converts it to Confluence storage format (XHTML). Handles headings, code blocks, tables, admonitions, and inline formatting. Replaces local image references with Confluence attachment references.
- **Attachment and diagram agent**: identifies all referenced images, diagrams, and rendered assets in the markdown. Uploads each as a Confluence attachment. For diagram source files (`.mmd`, `.excalidraw`, `.drawio`), uploads both the editable source and the rendered output. Uses `/adk:diagram` if rendering is needed.
- **Page reviewer** (`adk-doc-reviewer`): reviews the converted page for formatting issues, broken references, and missing attachments before publishing. Verifies all images render correctly in the Confluence preview.

### Publish Steps

1. **Read source.** Parse the markdown file and identify all content, images, and diagram references.
2. **Launch child agents.** Run converter, attachment handler, and reviewer in parallel.
3. **Upload attachments.** Upload all images and diagram assets to the target page via `mcp__atlassian-confluence__confluence_upload_attachment`.
4. **Create or update page.**
   - If `--publish-update` is provided: update the existing page via `mcp__atlassian-confluence__confluence_update_page`
   - Otherwise: create a new page via `mcp__atlassian-confluence__confluence_create_page` under the specified parent (`--publish-parent`)
5. **Verify.** Read the published page back to confirm content and attachments rendered correctly.

### Publish Output

```

### Confluence Publish Summary

Space: <space key>
Page: <page title>
URL: <confluence page URL>
Action: <created | updated>

### Attachments
- <filename>: <uploaded | skipped>
...

### Status: <success | partial | failed>
```

### Writing Rules (All Types)

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets or when strict layout control clearly requires it.
- Use only free or open tooling for conversion and rendering.
- When the document describes real code, inspect the repository first instead of inventing APIs.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:docs-write <prompt-text>
/adk:docs-write "ADR for choosing PostgreSQL over DynamoDB"
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:docs-write "Authentication service migration to OAuth2" --type rfc
/adk:docs-write "API reference for user service" --type api --format confluence
/adk:docs-write --type fix https://docs.google.com/document/d/abc123
/adk:docs-write "Cache Strategy" --type system-design --verbosity detailed --output-dir docs/
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:docs-write "API reference for user service" --type api --format confluence
/adk:docs-write "Q1 Architecture Review" --publish both --publish-space ENG
/adk:docs-write "Cache Strategy" --type system-design --verbosity detailed --output-dir docs/
/adk:docs-write docs/architecture.md --publish source --publish-space ENG --publish-parent "RFCs"
```
