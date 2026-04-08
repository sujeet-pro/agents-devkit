# Follow-Up Document Review

This stage handles re-reviewing a document that was previously reviewed. It reconciles prior comments, checks if issues were addressed, evaluates author replies, and focuses only on remaining or new issues.

Activated when `--mode followup` is set or when auto-detection finds prior review comments by the current user.

## Source Handling

Read the full document content plus all existing comments, their resolution state, and any reply chains:

- Confluence: `mcp__atlassian-confluence__confluence_get_page` + `mcp__atlassian-confluence__confluence_get_comments`
- Google Docs: `mcp__google-drive__getDocument` + `mcp__google-drive__getComments`

## Guideline Loading

Invoke the `/coding` helper skill to detect the repo stack and load the appropriate coding guidelines.

## Phase 1: Build Comment Ledger

Read all existing review comments and classify each into one of these buckets:

| Bucket | Description |
|--------|-------------|
| **Open and actionable** | Comment is unresolved and the issue persists in the document |
| **Addressed** | The document was updated to fix the issue, but the comment is not yet resolved |
| **Resolved** | Comment was marked resolved on the platform |
| **Resolved but not fixed** | Comment was resolved but the underlying issue persists |
| **Obsolete** | The section was rewritten in a way that makes the comment irrelevant |

For each comment, record:
- Comment ID and thread ID
- Original issue description
- Document section reference
- Current resolution state
- Author replies (if any)

## Phase 2: Evaluate Replies

For each comment that has author replies:

1. Read the reply in full context against the current document state.
2. Classify the reply:
   - **Valid resolution**: the author's change or explanation resolves the concern. Queue for resolution.
   - **Insufficient**: the concern remains despite the reply. Draft a follow-up reply explaining the gap.
   - **Needs discussion**: the point is debatable. Present to the user with both sides.
3. Present each reply evaluation:

```text
## Reply on Comment [N/total]

Original concern: <summary>
Author reply: <reply text>
Document state: [changed | unchanged]

Assessment: [Valid | Insufficient | Needs discussion]
Reasoning: <why>

Action: [A]ccept resolution | [R]eply (draft provided) | [E]dit reply | [S]kip
```

## Phase 3: Scan for New Issues

Run the standard review pipeline on the current document state:

1. Launch child agents in parallel for structure, accuracy, completeness, style, and actionability.
2. Deduplicate findings against open comments from the ledger.
3. Filter out issues that duplicate already-open threads.

## Phase 4: Interactive Summary

Present the full follow-up summary before posting:

```text
## Follow-Up Review Summary

### Previous Comments
| Status              | Count |
|---------------------|-------|
| Addressed           |     N |
| Resolved            |     N |
| Resolved but unfixed|     N |
| Obsolete            |     N |
| Replies evaluated   |     N |

### New Issues Found: N
```

Allow the user to:
- Override any classification
- Edit follow-up reply text before posting
- Skip posting for specific items

## Phase 5: Post and Resolve

After user confirmation:

1. **Addressed comments**: resolve the thread. Post a brief acknowledgment.
2. **Resolved but not fixed**: reopen or post a new comment referencing the original thread.
3. **Obsolete comments**: resolve with a note that the section was rewritten.
4. **Reply evaluations**: post follow-up replies within the existing thread (not as new top-level comments).
5. **New issues**: post as new comments.

### Thread Reply Rules

- Always reply within existing comment threads, never create new top-level comments for thread-related responses.
- For Confluence: use `mcp__atlassian-confluence__confluence_add_comment` with the parent comment ID.
- For Google Docs: do **not** post comments or replies via MCP (unreliable). Instead, collect all actions (replies, new comments, resolutions) and produce a markdown file at `.temp/docs-review/<doc-title>-followup-comments.md` listing each action with its target comment/section and content. Present the file path and ask the user to apply the actions manually.
- When the platform does not support threaded replies, post a new comment that references the original by quoting its first line.

## Summary

After all actions complete, display:

```text
## Follow-Up Document Review Complete

Platform: [Confluence | Google Docs | Local]
Document: <title>

Resolved threads: N
Follow-up replies posted: N
Reopened threads: N
New comments posted: N
Skipped: N
Output: [Platform comments | Markdown at <path>]
```
