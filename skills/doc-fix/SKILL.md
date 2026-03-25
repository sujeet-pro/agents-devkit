---
name: doc-fix
description: Use when you want to read comments on your own Confluence or Google Docs document, apply fixes, and resolve the comment threads
user_invocable: true
arguments:
  - name: url
    description: "Confluence page URL or Google Docs URL"
    required: true
  - name: auto-apply
    description: "Auto-apply fixes without asking (default: false)"
    required: false
---

# Document Fix Comments

Use the shared contracts in `skills/_references/source-routing.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

This skill reads review comments and feedback on your document, proposes fixes, and applies them after your approval.

## Preflight

Before any work, run:

`zsh scripts/check-skill-deps.zsh doc-fix url=<url>`

Then confirm the platform MCP is connected with a lightweight read:

- Confluence -> `mcp__atlassian-confluence__confluence_get_page`
- Google Docs -> `mcp__google-drive__getDocumentInfo`

## Source Handling

Detect the platform from the URL:

- Confluence URLs -> use `mcp__atlassian-confluence__*` tools
- Google Docs URLs -> use `mcp__google-drive__*` tools

Read the full document content and all comments (including inline comments, page comments, and reply threads).

## Phase 1: Read and Categorize Comments

1. Fetch all comments on the document via the platform MCP:
   - Confluence: `mcp__atlassian-confluence__confluence_get_comments`
   - Google Docs: `mcp__google-drive__listComments`
2. Categorize each comment:
   - **Actionable**: contains a fix request, correction, suggestion, or improvement that requires a document change
   - **Discussion**: a question, clarification request, or general feedback that does not require a document edit
   - **Already resolved**: marked as resolved on the platform
3. Filter out already-resolved comments. Present discussion comments as informational but do not attempt fixes for them.

## Phase 2: Analyze and Propose Fixes

For each actionable comment:

1. Read the surrounding document context (the section or paragraph the comment references).
2. Understand what the reviewer is asking for.
3. Draft a proposed fix — the specific text change to the document.

Save the plan to `.temp/plans/doc-fix.md` with each comment, its classification, and the proposed fix.

## Phase 3: Interactive Fix Loop

Present each proposed fix to the user:

```text
## Fix [N/total]

Comment by: <author>
Section: <document section or heading>

Reviewer said:
<comment text>

Current text:
<the text that would be changed>

Proposed fix:
<the replacement text>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

### Actions

- Accept: queue the fix for application as-is.
- Edit: let the user revise the proposed fix. Stay in the edit loop until the user accepts or rejects.
- Reject: skip this comment without applying a fix.
- Skip: defer to the end for a final decision.

### Loop Rules

1. Process fixes in document order (top to bottom).
2. If the user says "accept all remaining", queue all unprocessed fixes.
3. If the user says "reject all remaining", discard all unprocessed fixes.
4. If `auto-apply=true`, skip the interactive loop and apply all fixes directly.

## Phase 4: Apply Fixes

Apply all accepted fixes to the document:

- Confluence: use `mcp__atlassian-confluence__confluence_update_page` to update the page body
- Google Docs: use `mcp__google-drive__updateGoogleDoc` to apply text changes

Apply fixes in reverse document order (bottom to top) to prevent offset drift.

## Phase 5: Reply and Resolve

After fixes are applied:

1. For each fixed comment, post a reply explaining the fix:
   - Confluence: `mcp__atlassian-confluence__confluence_reply_to_comment`
   - Google Docs: `mcp__google-drive__replyToComment`
2. Reply text: "Fixed. [brief description of the change]"
3. If the platform supports it, mark the comment thread as resolved.

For discussion comments that were not actioned, leave them open for the reviewer to follow up.

## Output

Display a summary:

```text
## Document Fix Summary

Platform: [Confluence | Google Docs]
Document: <title>

| Status   | Count |
|----------|-------|
| Fixed    |     N |
| Skipped  |     N |
| Rejected |     N |
| Discussion (no action) | N |

### Changes Applied
- Section "<heading>": <what changed>
- Section "<heading>": <what changed>
```
