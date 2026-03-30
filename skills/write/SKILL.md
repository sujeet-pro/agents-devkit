---
name: write
description: "[full] [write] Use when creating or updating any engineering document — auto-detects type and loads the right stage, with optional Confluence/Google Docs publishing"
user-invocable: true
argument-hint: "<topic> [--type adr|rfc|api|blog|article|changelog|runbook|migration|onboarding|project|proposal|system-design|tech-radar|tool-eval|fix] [--template <path-or-url>] [--format] [--publish] [--publish-space] [--publish-parent] [--publish-update] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
  mcp-servers: [detect-from-input]
workflow-tier: full
---

# Document Writing

Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.

Use this skill when the agent should create or update any engineering document. It auto-detects the document type from the prompt or an explicit `--type` flag, loads the matching stage file for type-specific guidance, and runs the 6-phase workflow. This skill also handles publishing to Confluence or Google Docs when `--publish` is specified.

If you only want comment-only review without source edits, use `/review`.

## Help

### Parameters

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

### Behavior Variations

- **New document**: Full 6-phase workflow. Creates the document from scratch.
- **Revise existing**: Reads existing content, proposes targeted edits.
- **Fix comments** (`--type fix`): Abbreviated workflow. Reads review comments, proposes fixes, applies after approval.
- **Publish only** (`--publish source` with an existing file): Converts and publishes an existing markdown file to Confluence or Google Docs without rewriting.
- **Write and publish** (`--publish both`): Full writing workflow followed by publishing to the target platform.
- **Template-based** (`--template <path-or-url>`): Reads the template, extracts its structure (headings, sections, placeholders), and generates the document to match. The user can edit sections during Phase 4 via an interactive approval loop.
- **Formal doc types** (RFC, ADR, TDD/system-design): Loads document-metadata guidelines and formal structure templates with YAML frontmatter.
- **Informal doc types** (article, blog, runbook): Lighter structure, narrative-focused.

### Examples

```
/write "Authentication service migration to OAuth2" --type rfc
/write "ADR for choosing PostgreSQL over DynamoDB"
/write changelog --since v2.1.0
/write runbook "Incident response for payment service"
/write "API reference for user service" --type api --format confluence
/write --type fix https://docs.google.com/document/d/abc123
/write "New hire onboarding guide" --audience new-hires --depth comprehensive
/write "Q1 Architecture Review" --publish both --publish-space ENG
/write "Cache Strategy" --type system-design --verbosity detailed --output-dir docs/
/write docs/architecture.md --publish source --publish-space ENG --publish-parent "RFCs"
/write docs/runbook.md --publish source --publish-space OPS --publish-title "Deploy Runbook v2"
/write docs/design.md --publish source --publish-space ENG --publish-update 12345
/write "Onboarding guide" --template docs/templates/onboarding-template.md
/write "Q2 RFC" --template https://company.atlassian.net/wiki/spaces/ENG/pages/99999
```

## Preflight

Before research, drafting, revision, or publishing setup, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team:

- For Confluence (`--publish source` or `--format confluence`): verify access via `mcp__atlassian-confluence__confluence_search` with the space key. If `--publish-update` is provided, verify the page exists via `mcp__atlassian-confluence__confluence_get_page`.
- For Google Docs (`--format google-doc`): verify Google Drive MCP connectivity.

If the document needs diagrams, inherit the `/diagram` preflight before rendering assets.

## Stage Selection

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

## Template Handling

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

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Research the topic, scan related docs and code; Focused research on chosen approach, proposal at .temp/proposal/ |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes; Iterate on proposal with user feedback |
| 3. Planning | yes | Break into tasks/waves for parallel agentic teams |
| 4. Execute | yes | Write the document using child agents for research, writing, fact-checking |
| 5. Validate & Learn | yes | Self-review for accuracy, completeness, readability, guidelines compliance |

The `doc-fix` stage uses an abbreviated workflow (phases 2-5 skipped). See the stage file for details.

## Common Workflow

### Phase 0: Intent Expansion

- restate the document goal, audience, and deliverable
- surface assumptions, source requirements, and publishing constraints
- identify which helpers or connectors are needed
- get approval early before deep research or drafting

### Phase 1: Research & Options

- research the topic using official docs, existing repo content, and relevant source material
- scan for existing documents, patterns, and conventions in the repo
- identify constraints, dependencies, and integration points
- end with 2-3 viable approaches when structure, scope, or publishing strategy is not obvious

### Phase 2: Approach Selection

- present the best options with concrete trade-offs
- ask targeted clarifying questions one at a time
- capture the chosen direction, scope, and destination format

### Phase 3: Planning

- define the document structure, evidence to gather, diagrams needed, and publishing steps
- for larger writing tasks, break the work into explicit waves or checkpoints
- save planning artifacts when the work is complex enough to need tracking

### Phase 4: Execute

- write or revise the document using the child agent team from the loaded stage file
- follow type-specific execution guidance from the stage file
- update progress when the work spans multiple checkpoints or publishing steps

### Phase 5: Validate & Learn

- run an internal review loop with the doc-review team
- verify accuracy, completeness, readability, and guideline compliance
- fix all critical issues that block handoff
- end with a concise summary of what changed, what was validated, and what the reader should understand

## Default Child Agent Team

Unless the stage file specifies a different composition, run at least these child agents in parallel:

- `research-agent` for official docs, standards, and migration notes
- `code-snippet-agent` for examples grounded in the repository or ecosystem
- `doc-reviewer` for structure and clarity
- a diagram pass through `/diagram` when the topic benefits from visuals
- `source-publisher` if the final output is Confluence or Google Docs (see Confluence Publish Workflow below)

## Confluence Publish Workflow

When `--publish source` or `--publish both` is specified with a Confluence target, run the following after the document is written (or directly if publishing an existing file):

### Publish Child Agents

Run at least these child agents in parallel:

- **Markdown converter**: reads the markdown source and converts it to Confluence storage format (XHTML). Handles headings, code blocks, tables, admonitions, and inline formatting. Replaces local image references with Confluence attachment references.
- **Attachment and diagram agent**: identifies all referenced images, diagrams, and rendered assets in the markdown. Uploads each as a Confluence attachment. For diagram source files (`.mmd`, `.excalidraw`, `.drawio`), uploads both the editable source and the rendered output. Uses `/diagram` if rendering is needed.
- **Page reviewer** (`doc-reviewer`): reviews the converted page for formatting issues, broken references, and missing attachments before publishing. Verifies all images render correctly in the Confluence preview.

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
## Confluence Publish Summary

Space: <space key>
Page: <page title>
URL: <confluence page URL>
Action: <created | updated>

### Attachments
- <filename>: <uploaded | skipped>
...

### Status: <success | partial | failed>
```

## Guideline Loading

Invoke the `/coding` helper skill to detect the repo stack and load the appropriate coding guidelines when the document describes real code or architecture.

## Writing Rules (All Types)

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets or when strict layout control clearly requires it.
- Use only free or open tooling for conversion and rendering.
- When the document describes real code, inspect the repository first instead of inventing APIs.

## Output Format

All output is markdown by default. Structure varies by document type -- see the loaded stage file for the exact format. Support markdown, Confluence, Google Docs, and PDF as output targets (see `references/output-formats.md`).

## Adjacent Skills

- `/review` for comment-only review of documents
- `/diagram` for standalone architecture diagrams
- `/coding` for coding guidelines detection
- `/doc-writing` for document writing guidelines
