---
name: interaction
description: "adk - [helper] [guideline] Inline interaction protocols for intent confirmation, approach selection, plan approval, review findings, and progress dashboards."
user-invocable: false
allowed-tools: [Read]
workflow-tier: helper
maturity: stable
---

# Inline Interaction Protocol

Claude Code's Bash tool does not provide an interactive TTY, so all interactivity must happen via the agent itself — rendering structured prompts and processing compact user replies.

## Interaction Flags

Skills that support interactive workflows accept this flag:

| Flag | Description |
| ------ | ----------------------------------------------------------------------------------------- |
| `--auto` | **Automatic** — skip human confirmations and proceed with recommended defaults |

When `--auto` is not set, all interaction is rendered inline in the conversation (the default). When no arguments are provided, the skill enters interactive mode — asking the user for each required parameter with options to pick from, where the first option is the recommended choice based on prompt analysis.

---

## Intent Confirmation

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

## Approach Selection

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

## Plan Approval

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

## Review Findings

This is the most complex interaction. Only show findings with confidence >= 80%.

### Rendering Format

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

> **Actions:** **a** accept | **r** reject | **e** edit | **s** skip — by number
> Example: `a-1,4,5 r-2 e-3 s-6`
> Also: `a-all` | `details <N>` | `done`
```

### User Input Syntax

- `a-1,4,5` — accept findings 1, 4, 5
- `r-2,6` — reject findings 2, 6
- `e-3` — mark finding 3 for edit (prompt for edit instructions next)
- `s-7` — skip/defer finding 7
- `a-all` — accept all remaining pending items
- `details N` — show the full body of finding N, then re-prompt
- `done` — finalize (only if no pending items remain)

### Edit Loop

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

### Summary After All Items Resolved

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

## Progress Dashboard

For execution progress, render inline updates at wave boundaries:

```
## Progress

Wave 1: [completed] 2/2 tasks done
Wave 2: [running] 1/3 tasks done, 2 pending
Wave 3: [pending]
```

No user interaction needed — this is display-only. Update by re-rendering after each wave completes.
