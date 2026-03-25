---
name: write-article
description: Use when you need to draft or directly revise a professional deep software engineering article with research, diagrams, and code examples
user_invocable: true
arguments:
  - name: topic
    description: "Article topic or requested revision"
    required: false
  - name: source
    description: "Existing article path or URL to revise in place"
    required: false
  - name: depth
    description: "Depth: standard, exhaustive (default: exhaustive)"
    required: false
  - name: audience
    description: "Audience: senior, staff, principal (default: senior)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# Article

Use `/devkit:write-doc` with `doc-type=article` and `/devkit:research` at `depth=exhaustive`.

This skill owns both first drafts and direct article revisions. If you only want comment-only review, use `/devkit:review-doc`.

Required child agents:

- research
- code example authoring
- document review
- diagram support when the topic benefits from visuals

Keep the subject in software engineering, architecture, or development practice and make the final article professional, evidence-backed, and publication-ready.
