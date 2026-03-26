---
name: publish-confluence
description: Publish engineering markdown and diagram assets to Confluence using the Confluence MCP and source-aware attachments
user_invocable: true
arguments:
  - name: source
    description: "Path to the markdown source"
    required: true
  - name: space
    description: "Confluence space key"
    required: true
  - name: parent
    description: "Optional parent page title or ID"
    required: false
  - name: title
    description: "Optional page title override"
    required: false
  - name: update
    description: "Optional page ID to update instead of creating new"
    required: false
---

# Confluence Publish

Use `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before converting markdown or uploading attachments, run:

`zsh scripts/check-skill-deps.zsh publish-confluence format=confluence`

Then do a lightweight Confluence MCP read against the target space or page to confirm connectivity:

- `mcp__atlassian-confluence__confluence_search` with space key to verify access
- If `update` is provided, `mcp__atlassian-confluence__confluence_get_page` to verify the page exists

If the markdown contains diagram sources that need rendering, inherit the `/devkit:diagram` preflight.

## Required Child Agents

Run at least these child agents in parallel:

- **Markdown converter**: reads the markdown source and converts it to Confluence storage format (XHTML). Handles headings, code blocks, tables, admonitions, and inline formatting. Replaces local image references with Confluence attachment references.
- **Attachment and diagram agent**: identifies all referenced images, diagrams, and rendered assets in the markdown. Uploads each as a Confluence attachment. For diagram source files (`.mmd`, `.excalidraw`, `.drawio`), uploads both the editable source and the rendered output. Uses `/devkit:diagram-render` if rendering is needed.
- **Page reviewer** (`doc-reviewer`): reviews the converted page for formatting issues, broken references, and missing attachments before publishing. Verifies all images render correctly in the Confluence preview.

## Workflow

1. **Read source.** Parse the markdown file and identify all content, images, and diagram references.
2. **Launch child agents.** Run converter, attachment handler, and reviewer in parallel.
3. **Upload attachments.** Upload all images and diagram assets to the target page via `mcp__atlassian-confluence__confluence_upload_attachment`.
4. **Create or update page.**
   - If `update` is provided: update the existing page via `mcp__atlassian-confluence__confluence_update_page`
   - Otherwise: create a new page via `mcp__atlassian-confluence__confluence_create_page` under the specified parent
5. **Verify.** Read the published page back to confirm content and attachments rendered correctly.

## Output

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

## Adjacent Skills

- `/devkit:write-markdown` for creating markdown with Confluence sync preparation
- `/devkit:write-doc` for general document drafting
- `/devkit:diagram-render` for rendering diagram sources before upload
- `/devkit:review-doc` for reviewing Confluence pages
