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
    description: "Optional page ID to update"
    required: false
---

# Confluence Publish

Use `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before converting markdown or uploading attachments, run:

`zsh scripts/check-skill-deps.zsh publish-confluence format=confluence`

Then do a lightweight Confluence MCP read against the target space or page so configuration and connectivity are both confirmed before publishing.

Run in parallel:

- a markdown-to-Confluence conversion pass
- an attachment and diagram pass
- a final page review pass

Preserve both rendered assets and editable diagram source files as attachments when they are relevant to the page.
