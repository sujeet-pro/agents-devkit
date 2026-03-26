---
name: write-blog
description: Use when you need to draft or directly revise a professional software engineering blog post, changelog-style update, or technical announcement
user_invocable: true
arguments:
  - name: topic
    description: "Blog post, update, or announcement topic"
    required: false
  - name: source
    description: "Existing blog path or URL to revise in place"
    required: false
  - name: audience
    description: "Audience: developers, managers, general (default: developers)"
    required: false
  - name: tone
    description: "Tone: conversational, technical, opinionated (default: conversational)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# Blog

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill owns both first drafts and direct revisions. If you only want comments, use `/devkit:review-doc`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-blog format=<format>`

If the post will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/blog.md`

Load `skills/_references/guidelines/document/research-and-fact-checking.md` when the post makes technical claims that need verification.

## Required Child Agents

Run at least these child agents in parallel:

- **Research agent** (`research-agent`): gathers supporting evidence, statistics, or references that ground the post in facts. Uses `/devkit:research` at `depth=quick` or `depth=standard` depending on topic complexity. Produces a brief with key points and citations.
- **Code or example agent** (`code-snippet-agent`): writes, reviews, and validates any code examples, configuration snippets, or command-line examples included in the post. Ensures accuracy and relevance.
- **Editorial reviewer** (`doc-reviewer`): reviews the draft for tone consistency, audience fit, readability, logical flow, and publication readiness. Checks that the requested tone is applied consistently throughout.

## Workflow

1. **Research.** Launch the research agent to gather supporting material for the topic.
2. **Outline.** Design the blog structure:
   - **Hook**: opening paragraph that states the problem or insight
   - **Context**: background the reader needs
   - **Body**: main argument, analysis, or walkthrough (2-4 sections)
   - **Code or examples**: practical demonstrations where applicable
   - **Conclusion**: key takeaway and call to action
3. **Draft.** Write the full post with the requested tone and audience in mind.
4. **Code examples.** Launch the code example agent for any technical snippets.
5. **Review.** Launch the editorial reviewer for tone, flow, and accuracy.
6. **Revise.** Incorporate reviewer feedback and polish for publication.

Save intermediary artifacts to `.temp/write-blog/`.

## Writing Rules

- Produce polished, technically grounded, publication-ready posts.
- Apply the requested tone consistently:
  - **conversational**: first person, accessible language, analogies
  - **technical**: precise terminology, implementation details, benchmarks
  - **opinionated**: clear position, supporting arguments, counterpoints addressed
- Default to markdown as the source of truth.
- Keep both editable diagram source files and rendered outputs when visuals are included.

## Final Step

Before publishing, run an internal review loop with the editorial reviewer and fix all issues that block handoff.

## Adjacent Skills

- `/devkit:write-article` for deeper, research-heavy technical articles
- `/devkit:write-changelog` for release-focused changelogs
- `/devkit:write-doc` for general-purpose document drafting
- `/devkit:review-doc` for comment-only review without editing
