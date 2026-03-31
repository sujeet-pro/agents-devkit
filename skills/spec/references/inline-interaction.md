# Inline Interaction Protocol

Claude Code's Bash tool does not provide an interactive TTY, so Textual-based TUI scripts cannot run inside Claude Code. This reference defines interaction modes that replace TUI launches.

## Interaction Flags

Skills that support interactive workflows accept these flags:

| Flag | Description |
|------|-------------|
| `-i` | **Inline interactivity** (default) — render interactions directly in the conversation |
| `-tui` | **TUI interactivity** — user runs the TUI in a separate terminal, agent processes results |

When neither flag is provided, default to `-i` (inline). The `-tui` flag writes `items.json` and prints the terminal command for the user to run externally.

These flags replace the old `--mode interactive` parameter for controlling *how* the interaction happens (inline vs TUI). The `--mode` parameter still controls *what kind* of review runs (standard, interactive, followup, auto).

## Mid-Flow TUI Switch

At any point during inline review, the user can type **`tui`** to switch to TUI mode for the remaining items. When this happens:

1. Write the current pending items to a new `items.json` in the session directory
2. Print the TUI command for the user to run in a separate terminal
3. Wait for the user to return and say they're done
4. Read `results.json` and continue processing

This is useful when there are many items and the user wants richer navigation.

---

## Inline Mode (`-i`)

Render the interaction directly in the conversation. The user responds with compact syntax.

### Intent Confirmation (replaces `intent_confirm.py`)

Render:

```
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

Process the user's reply and continue.

### Approach Selection (replaces `approach_select.py`)

Render:

```
## Select Approach

1. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>) [recommended]
   Pros: <pros> | Cons: <cons>

2. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>)
   Pros: <pros> | Cons: <cons>

3. **<Name>** — <summary> (Risk: <level>, Effort: <estimate>)
   Pros: <pros> | Cons: <cons>

> Reply: **1**, **2**, **3**, **mix: <instructions>**, or **discuss**
```

### Plan Approval (replaces `plan_approve.py`)

Render:

```
## Approve Plan

**Wave 1** (parallel):
  1. <task> (~effort) [files: ...]
  2. <task> (~effort) [files: ...]

**Wave 2** (after wave 1):
  3. <task> (~effort) [files: ...]

> Reply: **approve**, **add: <task description>**, **remove: <number>**, or **cancel**
```

If the user adds/removes tasks, re-render the updated plan and ask again.

### Review Findings (replaces `review.py`)

This is the most complex interaction. Only show findings with confidence >= 80%.

#### Rendering Format

Render a **summary header** first, then each finding as a structured card:

```
## Review Findings

**<N> findings** | <blocker-count> Blocker | <critical-count> Critical | <should-count> Should Have | <may-count> May Have | <nitpick-count> Nitpick

---

**1.** [<Priority>] <Short, specific title>
*<file>:<line>* | *<Principle>* | *<Guideline name>* | Confidence: **<score>%**
> <1-2 sentence issue explanation>
> *Fix:* <1 sentence suggested fix>

---

**2.** [<Priority>] <Short, specific title>
*<file>:<line>* | *<Principle>* | *<Guideline name>* | Confidence: **<score>%**
> <1-2 sentence issue explanation>
> *Fix:* <1 sentence suggested fix>

---

...

> **Actions:** **a** accept | **r** reject | **e** edit | **s** skip — by number
> Example: `a-1,4,5 r-2 e-3 s-6`
> Also: `a-all` | `details <N>` | `tui` (switch to TUI) | `done`
```

#### Rendering Rules

- **Summary header**: Always show the total count and breakdown by priority. This gives the user an instant overview before reading individual items.
- **Priority in brackets**: Bold, e.g. `[Blocker]`, `[Critical]`, `[Should Have]`
- **Location**: Italicized file:line
- **Principle + Guideline**: Italicized, names only (not full descriptions). E.g. *Correctness* | *coding-guidelines/backend-general: null safety*
- **Confidence**: Bold score, e.g. Confidence: **92%**
- **Issue**: 1-2 sentences in a blockquote — enough to understand the problem without expanding details
- **Fix**: Italicized label, 1 sentence — the actionable takeaway
- **Horizontal rules** (`---`) between findings for visual separation
- **Confidence filter**: Only show findings with confidence >= 80%. If the skill's `--confidence` flag overrides this, use that threshold instead.

#### For Document Reviews (mode: doc)

Adapt the format for document findings:

```
**1.** [<Priority>] <Short description>
*Section: <section name>* | *<Category>* | Confidence: **<score>%**
> <1-2 sentence explanation of the issue>
> *Suggestion:* <1 sentence recommended change>
```

#### User Input Syntax

- `a-1,4,5` — accept findings 1, 4, 5
- `r-2,6` — reject findings 2, 6
- `e-3` — mark finding 3 for edit (prompt for edit instructions next)
- `s-7` — skip/defer finding 7
- `a-all` — accept all remaining pending items
- `details N` — show the full body of finding N (all sections from the review-comment-template), then re-prompt
- `tui` — switch to TUI mode for remaining items (see Mid-Flow TUI Switch)
- `done` — finalize (only if no pending items remain)

#### Edit Loop

When the user marks items for edit (`e-N`), handle them one at a time:

```
## Edit Finding <N>

**Current:**
> <full finding body — all sections>

**Edit instructions?** (type your changes, or `skip` to defer)
```

After the user provides instructions:
1. Regenerate the finding based on the edit prompt
2. Show the regenerated finding in the same card format
3. Ask: **accept** or **edit again**
4. Once resolved, if more edits remain, move to the next one

After all edits are resolved, show any remaining unacted items and re-prompt.

#### Summary After All Items Resolved

```
## Review Complete

| Action | Count |
|--------|-------|
| Accepted | N |
| Rejected | N |
| Edited | N |
| Skipped | N |
```

Then proceed with posting/processing accepted items per the skill's instructions.

### Progress Dashboard (replaces `progress_dashboard.py`)

For execution progress, render inline updates at wave boundaries:

```
## Progress

Wave 1: [completed] 2/2 tasks done
Wave 2: [running] 1/3 tasks done, 2 pending
Wave 3: [pending]
```

No user interaction needed — this is display-only. Update by re-rendering after each wave completes.

---

## TUI Mode (`-tui`)

When the user passes `-tui`, or types `tui` during inline review:

1. Write the `items.json` file to the session directory
2. Tell the user:

```
Session ready. Run in a separate terminal:

    python3 <skill_dir>/scripts/tui/adk-review-pr.py <session_dir>

Tell me when you're done and I'll process the results.
```

3. When the user returns, read `results.json` from the session directory
4. Process results normally (accepted -> post, rejected -> discard, edit -> regenerate)
5. If edits exist, write a new `items.json` with regenerated items and tell the user to re-launch
6. Repeat until all items are resolved

---

## Writing results.json (Inline Mode)

When using inline mode, after processing user actions, write the same `results.json` format that the TUI would produce. This keeps the downstream processing identical:

```json
{
  "results": [
    {"id": "finding-1", "action": "accepted"},
    {"id": "finding-2", "action": "rejected"},
    {"id": "finding-3", "action": "edit", "prompt": "user's edit instructions"}
  ],
  "summary": {
    "total": 3,
    "accepted": 1,
    "rejected": 1,
    "edit": 1,
    "skipped": 0,
    "pending": 0
  }
}
```
