---
name: review-doc-interactive
description: Use when you need an interactive document review loop for Confluence or Google Docs that accepts, edits, rejects comments before posting them to the platform
user_invocable: true
arguments:
  - name: url
    description: "Confluence page URL or Google Docs URL"
    required: true
  - name: type
    description: "Optional document type such as hld, lld, prd, tdd, project, article, blog"
    required: false
  - name: format
    description: "Output format for the review summary: markdown, source, both (default: both)"
    required: false
---

# Interactive Document Review

Use `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill is review-only from the reviewer's perspective. Do not edit the document itself. Post approved comments to the platform and produce a review summary.

## Preflight

Before loading the document body or comments, run:

`zsh scripts/check-skill-deps.zsh review-doc-interactive url=<url> format=<format>`

Then do one lightweight MCP read of the page or document metadata so connectivity is confirmed before the review team starts:

- Confluence -> `mcp__atlassian-confluence__confluence_get_page`
- Google Docs -> `mcp__google-drive__getDocumentInfo`

## Source Handling

Detect the platform from the URL:

- Confluence URLs -> use `mcp__atlassian-confluence__*` tools
- Google Docs URLs -> use `mcp__google-drive__*` tools

Read the full document content, existing comments, and any resolution state before starting analysis. Reconcile existing comments to avoid posting duplicates.

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

Also load `skills/_references/guidelines/document/research-and-fact-checking.md` when the document makes technical or vendor claims.

## Phase 1: Review

Run child agents in parallel:

- `doc-reviewer` for structure, clarity, consistency, completeness, and delivery fit
- `research-agent` for factual verification when the document makes technical claims
- `code-snippet-agent` for embedded code examples
- domain specialist based on document content (frontend, backend, infrastructure, etc.)

Consolidate findings: deduplicate, assign severity and confidence scores.

## Phase 2: Interactive Loop

Present each finding to the user one at a time in this format:

```text
## Finding [N/total] - [severity: critical|high|medium|low]

Section: <document section or heading>
Confidence: NN%

Issue
<description of the issue>

Suggested Comment
<the review comment text that would be posted to the platform>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

### Actions

- Accept: queue the comment for posting as-is.
- Edit: let the user revise the comment text. Stay in the edit loop until the user accepts or rejects the revised version.
- Reject: discard the finding entirely.
- Skip: defer to the end. After all other findings are processed, return to skipped items for a final decision.

### Loop Rules

1. Process findings in severity order (critical first).
2. Do not repost findings that match existing comments on the document.
3. If the user says "accept all remaining", queue all unprocessed findings.
4. If the user says "reject all remaining", discard all unprocessed findings.

## Phase 3: Posting

After the loop finishes, post accepted comments to the platform:

- Confluence: use `mcp__atlassian-confluence__confluence_add_comment` for page-level comments
- Google Docs: use `mcp__google-drive__addComment` for inline or document-level comments

Do NOT edit the document content itself. This skill posts review comments only.

## Phase 4: Summary

Display:

```text
## Interactive Document Review Summary

Platform: [Confluence | Google Docs]
Document: <title>

Accepted: N
Edited: N
Rejected: N
Skipped: N
Posted to platform: N
```

If `format` includes markdown, also produce a markdown review artifact with all findings (accepted and rejected) for reference.
