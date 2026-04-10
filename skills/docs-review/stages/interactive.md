# Interactive Document Review

This stage runs an interactive review loop for Confluence or Google Docs. The user accepts, edits, rejects, or skips each comment before it is posted to the platform.

## Source Handling

Detect the platform from the URL:

- Confluence URLs -> use `mcp__atlassian-confluence__*` or `mcp__plugin-adk-atlassian__*` tools
- Google Docs URLs -> use `mcp__google-drive__*` tools

Read the full document content, existing comments, and any resolution state before starting analysis. Reconcile existing comments to avoid posting duplicates.

## Guideline Loading

Invoke the `/adk:coding` helper skill to detect the repo stack and load the appropriate coding guidelines.

## Interaction Mode

Use inline interactivity — render findings in the conversation per `references/inline-interaction.md`.

## Interactive Review

After generating and validating all findings, filter out any with confidence below the `--confidence` threshold (default: 80%). Present the remaining findings to the user.

### Step 1: Prepare Session

Create the session directory and write all findings as `items.json`:

```bash
mkdir -p .temp/interactive/doc-review-<slug>/
```

Write `.temp/interactive/doc-review-<slug>/items.json`:

```json
{
  "title": "Doc Review: <document title>",
  "mode": "doc",
  "items": [
    {
      "id": "finding-<N>",
      "title": "[<Priority>] <short description>",
      "body": "<full comment with context and suggestion>",
      "metadata": {
        "section": "<document section>",
        "priority": "<Critical|Should Have|May Have|Nitpick>",
        "category": "<accuracy|clarity|structure|style|completeness>",
        "confidence": "<score>"
      }
    }
  ]
}
```

Sort items by severity (critical first).

### Step 2: Present Findings

Use the **Review Findings** protocol from `references/inline-interaction.md`. Render a summary header then each finding as a structured card:

```
## Review Findings

**<N> findings** | <critical-count> Critical | <should-count> Should Have | <may-count> May Have | <nitpick-count> Nitpick

---

**1.** [<Priority>] <Short description>
*Section: <section name>* | *<Category>* | Confidence: **<score>%**
> <1-2 sentence explanation of the issue>
> *Suggestion:* <1 sentence recommended change>

---

**2.** [<Priority>] <Short description>
*Section: <section name>* | *<Category>* | Confidence: **<score>%**
> <1-2 sentence explanation of the issue>
> *Suggestion:* <1 sentence recommended change>

---

> **Actions:** **a** accept | **r** reject | **e** edit | **s** skip — by number
> Example: `a-1,4,5 r-2 e-3 s-6`
> Also: `a-all` | `details <N>` | `done`
```

The user responds with compact syntax: `a-1,4,5 r-2 e-3`

### Step 3: Process Results

After the user responds inline, process each finding:

- **`accepted`** -> Post to platform or produce manual comment file:
  - Confluence: `mcp__atlassian-confluence__confluence_add_comment`
  - Google Docs: do **not** post via MCP (unreliable). Instead, collect all accepted comments and produce a markdown file at `.temp/docs-review/<doc-title>-comments.md` listing each comment with its target section/paragraph and content. Present the file path and ask the user to add comments manually.
- **`rejected`** -> Discard
- **`edit`** -> Handle in edit loop (Step 4)
- **`skipped`** -> Defer, do not post

Write `results.json` to the session directory for traceability.

Do NOT edit the document content itself. This stage posts review comments only.

### Step 4: Edit Loop

If any findings were marked for edit, handle them one at a time:

```
## Edit Finding <N>

**Current:**
> <full finding body>

**Edit instructions?** (type your changes, or `skip` to defer)
```

After the user provides instructions:
1. Regenerate the comment based on the user's instructions
2. Show the regenerated finding in the same card format
3. Ask: **accept** or **edit again**
4. Once resolved, move to the next edit item

After all edits are resolved, if any items are still pending, re-render the remaining list and prompt again. Repeat until all items are `accepted` or `rejected`.

### Summary

After all rounds complete, display:

```text
## Interactive Document Review Summary

Platform: [Confluence | Google Docs]
Document: <title>
Rounds: N

- **Accepted:** N
- **Rejected:** N
- **Edited:** N
- **Skipped:** N
- **Posted to platform:** N (Confluence only)
- **Manual comment file:** [path | N/A] (Google Docs only)
```

If `--verbosity detailed` is set, also produce a markdown review artifact with all findings (accepted and rejected) for reference.
