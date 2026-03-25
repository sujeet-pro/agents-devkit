---
name: write-markdown
description: Use when you need a professional markdown-first engineering deliverable or direct markdown revision with diagrams, code samples, and optional publishing
user_invocable: true
arguments:
  - name: title
    description: "Document title"
    required: true
  - name: output-dir
    description: "Output directory"
    required: false
  - name: frontmatter
    description: "Include YAML frontmatter: yes, no (default: no)"
    required: false
  - name: confluence-sync
    description: "Prepare for Confluence sync: yes, no (default: no)"
    required: false
  - name: doc-type
    description: "Document type such as hld, lld, prd, article, blog, project"
    required: false
---

# Markdown

Use `/devkit:write-doc` with `format=markdown`, but always preserve:

- editable diagram sources
- rendered outputs
- code examples reviewed by `code-snippet-agent`

If you only want review comments instead of direct edits, use `/devkit:review-doc`.

If `confluence-sync=yes`, keep attachments and rendered assets organized so `/devkit:publish-confluence` can post them cleanly.
