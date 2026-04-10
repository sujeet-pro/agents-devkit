# Inline Interaction Protocol

Use inline interaction in the agent conversation as the default and primary interaction method.

## Interaction Flags

Skills that support interactive workflows should prefer:

| Flag | Description |
|------|-------------|
| `--auto` | Skip human confirmations and proceed with recommended defaults |

When `--auto` is not set, interactions are rendered inline in conversation.

## Intent Confirmation

Render:

```text
## Confirm Intent

**Goal**: <one-line restatement>
**Reasoning**:
- <bullet 1>
- <bullet 2>
**Skills**: <skill list with rationale>
**Tools/MCPs**: <list with availability>
**Complexity**: <level> — <justification>

> Reply: **approve**, **edit: <changes>**, **simplify**, or **cancel**
```

## Approach Selection

Render:

```text
## Select Approach

1. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>) [recommended]
2. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>)
3. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>)

> Reply: **1**, **2**, **3**, **mix: <instructions>**, or **discuss**
```

## Plan Approval

Render:

```text
## Approve Plan

Wave 1:
1. <task>
2. <task>

Wave 2:
3. <task>

> Reply: **approve**, **add: <task>**, **remove: <number>**, or **cancel**
```

## Review Findings

For review-style triage, present all findings numbered and then prompt for batch disposition:

```text
## Review Findings

> Actions: **a** accept | **r** reject | **e** edit | **s** skip — by number
> Separate action groups with semicolons.
> Example: `a-1,4;r-2,6;e-3,5`
> Also: `a-all` | `details <N>` | `done`
> Note: Praise comments are auto-accepted — no action needed.
```

### Batch Action Processing Order

1. **Accept** items first — post each accepted comment to the PR immediately as an inline comment (do not batch; post as soon as accepted so the author sees feedback incrementally).
2. **Reject** items — discard silently.
3. **Skip** items — defer to `.temp/` for future sessions.
4. **Edit** items — enter the **Edit Loop** (see below).

### Edit Loop

Process edit-marked items **one at a time**, in the order given:

```text
## Edit Finding <N>

**Current:**
> <full finding body>

**Edit instructions?** (describe changes, or `skip` to defer)
```

After the user provides instructions:
1. Regenerate the comment based on the user's instructions.
2. Re-run auto-validation on the regenerated comment.
3. Show the regenerated finding in the same card format.
4. Prompt: `[a] approve | [r] reject | [e] edit again`
5. If **approve** — post the comment immediately as an inline PR comment, then move to the next edit item.
6. If **reject** — discard, move to the next edit item.
7. If **edit again** — repeat from step 1.
8. This loop continues until the comment is either approved or rejected.

After all edit items are resolved, display the final Review Summary.

## Progress Dashboard

For long execution, show checkpoint-style inline progress:

```text
## Progress

Wave 1: [completed]
Wave 2: [running]
Wave 3: [pending]
```
