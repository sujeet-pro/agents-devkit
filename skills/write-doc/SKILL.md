---
name: write-doc
description: Use when you need to draft or directly revise a professional engineering document and want DevKit to update the content instead of leaving review comments
user_invocable: true
arguments:
  - name: topic
    description: "Topic, title, or requested change"
    required: false
  - name: source
    description: "Existing document path or URL to revise in place"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
  - name: depth
    description: "Depth: overview, standard, deep-dive (default: standard)"
    required: false
  - name: audience
    description: "Audience: developer, senior, staff, principal (default: senior)"
    required: false
  - name: doc-type
    description: "Optional type such as rfc, tech-spec, adr, hld, lld, prd, project, article, blog"
    required: false
---

# Document Writing

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should improve the document directly. If you want comment-only review without source edits, use `/devkit:review-doc`.

For the three core engineering document types, prefer the dedicated skills:
- **RFC** -> `/devkit:write-rfc` (pre-alignment: "should we do this?")
- **Tech Spec / TDD** -> `/devkit:write-system-design` (implementation: "how will we build this?")
- **ADR** -> `/devkit:write-adr` (durable decisions: "what did we decide?")

HLD and LLD are sections within a Tech Spec, not separate document types. If `doc-type` is `hld` or `lld`, consider whether the user actually needs a full Tech Spec.

## Preflight

Before research, drafting, revision, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-doc format=<format> source=<source>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If the document needs diagrams, inherit the `/devkit:diagram` preflight before rendering assets.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for official docs, standards, and migration notes
- `code-snippet-agent` for examples grounded in the repository or ecosystem
- `doc-reviewer` for structure and clarity
- a diagram pass through `/devkit:diagram` when the topic benefits from visuals
- `source-publisher` if the final output is Confluence or Google Docs

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

For document types that require metadata, review tracking, or status lifecycle (RFC, Tech Spec, ADR, or any formal engineering document), also load:

- `skills/_references/guidelines/document/document-metadata.md`

Then add the document-type guideline when matched:

- RFC -> `skills/_references/guidelines/document/rfc.md`
- tech-spec / TDD -> `skills/_references/guidelines/document/tdd.md`
- ADR -> `skills/_references/guidelines/document/adr.md`
- HLD -> `skills/_references/guidelines/document/hld.md`
- LLD -> `skills/_references/guidelines/document/lld.md`
- PRD -> `skills/_references/guidelines/document/prd.md`
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

Load `skills/_references/guidelines/document/research-and-fact-checking.md` for research-heavy work and the matching coding guidance from `skills/_references/guidelines/coding/` when the document includes code or architecture analysis.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- When `source` is provided, revise the existing document directly instead of generating a detached review.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets or when strict layout control clearly requires it.
- Use only free or open tooling for conversion and rendering.
- When the document describes real code, inspect the repository first instead of inventing APIs.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.
