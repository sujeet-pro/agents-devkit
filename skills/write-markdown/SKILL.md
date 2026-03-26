---
name: write-markdown
description: Use when you need a professional markdown-first engineering deliverable or direct markdown revision with diagrams, code samples, and optional publishing
user_invocable: true
arguments:
  - name: title
    description: "Document title"
    required: true
  - name: doc-type
    description: "Document type such as hld, lld, prd, article, blog, project, tdd, runbook, adr"
    required: false
  - name: output-dir
    description: "Output directory"
    required: false
  - name: frontmatter
    description: "Include YAML frontmatter: yes, no (default: no)"
    required: false
  - name: confluence-sync
    description: "Prepare for Confluence sync: yes, no (default: no)"
    required: false
---

# Markdown

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill produces markdown-first deliverables with inline diagrams, code samples, and optional Confluence sync preparation. For document types with dedicated skills (RFC, ADR, system design), prefer those skills. For comment-only review, use `/devkit:review-doc`.

## Preflight

Before drafting or revision, run:

`zsh scripts/check-skill-deps.zsh write-markdown`

If diagrams will be included, inherit the `/devkit:diagram` preflight before rendering assets. If `confluence-sync=yes`, verify Confluence MCP connectivity.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

When `doc-type` is specified, also load the matching guideline:

- hld -> `skills/_references/guidelines/document/hld.md`
- lld -> `skills/_references/guidelines/document/lld.md`
- prd -> `skills/_references/guidelines/document/prd.md`
- article -> `skills/_references/guidelines/document/article.md`
- blog -> `skills/_references/guidelines/document/blog.md`
- project -> `skills/_references/guidelines/document/project.md`
- tdd -> `skills/_references/guidelines/document/tdd.md`
- runbook -> `skills/_references/guidelines/document/runbook.md`
- adr -> `skills/_references/guidelines/document/adr.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Source analyst**: reads the repository, existing docs, or reference material to gather context. Produces a content brief with key facts, structure recommendations, and source references.
- **Code snippet agent** (`code-snippet-agent`): writes, reviews, and validates all code examples. Ensures correctness and relevance to the narrative.
- **Document reviewer** (`doc-reviewer`): reviews the draft for structure, completeness, clarity, and adherence to the loaded guidelines.
- **Diagram agent**: produces diagrams through `/devkit:diagram` when the document benefits from visual explanation.

## Workflow

1. **Gather context.** Launch the source analyst to read relevant repository code, docs, or reference material.
2. **Outline.** Design the document structure based on the `doc-type` guidelines or the requested title and scope.
3. **Draft.** Write the full markdown document with code example and diagram placeholders.
4. **Code examples.** Launch the code snippet agent to fill and validate all code blocks.
5. **Diagrams.** Launch the diagram agent for any visual elements.
6. **Review.** Launch the document reviewer to check against guidelines.
7. **Revise.** Incorporate reviewer feedback and fix all critical issues.
8. **Confluence prep.** If `confluence-sync=yes`, organize rendered assets and attachments so `/devkit:publish-confluence` can post them cleanly.

Save intermediary artifacts to `.temp/write-markdown/`.

## Output

A professional markdown document with:

- clean heading hierarchy and consistent formatting
- validated code examples
- editable diagram sources alongside rendered outputs
- YAML frontmatter if `frontmatter=yes`
- Confluence-ready asset organization if `confluence-sync=yes`

## Final Step

Before delivering, run an internal review loop and fix all critical issues.

## Adjacent Skills

- `/devkit:write-rfc` for RFC documents
- `/devkit:write-adr` for Architecture Decision Records
- `/devkit:write-system-design` for system design documents
- `/devkit:write-doc` for general document drafting with broader format support
- `/devkit:publish-confluence` for publishing markdown to Confluence
- `/devkit:review-doc` for comment-only review without editing
