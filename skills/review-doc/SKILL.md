---
name: review-doc
description: Use when you need a non-mutating review of a local document, Confluence page, or Google Doc with comments or a review artifact instead of direct edits
user_invocable: true
arguments:
  - name: source
    description: "File path, Confluence URL, or Google Docs URL"
    required: true
  - name: doc-type
    description: "Optional type such as hld, lld, prd, tdd, project, article, blog"
    required: false
  - name: coding-tags
    description: "Optional coding guideline tags used when the document includes code"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100, default: 75)"
    required: false
  - name: publish
    description: "Where to send the review: markdown, source, both (default: both)"
    required: false
---

# Document Review

Use `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill is review-only. Do not revise the source document in place. Leave inline comments when the source supports them, otherwise produce a markdown review artifact that can drive follow-up edits.

## Preflight

Before loading the document body or comments, run:

`zsh scripts/check-skill-deps.zsh review-doc source=<source> publish=<publish>`

For Confluence and Google Docs, follow that with one lightweight MCP read of the page or document metadata so connectivity is confirmed before the review team starts.

## Source Handling

- Local files: read the file plus any linked diagrams or attachments.
- Confluence: read the page body, labels, attachments, existing comments, and resolution state through the Confluence MCP.
- Google Docs: read the document body, comments, and linked assets through Google Drive MCP.
- Read existing comments first and reconcile them before emitting new findings.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

Then add the document-type guideline when matched:

- HLD -> `skills/_references/guidelines/document/hld.md`
- LLD -> `skills/_references/guidelines/document/lld.md`
- PRD -> `skills/_references/guidelines/document/prd.md`
- TDD -> `skills/_references/guidelines/document/tdd.md`
- project -> `skills/_references/guidelines/document/project.md`
- article -> `skills/_references/guidelines/document/article.md`
- blog -> `skills/_references/guidelines/document/blog.md`
- changelog -> `skills/_references/guidelines/document/changelog.md`
- coding-guidelines -> `skills/_references/guidelines/document/coding-guidelines-doc.md`
- community-guidelines -> `skills/_references/guidelines/document/community-guidelines.md`
- deep-dive -> `skills/_references/guidelines/document/deep-dive.md`
- ERD -> `skills/_references/guidelines/document/erd.md`
- feedback -> `skills/_references/guidelines/document/feedback.md`
- appraisal-review -> `skills/_references/guidelines/document/appraisal-review.md`
- system-design -> `skills/_references/guidelines/document/system-design-article.md`
- tool-evaluation -> `skills/_references/guidelines/document/tool-evaluation.md`

Also load `skills/_references/guidelines/document/research-and-fact-checking.md` when the document makes technical or vendor claims, and add coding guidance from `skills/_references/guidelines/coding/` when the document includes real code or architecture decisions.

## Required Child Agents

Run at least these child agents in parallel:

- `doc-reviewer` for structure, clarity, consistency, and delivery fit
- `code-snippet-agent` for embedded code examples
- `research-agent` for factual verification when the doc makes technical claims
- `code-reviewer` when the document proposes or critiques implementation details
- `source-publisher` after consolidation if `publish` includes source comments

## Review Requirements

Every document review must check:

- structure and completeness
- factual accuracy and version drift
- code and diagram correctness
- alignment with the destination format
- actionability for engineering readers
- existing comment reconciliation before new comments are posted

## Output

Always produce a markdown review artifact first. If `publish` includes source posting, add comments back to Confluence or Google Docs using the matching MCP. If the source cannot accept comments, the markdown review artifact is the final handoff.
