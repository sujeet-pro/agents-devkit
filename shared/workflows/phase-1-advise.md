# workflow: Phase 1 — advise

> The plan/clarify/present phase. Wraps `shared/advisor.md` + `shared/question-first.md`. Mandatory.

## Steps

1. **Summarize the context** in 3–5 bullets (drawn from `task-slug/context.md`).
2. **Identify ambiguity**: list the open questions the agent has after reading context. Cap at 3 user-facing; rest become `auto-defaulted` choices.
3. **Apply `question-first.md`**: ask up to 3 questions. Wait for answers (or proceed silently under `--auto` + `defaults.question_first.silent: true`).
4. **Present approaches**: 2–4 options, one-line trade-off each, one marked recommended (with one-line evidence: "you picked X on the last 3 similar tasks").
5. **Wait for user choice**.
6. **Write the chosen plan** to `<task-slug>/plan.md` — 1-pager: goal, approach, scope, success criteria, risks, rollback.
7. **Log every fork to decisions.jsonl**.

## Plan.md template

```markdown
# plan: <task-slug>

## goal
<one sentence, the user's confirmed restatement>

## approach
<chosen option>: <one-line summary>

## scope
in-scope:
  - <item>
  - <item>
out-of-scope:
  - <item>

## success criteria
1. <testable criterion>
2. <testable criterion>

## risks
- <risk>: <mitigation>

## rollback
<one sentence: how do we undo this if it goes wrong>

## decisions log entries
- scope=full (user-answered)
- test_framework=jest (override-applied from overrides.yaml)
- pr_strategy=single (auto-defaulted, based on 5 prior tasks in this repo)
```

## Recommendation logic

- Read `~/.config/adk/learning/decisions.jsonl` + `summary.md` for prior matching `fork_id`s.
- Read `~/.config/adk/overrides.yaml.defaults.<skill>.*`.
- Read `<repo>/.adk/overrides.yaml.defaults.<skill>.*` (override layer).
- Recommendation = highest-priority match.
- If no prior data: recommendation = the most common cross-user-base default, marked `[no personal history]`.

## Honesty

- If the agent has too little context to recommend, **say so**: "no recommendation — I don't know your team's preference on PR strategy. Pick one and I'll learn."
- If the recommendation is uncertain (< 3 prior matches), mark it `[weak signal]`.
