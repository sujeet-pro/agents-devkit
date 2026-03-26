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

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill owns both first drafts and direct article revisions. If you only want comment-only review, use `/devkit:review-doc`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-article format=<format>`

If the article will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If the article needs diagrams, inherit the `/devkit:diagram` preflight before rendering assets.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/article.md`
- `skills/_references/guidelines/document/research-and-fact-checking.md`

Load additional coding guidelines from `skills/_references/guidelines/coding/` when the article covers implementation details or includes code examples.

## Required Child Agents

Run at least these child agents in parallel:

- **Research agent** (`research-agent`): conducts research using `/devkit:research` at the requested depth. Gathers primary sources, official documentation, academic references, and real-world implementation examples. Produces a research brief with citations and source quality ratings.
- **Code example agent** (`code-snippet-agent`): writes, reviews, and validates all code examples in the article. Ensures examples are grounded in real repositories or ecosystem patterns, compile or run correctly, and follow best practices for the target language.
- **Document reviewer** (`doc-reviewer`): reviews the draft for structure, clarity, logical flow, audience fit, and completeness. Checks that claims are supported by the research brief and that the article meets professional publication standards.
- **Diagram agent**: produces architecture diagrams, flow diagrams, or comparison visuals through `/devkit:diagram` when the topic benefits from visual explanation.

## Workflow

1. **Research.** Launch the research agent to gather sources, prior art, and supporting evidence for the topic.
2. **Outline.** Design the article structure with sections appropriate to the topic and audience.
3. **Draft.** Write the full article with the research brief as input. Include inline citations, code examples, and diagram placeholders.
4. **Code examples.** Launch the code example agent to write, validate, and polish all code samples.
5. **Diagrams.** Launch the diagram agent for any visual elements that clarify the narrative.
6. **Review.** Launch the document reviewer to check the complete draft against article guidelines.
7. **Revise.** Incorporate reviewer feedback and fix all critical issues.

Save intermediary artifacts to `.temp/write-article/`.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.
- When the article describes real code, inspect the repository first instead of inventing APIs.
- Tailor depth and terminology to the specified audience.
- Every claim must be backed by a citation or direct code reference.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.

## Adjacent Skills

- `/devkit:write-blog` for shorter, conversational technical posts
- `/devkit:write-doc` for general-purpose document drafting
- `/devkit:review-doc` for comment-only review without editing
- `/devkit:research` for standalone research without article drafting
