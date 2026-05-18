# shared/question-first.md — mandatory pre-execution interrogation

> Every skill goes through this before any work happens. Even under `--auto`, the agent records what it *would* have asked and what defaults it picked. **Every user answer is training data.**

## Hard cap

- **≤3** user-facing questions per skill invocation.
- If you need more, run a second round AFTER showing partial results from the first round.

## Question types (pick at most 3, in this order of priority)

### 1. Goal restatement (always)

"I understand you want to **[restated goal in one sentence]**. Is that right?"

- Yes → proceed.
- No → user re-states, re-loop ONCE. If still ambiguous → hand to `/adk-explain`.

This is one of your three questions only if the restatement is non-trivial. For obvious goals ("review PR #123"), skip and proceed.

### 2. Scope check

"Smallest version that helps you ship today?"

- Asks the user to narrow scope. Defaults from `overrides.yaml.defaults.<skill>.scope` if set.
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

## Default-on-silence

The agent may proceed with the recommended default WITHOUT user input only if ALL of:

1. `--auto` mode is active.
2. `overrides.yaml.defaults.question_first.silent: true` is set for this skill (or globally).
3. The chosen default is the marked recommendation, NOT a tie-broken arbitrary pick.

In all other cases, **wait for user input**. The user's `--auto` is a "go fast on execution"; it doesn't waive clarification.

When the agent proceeds silently:
- Log every skipped question + chosen default to the decision log as `fork_type: auto-defaulted`.
- Surface "I assumed X, Y, Z" in the final report. The user can correct, and that correction becomes a high-value training signal for future `--auto` runs.

## Recording (the part that's training data)

For each question asked + answered, append one line to `~/.config/adk/learning/decisions.jsonl`:

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
