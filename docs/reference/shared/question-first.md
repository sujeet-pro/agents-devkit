---
title: 'shared/question-first'
description: '- **≤3** user-facing questions per skill invocation (only applies in `-i` mode).'
source: 'shared/question-first.md'
group: 'shared'
order: 5602
---
# shared/question-first

> Source: `shared/question-first.md`

# shared/question-first.md — pre-execution interrogation contract

> Default mode for every skill is **auto** — the agent does NOT pause for clarifying questions; it picks the recommended default for each fork and logs the choice. The user opts into interactive mode with **`-i`** (or `--interactive`), which actually waits for answers. In both modes, every fork is recorded — that's what feeds `/adk-improve`.
>
> **Why auto is the default:** the questions are still there (the agent walks the same list internally), but they happen silently against the user's prior decision log + sensible recommendations. Users get out of the way unless they ask to be involved.

## Hard cap

- **≤3** user-facing questions per skill invocation (only applies in `-i` mode).
- If you need more, run a second round AFTER showing partial results from the first round.
- In auto mode (default): 0 user-facing questions; the agent narrates each decision instead so the user can stop / correct.

## Question types (pick at most 3, in this order of priority)

### 1. Goal restatement (always)

"I understand you want to **[restated goal in one sentence]**. Is that right?"

- Yes → proceed.
- No → user re-states, re-loop ONCE. If still ambiguous → hand to `/adk-explain`.

This is one of your three questions only if the restatement is non-trivial. For obvious goals ("review PR #123"), skip and proceed.

### 2. Scope check

"Smallest version that helps you ship today?"

- Asks the user to narrow scope. Defaults from `core.yaml.defaults.<skill>.scope` if set.
- For `/adk-implement`: vertical slice vs full vs spike?
- For `/adk-investigate`: just this incident vs incident + prior similar?
- For `/adk-document`: one-pager vs full doc?

### 3. Constraint check

"Constraints I should know? (deadline / blocker / specific reviewer / can't touch X)"

- Cheap to ask; often unblocks downstream questions.
- Recorded constraints become decision-log entries used for future defaults.

### 4. Scale check (when implied by input)

When the task implies non-trivial scale (touching N files, processing N rows, fanning out to N services), surface a concrete count. Two options:

```
"This task likely touches ~12 files across the BFF + 2 services. Want me to verify
scale before planning?
  [verify] run `gh pr diff --stat` + repo grep to confirm
  [proceed] estimate is good enough
  [other] tell me how to estimate"
```

- On `verify`: run the named programmatic check (script or MCP query). Report numbers. Then proceed to approach presentation.
- This is the ONLY question type where the agent runs a side-effect (a read query) during the question phase.

### 5. Challenge (only fires conditionally)

When the agent detects the task may be unnecessary or redundant, surface it ONCE — never twice in the same invocation:

- "is this actually needed? <shorter-alternative>?"
- Example: user says "review PR #123" but the PR is already approved by 2 reviewers — challenge: "PR #123 has 2 approvals. Want a fresh pass or just a sanity check on the last commit?"
- Example: user says "implement <ticket>" but `grep`-ing the repo shows the feature already exists — challenge: "Found X that may already cover this. Update existing or build new?"

## How to ask

- **One question at a time**, not a wall.
- **Multiple-choice when possible**, free-form when not. Multiple-choice answers are easier to log + learn from.
- **Show the default** in the recommendation line ("[Recommended: X because Y from your past decisions]").
- **Plain English**, no jargon. If jargon is required, define it inline.
- **No leading questions**. Don't say "you probably want X, right?" — say "options are X, Y, Z — pick one".

## Mode → behavior

| Invocation flag | Behavior |
|---|---|
| (none — **default**) | Auto. Pick the recommended default for each fork. Log every choice as `auto-defaulted`. Narrate the chosen path as the skill runs. Surface "I assumed X, Y, Z" in the final summary so the user can correct. |
| `-i` / `--interactive` | Ask up to 3 user-facing questions per the contract above. Each answer is logged as `user-answered` — the highest-value training signal. |
| `-i --depth deep` (some skills) | Allow the second round of questions after partial results are shown. |

Posting to shared state (Slack / PR comments / Jira / Confluence) still requires per-invocation confirmation — that gate is independent of `-i` and is set by the constitution (§I.4). The skill surfaces "About to post N comments to PR X — proceed?" before transmission, in BOTH modes.

When the agent proceeds in auto mode:
- Log every skipped question + chosen default to the decision log as `fork_type: auto-defaulted`.
- Narrate each non-trivial decision live: `[chose: vertical-slice, reason: prior 3 tickets in this repo picked vertical-slice]`.
- Surface "I assumed X, Y, Z" in the final summary; the user can correct, which becomes a high-value `user-corrected` training signal next time.

## Recording (the part that's training data)

For each question asked + answered, append one line to `~/.agents-devkit/improve/learning/decisions.jsonl`:

```json
{"ts":"2026-05-18T14:22Z","skill":"adk-implement","sub_flow":"from-jira",
 "fork_id":"scope","fork_type":"user-answered",
 "question":"smallest version that helps you ship today?",
 "options":["vertical-slice","full","spike"],
 "default_offered":"vertical-slice",
 "user_chose":"full","reason_if_given":"need it for demo Monday",
 "repo":"storefront-bff","task_slug":"implement-SF-1234"}
```

For default-on-silence (`--auto`):

```json
{"ts":"...","skill":"...","fork_id":"scope","fork_type":"auto-defaulted",
 "default_chosen":"vertical-slice","evidence":"3 prior identical-shape Jira tickets in this repo chose vertical-slice"}
```

These two `fork_type`s are what `/adk-improve` consumes.

## Anti-patterns

- Yes/no questions when there are real alternatives. "Do you want me to proceed?" is not a question.
- Recap questions that just re-ask what the user already said. The agent should be summarizing, not re-asking.
- Hidden assumptions baked into the question wording. ("Should I use vitest as usual?" assumes "as usual" — log assumption separately.)
- Asking for permission for non-shared-state actions. The question-first phase shapes WHAT the agent does, not WHETHER. Shared-state confirms come in a separate gate (constitution §I).
