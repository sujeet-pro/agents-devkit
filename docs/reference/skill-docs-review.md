---
title: "docs-review"
description: Review documentation — local files, Confluence, or Google Docs with multi-dimensional analysis
skill_name: docs-review
category: task
workflow_tier: full
user_invocable: true
---

# docs-review

Reviews documentation files for accuracy, completeness, clarity, and style. Produces structured feedback with inline comments and actionable improvement suggestions. Supports local markdown files, entire `docs/` directories, Confluence pages, and Google Docs. Review-only — does not modify source documents.

## When to Use

- Review documentation for technical accuracy against source code
- Check API docs, guides, or READMEs for completeness
- Audit documentation clarity and readability
- Verify style consistency across a documentation set
- Review Confluence pages or Google Docs with comment posting
- Follow up on a previous documentation review to check resolutions
- Run a focused deep-dive on a single review dimension (accuracy, completeness, clarity, style)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<path-or-url>` | file path, directory, Confluence URL, or Google Docs URL | required | What to review. A single file, a directory of docs, or a platform URL |
| `--mode` | `standard` \| `interactive` \| `followup` \| `auto` | `auto` | Review mode. `standard` produces a markdown artifact; `interactive` enables per-finding approval; `followup` reconciles prior comments and checks resolutions; `auto` detects from context |
| `--focus` | `accuracy` \| `completeness` \| `clarity` \| `style` \| `all` | `all` | Focus the review on specific dimensions |
| `--publish` | flag | off | Post comments back to the source platform (Confluence or Google Docs) |
| `--auto` | flag | off | Skip interactive confirmation steps and proceed with recommended actions |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--confidence` | number | 80 | Minimum confidence threshold (0-100). Only findings at or above this score are shown |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Standard mode** (default for local files) | Non-mutating review that produces a markdown artifact. Use `--publish` to also post comments to the platform |
| **Interactive mode** (`--mode interactive`) | Presents each finding for user approval before posting. Only works with Confluence or Google Docs URLs |
| **Follow-up mode** (`--mode followup`) | Re-reviews a document that was previously reviewed. Reconciles prior comments, checks if issues were addressed, evaluates author replies, posts only new or unresolved findings |
| **Auto mode** (default for platform URLs) | Detects prior review comments by the current user. If found → follow-up mode; otherwise → interactive mode |
| **Single file** | Reviews one document in depth across all dimensions |
| **Directory** | Reviews all markdown files. Produces per-file findings plus a cross-cutting summary (consistency, cross-references, navigation gaps) |
| **Focused review** (`--focus accuracy`) | Deep-dives on a single dimension. More thorough than the `all` pass for that dimension |
| **Pagesmith detected** | Adds pagesmith-specific style checks (frontmatter, meta.json5, folder/README.md convention) |

## Review Dimensions

The skill reviews across **5 dimensions**:

1. **Accuracy** — facts match code. API signatures, config keys, CLI flags, endpoint paths, return types verified against actual source
2. **Completeness** — missing topics. Undocumented public APIs, missing error handling docs, absent configuration options, no migration guides for breaking changes
3. **Clarity** — readability. Ambiguous phrasing, unclear antecedents, missing context, jargon without definition, overly complex sentences
4. **Style** — consistency. Heading hierarchy, code block formatting, alert usage, frontmatter correctness, terminology consistency across pages
5. **Examples** — quality and correctness of code examples. Runnable, up-to-date, properly highlighted, error handling shown

Findings are ranked by severity: **must-fix** > **should-fix** > **suggestion** > **nitpick**.

## Key Behaviors

- **Code cross-referencing**: maps doc claims to code locations for accuracy verification (API signatures, config keys, CLI flags)
- **Pagesmith awareness**: detects `pagesmith.config.json5` and adds format-specific checks (frontmatter, meta.json5, folder/README.md)
- **Platform-adaptive**: works with local markdown, Confluence, and Google Docs with appropriate MCP connectors
- **Content inventory**: builds a full inventory of pages, headings, code examples, links, and frontmatter before reviewing
- **Parallel review agents**: launches dedicated agents per dimension (accuracy, completeness, style, clarity)
- **Confidence-scored findings**: each finding includes a confidence score for filtering
- **Review-only**: does not modify source documents — use `/adk:docs-crud` to apply fixes

## Workflow

Follows the 6-phase workflow with phases 2-3 skipped (direct execution after scope confirmation).

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm review target, focus dimensions, audience expectations |
| 1. Research & Options | yes | Read all docs, scan corresponding code, identify review scope |
| 2. Approach Selection | skip | Direct review execution after scope confirmation |
| 3. Planning | skip | Review agents launch directly |
| 4. Execute | yes | Parallel review agents produce findings |
| 5. Validate & Learn | yes | Deduplicate findings, rank by severity, produce final report |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `review-standards` | always | Review pipeline and canonical comment template |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch child agents with distinct review roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `confluence` | target is Confluence | Page CRUD, comments, attachments via REST API |

## Output Format

All output is markdown. Reviews include:

**Per-file findings** with line number, dimension tag, severity, and actionable description:
- `**Line 12** [accuracy] [must-fix]: The install command is wrong...`
- `**Line 34** [completeness] [should-fix]: Missing error handling example...`
- `**Line 56** [clarity] [suggestion]: "Configure appropriately" is vague...`

**Summary table** with dimension-by-severity matrix:

| Dimension | Must-Fix | Should-Fix | Suggestion | Nitpick |
|-----------|----------|------------|------------|---------|
| Accuracy | n | n | n | n |
| Completeness | n | n | n | n |
| Clarity | n | n | n | n |
| Style | n | n | n | n |
| Examples | n | n | n | n |

**Top Issues** list and **Next Steps** with suggested follow-up skills.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:docs-crud` | Apply fixes and improvements from review findings |
| `/adk:docs-repo` | Generate documentation for undocumented areas |
| `/adk:docs-write` | Write formal engineering documents (ADRs, RFCs) |
| `/adk:diagram` | Create diagrams for documentation |

## Examples

```
/adk:docs-review docs/
/adk:docs-review docs/guide/getting-started/README.md --focus accuracy
/adk:docs-review docs/reference/ --focus completeness --verbosity detailed
/adk:docs-review https://company.atlassian.net/wiki/spaces/ENG/pages/12345 --publish
/adk:docs-review https://docs.google.com/document/d/abc123 --mode interactive
/adk:docs-review https://docs.google.com/document/d/abc123 --mode followup
/adk:docs-review ./docs/architecture.md --verbosity detailed
```
