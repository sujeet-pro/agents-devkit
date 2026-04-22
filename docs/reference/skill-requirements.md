---
title: 'requirements'
description: '|'
skill_name: requirements
category: standalone
---
# requirements — iterative requirement gathering

A continuous Q&A session that converts "I want X" into a confirmed requirements doc.

## When to use

- Right after `@adk:context-gather` (a.k.a. `adk-context-gather`) finishes (or skipped if no links).
- Before any spec, design, or implementation.
- When requirements are vague, contradictory, or assumed.

## When NOT to use

- The requirements are already in a complete, confirmed Jira ticket / spec / PRD — just read it.
- The work is purely exploratory ("show me what's possible") — use `@adk:plan-research` instead.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | `.temp/task-<slug>/` |
| `<context.md>` | optional | Output of context-gather; used to inform questions |
| `--auto` | optional | Default the most-conservative answer to every question, then ask user to confirm |

## Workflow

1. **Phase 1 validator.** `.temp/task-<slug>/` exists. Read `context.md` if present.
2. **Restate the prompt** in your own words. One sentence. Confirm: "yes/no/refine".
3. **One question at a time** (per `references/clarifying-questions.md`). Capture the answer in `requirements.md` as you go.
4. **Iterate.** When you think requirements are complete, summarize back to user. They say "yes" or "missing X".
5. **Phase 4 validator.** `requirements.md` has all required sections (see `references/artifact-format.md`); user confirmed.
6. Hand off to `@adk:scoping` (a.k.a. `adk-scoping`).

## Required sections in `requirements.md`

- **Outcome** — what does success look like? (one sentence)
- **Users** — who benefits? (one sentence per user type)
- **Triggers** — when does this happen? (events / conditions)
- **Behavior** — what does the system do? (3-7 bullets)
- **Inputs / outputs** — data flowing in / out
- **Success measures** — how do we know it works? (testable)
- **Must-haves** — bullet list (P0)
- **Nice-to-haves** — bullet list (P1+)
- **Explicit non-goals** — bullet list ("we are NOT building X")
- **Edge cases** — error conditions, empty / max / overflow / unauthorized
- **Constraints** — technical, business, time, regulatory
- **Open questions** — unresolved (escalate to scoping or human owner)

## Mode

`auto` only. Reviewing or fixing requirements is the job of `scoping` and downstream skills.

## Output

`.temp/task-<slug>/requirements.md` per the artifact format. Plus a one-paragraph summary in chat.

## Anti-patterns

- Asking 5 questions in one turn. Iterate one at a time.
- Producing a 50-bullet must-haves list. P0 should be 3-7 items max.
- Forgetting non-goals. Half of all requirements failures are about what was NOT in scope.
- Letting "should" requirements (vague) ride. Convert to "MUST" or "MAY" with a measurable signal.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Iterative loop diagram |
| `references/modes.md` | auto only |
| `references/persona.md` | The requirements interviewer |
| `references/workflow.md` | Detailed Q-loop |
| `references/clarifying-questions.md` | The 12-question default-ask script |
| `references/output-format.md` | Final summary shape |
| `references/artifact-format.md` | `requirements.md` shape |
| `references/validator.md` | Four-phase gate |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked examples |
| `references/interaction-contract.md` | Synced from canonical |
