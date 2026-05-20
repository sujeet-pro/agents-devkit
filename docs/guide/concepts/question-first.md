---
title: Question-first
description: The mandatory ≤3-question phase that runs before any skill execution. Every Q&A is training data for /adk-improve.
order: 6
---

# Question-first execution

Every skill goes through this before any work happens.

## Why

Most skill failures come from misunderstood scope or unstated constraints. A 30-second clarifying exchange up front saves a 30-minute redo later. And — critically — **every user answer is training data**: it teaches `/adk-improve` what your real defaults are.

Source: `shared/question-first.md`.

## The contract

- **Up to 3 user-facing questions** per skill invocation.
- If you need more, run a second round AFTER showing partial results.
- Each question is logged to `~/.agents-devkit/improve/learning/decisions.jsonl`.

## Question types (in priority order)

### 1. Goal restatement (when ambiguous)

"I understand you want to **[restated goal]**. Is that right?"

Only one of your 3 questions if the goal isn't obvious. For unambiguous prompts ("review PR #123"), skip.

### 2. Scope check

"Smallest version that helps you ship today?"

- `/adk-implement`: vertical-slice vs full vs spike?
- `/adk-investigate`: just this incident vs incident + prior similar?
- `/adk-document`: one-pager vs full doc?

Recommendation derived from `defaults.<skill>.scope` in your overrides.

### 3. Constraint check

"Constraints I should know? (deadline / blocker / specific reviewer / can't touch X)"

Surfaces implicit constraints early. Cheap to ask, often unblocks downstream questions.

### 4. Scale check (when implied)

When the task implies non-trivial size (touching N files, processing N rows, fanning out to N services), the skill surfaces a concrete count BEFORE work:

```
"This task likely touches ~12 files across the BFF + 2 services. Want me to verify
scale before planning?
  [verify] run `gh pr diff --stat` + repo grep to confirm
  [proceed] estimate is good enough
  [other] tell me how to estimate"
```

On `verify`, the agent runs a read-only programmatic check (script or MCP query), reports numbers, then proceeds.

This is the ONLY question type where the agent runs a side-effect during the question phase — and only read-only.

### 5. Challenge (conditional)

When the agent detects the task may be unnecessary or redundant, it surfaces ONCE — never twice:

- "PR #123 has 2 approvals. Want a fresh pass or last-commit-only?"
- "Found `discounts.applyMultiple` that may already cover this. Update existing or build new?"

## How to ask

- **One question at a time**, not a wall.
- **Multiple-choice when possible** — easier to log + learn from.
- **Show the default** in the recommendation line: `[Recommended: X because Y from your past 5 decisions]`.
- **Plain English** — no jargon; define inline if unavoidable.
- **No leading questions** — present options, don't lead.

## Default-on-silence

The agent may proceed without your input only if ALL of:

1. `--auto` mode is active.
2. `overrides.yaml.defaults.question_first.silent: true` is set for this skill (or globally).
3. The chosen default is the marked recommendation (not a tie-broken arbitrary pick).

When the agent proceeds silently:
- It logs every skipped question + chosen default to the decision log as `fork_type: auto-defaulted`.
- The final report says "I assumed X, Y, Z" — your corrections become high-value training signal for future `--auto` runs.

## What gets logged

For each user-answered question, one JSONL line:

```json
{"ts":"2026-05-18T14:22Z","skill":"adk-implement","sub_flow":"from-jira",
 "fork_id":"scope","fork_type":"user-answered",
 "question":"smallest version that helps you ship today?",
 "options":["vertical-slice","full","spike"],
 "default_offered":"vertical-slice",
 "user_chose":"full","reason_if_given":"demo Monday",
 "repo":"storefront-bff","task_slug":"implement-SF-1234"}
```

`/adk-improve` reads these and detects patterns (e.g., "user overrode `scope: vertical-slice` 5+ times in favor of `full` — propose changing the default").

## Anti-patterns

- Yes/no questions when there are real alternatives. "Do you want me to proceed?" is not a question.
- Recap questions that re-ask what the user already said.
- Hidden assumptions baked into the question wording.
- Asking permission for non-shared-state actions (those go through the shared-state gate, not the question phase).

## Next

- [Advisor strategy](./advisor-strategy.md) — the broader plan→clarify→execute wrapper question-first is the first step of
- [Decision logs](./decision-logs.md) — how Q&A becomes training data
