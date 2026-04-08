# Stage: Document Fix (Comment Resolution)

Use this stage to read comments on a Confluence or Google Docs document, propose fixes, and resolve the comment threads. This stage uses an abbreviated workflow -- phases 2-5 are skipped.

Use the shared contracts in `references/source-routing.md`, `references/output-formats.md`, and `references/preflight.md`.

## Phase Applicability Override

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Read document and categorize comments |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Apply fixes to the document |
| 5. Validate & Learn | yes | Verify fixes were applied correctly |

## Preflight Addition

After the standard preflight, confirm the platform MCP is connected with a lightweight read:
- Confluence -> `mcp__atlassian-confluence__confluence_get_page`
- Google Docs -> `mcp__google-drive__getDocumentInfo`

## Source Handling

Detect the platform from the URL:
- Confluence URLs -> use `mcp__atlassian-confluence__*` tools
- Google Docs URLs -> use `mcp__google-drive__*` tools

Read the full document content and all comments (including inline comments, page comments, and reply threads).

## Child Agent Team

- **Comment classifier**: reads all comments and categorizes each as actionable (requires a document change), discussion (question or general feedback), or already-resolved. For actionable comments, extracts the specific change requested and the affected document section. Produces a classified comment list.
- **Fix drafter**: for each actionable comment, reads the surrounding document context and drafts a proposed fix -- the specific text change that addresses the reviewer's request. Ensures fixes are minimal and targeted. Produces a fix plan with before/after text for each comment.

## Workflow

### Step 1: Read and Categorize Comments

1. Fetch all comments on the document via the platform MCP:
   - Confluence: `mcp__atlassian-confluence__confluence_get_comments`
   - Google Docs: `mcp__google-drive__listComments`
2. Launch the comment classifier agent.
3. Filter out already-resolved comments. Present discussion comments as informational.

### Step 2: Analyze and Propose Fixes

1. Launch the fix drafter agent for all actionable comments.
2. Save the plan to `.temp/plans/doc-fix.md` with each comment, its classification, and the proposed fix.

### Step 3: Interactive Fix Loop

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

#### Actions
- Accept: queue the fix for application as-is.
- Edit: let the user revise the proposed fix. Stay in the edit loop until the user accepts or rejects.
- Reject: skip this comment without applying a fix.
- Skip: defer to the end for a final decision.

#### Loop Rules
1. Process fixes in document order (top to bottom).
2. If the user says "accept all remaining", queue all unprocessed fixes.
3. If the user says "reject all remaining", discard all unprocessed fixes.
4. If `auto-apply=true`, skip the interactive loop and apply all fixes directly.

### Step 4: Apply Fixes

Apply all accepted fixes to the document:
- Confluence: use `mcp__atlassian-confluence__confluence_update_page` to update the page body
- Google Docs: use `mcp__google-drive__updateGoogleDoc` to apply text changes

Apply fixes in reverse document order (bottom to top) to prevent offset drift.

### Step 5: Reply and Resolve

After fixes are applied:
1. For each fixed comment, post a reply explaining the fix:
   - Confluence: `mcp__atlassian-confluence__confluence_reply_to_comment`
   - Google Docs: do **not** post replies via MCP (unreliable). Instead, produce a markdown file at `.temp/docs-write/<doc-title>-fix-replies.md` listing each reply with its target comment and content. Present the file path and ask the user to add replies manually.
2. Reply text: "Fixed. [brief description of the change]"
3. If the platform supports it, mark the comment thread as resolved.

For discussion comments that were not actioned, leave them open for the reviewer to follow up.

## Type-Specific Output Format

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

## Adjacent Skills

- `/code-review-pr` for comment-only review of documents
- `general` stage for drafting new documents
