---
title: 'docs-confluence'
description: 'Confluence-specific documentation — read/write Confluence pages with format mapping between Confluence storage format and markdown'
skill_name: docs-confluence
category: task
workflow_tier: full
user_invocable: true
---

# docs-confluence

Use `docs-confluence` to confluence-specific documentation — read/write Confluence pages with format mapping between Confluence storage format and markdown. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`docs-confluence` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `read`, `write`, `sync` | required | The operation to perform |
| `<page-url-or-id>` | Confluence URL or page ID | required | Target page |
| `--space` | space key | auto-detect | Confluence space |
| `--parent` | page ID | none | Parent page for new pages |
| `--format` | `markdown`, `confluence` | `markdown` | Local file format |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | off | Show help |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. |
| `/adk:preflight-check` | before work | Run preflight.py for tool/MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:confluence` | always | Confluence REST API connector — page CRUD, comments, attachments via curl. |
| `/adk:docs-md` | when converting to/from markdown | Markdown/pagesmith features and formatting rules. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

Check for Confluence connectivity:
1. Verify `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` in environment
2. Check for MCP connector: `mcp__atlassian-confluence__*`, `mcp__plugin-atlassian-atlassian__*`, or `mcp__plugin-adk-atlassian__*`
3. Prefer MCP for supported operations, fall back to curl scripts

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `read` | Download Confluence page as local markdown | Page URL/ID | Local .md file with frontmatter |
| `write` | Publish local markdown to Confluence | Local .md file + page URL/ID | Updated Confluence page |
| `sync` | Bi-directional sync between local and Confluence | Directory + space | Updated files and pages |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:docs-crud` — general doc lifecycle management
- `/adk:docs-review` — review Confluence pages for quality
- `/adk:docs-write` — write formal documents, optionally publish to Confluence
- `/adk:confluence` — low-level Confluence API connector (used internally)

## Additional Reference

### Common Workflow

### 1. Confirm

- Confirm action (read, write, sync), target page, and format
- Verify Confluence connectivity via MCP or env vars

### 2. Research

- Read the source content (Confluence page or local markdown)
- Identify format mapping requirements (macros, attachments, alerts)

### 3. Execute

- For `read`: fetch page, convert to markdown, save locally with frontmatter
- For `write`: convert markdown to Confluence storage format, upload attachments, create/update page
- For `sync`: compare local and remote, apply changes in the appropriate direction

### 4. Validate

- Verify round-trip fidelity (no content loss in format conversion)
- Confirm attachments and images render correctly
- Print summary with page URL and action taken

### Format Mapping

### Confluence -> Markdown

| Confluence Element | Markdown Equivalent |
|---|---|
| `<h1>` through `<h6>` | `#` through `######` |
| `<p>` | Paragraph text |
| `<ac:structured-macro ac:name="code">` | Fenced code block with language |
| `<ac:structured-macro ac:name="info">` | `> [!NOTE]` alert |
| `<ac:structured-macro ac:name="warning">` | `> [!WARNING]` alert |
| `<ac:structured-macro ac:name="tip">` | `> [!TIP]` alert |
| `<ac:structured-macro ac:name="note">` | `> [!IMPORTANT]` alert |
| `<table>` | GFM table |
| `<ac:image>` | `![alt](attachment-url)` |
| `<ac:link>` | `[text](url)` |
| `<ac:task-list>` | `- [ ]` / `- [x]` task list |
| `<ac:structured-macro ac:name="expand">` | `<details><summary>` |
| `<ac:structured-macro ac:name="toc">` | (omitted, auto-generated) |

### Markdown -> Confluence

Reverse mapping. Additionally:
- Frontmatter `title` becomes the page title
- Frontmatter `labels` become Confluence labels
- Images referenced as local paths are uploaded as attachments first
- Internal links (`[text](./other-page.md)`) are converted to Confluence page links

### Frontmatter Convention

When reading from Confluence, generate frontmatter:
```yaml
---
confluence_id: "12345"
confluence_url: "https://..."
space: "ENG"
title: "Page Title"
labels: [architecture, api]
last_synced: "2026-04-06T00:00:00Z"
---
```

When writing to Confluence, read frontmatter to determine target page.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:docs-confluence <action> <url>
/adk:docs-confluence read https://company.atlassian.net/wiki/spaces/ENG/pages/12345
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:docs-confluence <action> <url> --auto
```
