# Interactive Document Review

This stage runs an interactive review loop for Confluence or Google Docs. The user accepts, edits, rejects, or skips each comment before it is posted to the platform. Activated with `--interactive`.

## Source Handling

Detect the platform from the URL:

- Confluence URLs -> use `mcp__atlassian-confluence__*` tools
- Google Docs URLs -> use `mcp__google-drive__*` tools

Read the full document content, existing comments, and any resolution state before starting analysis. Reconcile existing comments to avoid posting duplicates.

## Guideline Loading

Invoke the `/coding` helper skill to detect the repo stack and load the appropriate coding guidelines.

## Interactive Review TUI

After generating and validating all findings, launch the interactive review TUI.

### Step 1: Prepare Session

Create the session directory and write all findings as `items.json`:

```bash
mkdir -p .temp/interactive/doc-review-<slug>/
```

Write `.temp/interactive/doc-review-<slug>/items.json`:

```json
{
  "title": "Doc Review: <document title>",
  "items": [
    {
      "id": "finding-<N>",
      "title": "[<Priority>] <short description>",
      "body": "<full comment with context and suggestion>",
      "metadata": {
        "section": "<document section>",
        "priority": "<Critical|Should Have|May Have|Nitpick>",
        "category": "<accuracy|clarity|structure|style|completeness>"
      }
    }
  ]
}
```

Sort items by severity (critical first).

### Step 2: Launch TUI

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/tui/review.py .temp/interactive/doc-review-<slug>/
```

The TUI auto-installs its dependency (`textual`) on first run. The user reviews each finding and marks it as:

- **Accept** (a): queue for posting
- **Reject** (r): discard
- **Edit** (e): mark for regeneration with a user-provided prompt

### Step 3: Process Results

Read `.temp/interactive/doc-review-<slug>/results.json` and process:

- **`accepted`** → Post to platform immediately:
  - Confluence: `mcp__atlassian-confluence__confluence_add_comment`
  - Google Docs: `mcp__google-drive__addComment`
- **`rejected`** → Discard
- **`edit`** → Regenerate the comment using the `prompt` field

Do NOT edit the document content itself. This stage posts review comments only.

### Step 4: Edit Loop

If any results have `action: "edit"`:

1. Regenerate those comments based on each item's edit `prompt`
2. Write a new `items.json` with only the regenerated items
3. Launch the TUI again (back to Step 2)
4. Repeat until all items are `accepted` or `rejected`

### Summary

After all rounds complete, display:

```text
## Interactive Document Review Summary

Platform: [Confluence | Google Docs]
Document: <title>
TUI rounds: N

Accepted: N
Rejected: N
Posted to platform: N
```

If `--verbosity detailed` is set, also produce a markdown review artifact with all findings (accepted and rejected) for reference.
