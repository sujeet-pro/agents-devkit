---
title: 'adk-confluence'
description: 'Manage Confluence pages, spaces, comments, labels, and attachments via MCP. Use when publishing, updating, or searching documentation on Confluence'
skill_name: adk-confluence
category: task
workflow_tier: full
user_invocable: true
---

# adk-confluence

Use `adk-confluence` to manage Confluence pages, spaces, comments, labels, and attachments via MCP. Use when publishing, updating, or searching documentation on Confluence. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-confluence` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What Confluence operation to perform |
| `--action` | `create`, `update`, `search`, `publish`, `manage` | inferred from task | Explicit action when ambiguous |
| `--space` | space key (e.g. `ENG`, `DOCS`) | none | Target Confluence space |
| `--page` | page ID or exact title | none | Target page identifier |
| `--parent` | page ID or title | none | Parent page for creation or moves |
| `--labels` | comma-separated labels | none | Labels to add after create/update |
| `--format` | `markdown`, `storage` | `markdown` | Input format when publishing local content |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Discover | Search existing pages, identify target space and parent, check for duplicates | **Confirm**: space, parent, intent |
| 2. Plan | Propose page structure, content outline, labels, attachments | **Approval**: content plan |
| 3. Draft | Write content from code evidence; dispatch subagents for complex sections | -- |
| 4. Publish | Create or update page via MCP; upload attachments; apply labels | -- |
| 5. Verify | Confirm page exists, renders correctly, URL is accessible | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Action**: created page
**Space**: ENG
**Page**: "Auth Service Architecture" (ID: 12345)
**URL**: https://wiki.example.com/spaces/ENG/pages/12345
**Labels**: architecture, auth, backend
**Next**: add diagrams, link from parent page
```

Lead with action and URL. Offer content preview on request.

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- page creation, updates, and deletions require content preview and approval; searches and reads proceed immediately.
- **Plan First** -- discover existing pages, propose page structure and content plan, get approval before publishing.
- **Brainstorm Only For Publishing Choice** -- when the user is still deciding whether to create, update, publish, or reorganize content, run a short brainstorming pass before mutating Confluence.
- **Concise by Default** -- lead with page URL and change summary; offer full content preview on request.
- **Self-Sufficient** -- requires Confluence MCP server; provides setup instructions if missing.
- **Parallel Agentic Teams** -- dispatch `adk-doc-writer` subagents for section authoring when content is complex.

### Persona

See `references/persona.md` for full definition.

**Knowledge Base Curator.** Organized documentation specialist who treats Confluence as a structured knowledge system. Searches before creating to avoid duplicates, proposes page hierarchies that fit existing space structure, and converts markdown to Confluence storage format with precision.

### When To Use

- creating, reading, updating, or deleting Confluence pages
- publishing local markdown files to Confluence as formatted pages
- searching across Confluence spaces for pages, content, or labels
- navigating space page trees and managing page hierarchy
- adding or reading comments, labels, and attachments
- reviewing page history and comparing versions

### When NOT To Use

- local-only documentation with no Confluence destination -- use `adk-write-docs`
- reviewing doc quality without publishing -- use `adk-review-docs`
- Google Docs or Drive operations -- use `adk-google-drive`

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` and `python3` are in PATH
2. Confirm the `atlassian-confluence` MCP server is configured in IDE settings
3. If MCP server is missing, exit with setup instructions

### Interaction Protocol

- **Search before creating**: always check for existing pages with similar titles or content to avoid duplicates
- **Preview before publishing**: present content preview with target space, parent, title, and word count before executing
- **Confirm destructive operations**: delete, overwrite, and page moves require explicit approval even with `--auto`
- **Report with URLs**: every response includes the page URL and page ID
- **Markdown conversion**: automatically convert markdown to Confluence storage format; warn about unsupported elements

### Parallel Agents

- Dispatch `adk-doc-writer` subagents for individual section authoring when the page has multiple complex sections
- Dispatch a search subagent to check for duplicate pages while the main agent plans content
- The orchestrator assembles sections into the final page; subagents produce section content only

### Validation

- Every page create/update is confirmed by fetching the resulting page
- Every delete is confirmed by verifying the page is no longer accessible
- Attachment uploads are confirmed by listing page attachments after upload
- Search results include page IDs and URLs for verification
- Never claim success without checking the MCP response

### Anti-Patterns / Red Flags

- Creating pages without searching for existing duplicates via `confluence_search`
- Publishing without converting markdown to Confluence storage format
- Deleting pages without confirming the page tree impact via `confluence_get_page_children` (child pages become orphans)
- Updating pages without fetching current version via `confluence_get_page` first (risks overwriting concurrent edits)
- Ignoring local image references when publishing markdown (images must be uploaded via `confluence_upload_attachment` first)
- Moving pages without checking the destination space and parent via `confluence_get_space_page_tree`

### Related Skills

- `adk-write-docs` -- local documentation authoring
- `adk-review-docs` -- documentation quality review
- `adk-google-drive` -- Google Docs/Drive operations

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-confluence <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-confluence <prompt-text> --auto
```
