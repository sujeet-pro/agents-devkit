---
title: "docs-crud"
description: Manage documentation lifecycle — create, update, improve, respond to comments
skill_name: docs-crud
category: task
workflow_tier: full
user_invocable: true
---

# docs-crud

Manage individual documentation pages through their lifecycle. Supports creating new pages from 14 built-in templates, updating docs to match code changes, improving quality, and responding to review comments. Detects pagesmith format automatically and adapts output conventions.

## When to Use

- Create a new documentation page (TDD, HLD, LLD, PRD, ERD, ADR, runbook, incident report, etc.)
- Update an existing doc to reflect code changes
- Improve documentation quality (clarity, examples, structure)
- Respond to review comments on a document
- Create docs from a custom template (local file or URL)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<action>` | `create` \| `update` \| `improve` \| `comment-reply` | required | The lifecycle action to perform |
| `<path>` | file path, directory, or URL | required | Target document or location for new document |
| `--type` | `tdd` \| `hld` \| `lld` \| `prd` \| `erd` \| `adr` \| `rfc` \| `runbook` \| `incident-report` \| `status-report` \| `api-reference` \| `onboarding` \| `release-notes` \| `project` | auto-detect | Document type — loads matching template skeleton |
| `--template` | file path or URL | none | Custom template — overrides `--type` template. Supports local markdown, Confluence URL, Google Docs URL |
| `--auto` | flag | off | Apply changes without interactive approval |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--format` | `markdown` \| `confluence` \| `google-doc` \| `pdf` \| `docx` | `markdown` | Output format for the final document |
| `--help` | flag | — | Show parameter reference and exit |

## Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `create` | Create a new documentation page | Target directory + topic | New document with proper structure |
| `update` | Update a doc based on code changes | Existing doc path | Updated doc with outdated sections refreshed |
| `improve` | Review a doc and apply improvements | Existing doc path | Improved doc with clarity/completeness fixes |
| `comment-reply` | Respond to comments on a doc | Doc path or PR URL | Updated doc + comment replies |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`create`** | Interactive page creation. Loads matching template if `--type` is set, reads custom template if `--template` is provided. Creates folder/README.md structure when pagesmith detected |
| **`create --type tdd`** | Loads TDD template skeleton, confirms scope, runs research, generates diagrams for architecture sections, generates charts for metrics sections |
| **`create --template <url>`** | Fetches template from URL, extracts heading structure and placeholders, uses it as skeleton |
| **`update`** | Diff-driven update. Compares doc against current code to find stale API signatures, removed options, changed behavior. Suggests specific updates |
| **`improve`** | Quality-focused pass. Runs focused quality check (clarity, examples, structure) and suggests concrete improvements |
| **`comment-reply`** | Comment triage. Reads comments from PR reviews, Confluence inline comments, or Google Docs suggestions. Categorizes as fix-needed, discussion, or resolved |
| **`--auto`** | Skips interactive approval — all proposed changes applied directly |

## Document Type Aliases

| Alias | Maps To |
|-------|---------|
| `tech-spec`, `tech-design`, `design-doc` | `tdd` |
| `high-level-design`, `architecture` | `hld` |
| `low-level-design`, `detailed-design` | `lld` |
| `product-requirements`, `product-spec` | `prd` |
| `engineering-requirements`, `requirements` | `erd` |
| `decision-record`, `architecture-decision` | `adr` |
| `request-for-comments`, `proposal` | `rfc` |
| `ops-runbook`, `playbook` | `runbook` |
| `postmortem`, `incident-postmortem` | `incident-report` |
| `sprint-report`, `weekly-report`, `progress-report` | `status-report` |
| `api-docs`, `api-doc`, `endpoint-reference` | `api-reference` |
| `getting-started`, `new-hire`, `setup-guide` | `onboarding` |
| `changelog`, `release`, `what's-new` | `release-notes` |
| `readme`, `project-docs` | `project` |

## Key Behaviors

- **Format detection**: auto-detects pagesmith format from `pagesmith.config.json5` and adapts conventions (folder/README.md, frontmatter, meta.json5)
- **Template system**: 14 built-in templates with document skeletons, placeholder text, diagram/chart markers, and review trackers
- **Diagram integration**: scans `<!-- DIAGRAM: description -->` placeholders and invokes `/adk:diagram` to generate and embed visuals
- **Chart integration**: scans `<!-- CHART: type | data-description -->` placeholders and invokes `/adk:chart` to generate and embed data charts
- **Code-aware updates**: diffs documentation against source code to detect stale content
- **Comment categorization**: classifies review comments as fix-needed, discussion, or resolved before processing

## Workflow

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm action, target, scope, and document type |
| 1. Research & Options | yes | Read current doc state, scan related code, research topic, identify diagram/chart needs |
| 2. Approach Selection | conditional | Only for `create` when section placement is ambiguous or template selection needed |
| 3. Planning | conditional | Only for `create` when the page has multiple sections to outline |
| 4. Execute | yes | Perform the action — create, update, improve, or reply |
| 5. Validate & Learn | yes | Verify links, code examples, frontmatter, diagram/chart rendering |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py for MCP validation |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents: source analyst, outline editor, fact checker, code/diagram specialist, publisher |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `confluence` | target is Confluence | Confluence REST API — page CRUD, comments, attachments |
| `jira` | context references Jira | Jira REST API — issues, comments, search |
| `docs-guidelines` | `--type` is set | Load type-specific document writing guidelines |
| `diagram` | doc needs diagrams | Generate diagrams and render to SVG/PNG |
| `chart` | doc needs data charts | Generate charts from data and render to SVG/PNG |

## Output Format

Output varies by action and `--format`. All actions end with a concise summary.

- **short**: one-line status (e.g., "Created docs/guide/auth/README.md with 4 sections")
- **standard**: action summary with change list
- **detailed**: full change list with before/after comparisons and rationale

| Format | Diagrams | Charts | Embedding |
|--------|----------|--------|-----------|
| `markdown` | SVG (default) | SVG | `![alt](path)` |
| `confluence` | PNG (uploaded as attachment) | PNG (uploaded) | `<ac:image>` tag |
| `google-doc` | PNG (uploaded) | PNG (uploaded) | Inline image |
| `pdf` | PNG (embedded) | PNG (embedded) | Inline |
| `docx` | PNG (embedded) | PNG (embedded) | Inline |

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:docs-repo` | Bulk documentation generation for the entire repository |
| `/adk:docs-review` | Review-only feedback without modifications |
| `/adk:docs-write` | Formal engineering documents (ADRs, RFCs, specs) with stages |
| `/adk:diagram` | Generate diagrams to embed in documentation |
| `/adk:chart` | Generate data charts to embed in documentation |
| `/adk:docs-guidelines` | Document writing quality guidelines per type |

## Examples

```
/adk:docs-crud create docs/design/ --type tdd
/adk:docs-crud create docs/requirements/ --type erd
/adk:docs-crud create docs/prd/ --type prd
/adk:docs-crud create docs/design/auth-service.md --type hld
/adk:docs-crud create docs/reports/ --type incident-report
/adk:docs-crud create docs/ --type status-report
/adk:docs-crud create docs/ --template https://company.atlassian.net/wiki/spaces/ENG/pages/99999
/adk:docs-crud create docs/ --template docs/templates/custom-template.md
/adk:docs-crud update docs/reference/api/README.md
/adk:docs-crud improve docs/guide/getting-started/README.md
/adk:docs-crud comment-reply docs/guide/configuration/README.md
/adk:docs-crud update docs/reference/ --auto
```
