---
title: 'shared/advisor'
description: 'Reference: https://claude.com/blog/the-advisor-strategy'
source: 'shared/advisor.md'
group: 'shared'
order: 5601
---
# shared/advisor

> Source: `shared/advisor.md`

# shared/advisor.md — the advisor-strategy wrapper

> Every skill includes this. The shape: **understand → clarify → present options → defer → execute → validate → report**. Never execute without going through it.

Reference: https://claude.com/blog/the-advisor-strategy

## Phases

### A. Understand

1. Restate the user's goal in one sentence. Quote the input.
2. Identify the **intent verb** (implement / review / investigate / document / sync / explain / improve / setup).
3. Identify entities mentioned: repo, service, PR, ticket, dashboard, experiment, dataset, channel, user.
4. Resolve entities against `~/.agents-devkit/config/overrides.yaml` + `<repo>/.adk/overrides.yaml` if present. Surface ambiguity.

### B. Clarify (the question-first phase)

Apply `shared/question-first.md` in full. Auto by default; `-i` opts into interactive (cap 3 user-facing questions).

Outcomes:
- **Default (auto):** for each fork, pick the recommended default; log as `auto-defaulted`. Narrate each pick: `→ scope=vertical-slice (prior 3 tickets in this repo picked vertical-slice)`.
- **`-i`:** ask each question; user answers logged as `user-answered`. User says "you decide" / "I don't know" → either (a) load default from overrides, or (b) hand off to `/adk-explain` with the topic and resume.

### C. Present approaches

Present 2–4 viable approaches with **one-line trade-offs each**. Mark one as recommended (based on overrides + decision-log history + repo conventions).

- **Default (auto):** print the menu + recommended pick, log the choice, proceed — do not wait. The user can interrupt if the pick is wrong; the menu is shown so they have something to interrupt with.
- **`-i`:** wait for choice.

Example (for `/adk-implement` against a Jira ticket):

```
1. Vertical slice — minimum viable: ship the happy path now, defer edge cases to a follow-up.   [Recommended for this team based on your past 8 similar tickets]
2. Full implementation — happy path + 3 edge cases + tests, single PR.   [Slower but no follow-up debt]
3. Spike first — exploratory PR marked draft, no tests, get reviewer eyes early.   [If you're unsure about the design]
```

In auto mode, the agent picks option 1 and continues with: `→ chose option 1 (vertical-slice).`

### D. Defer

In `-i` mode, wait. In auto mode, this phase is a no-op — the agent already committed to the recommended pick in C and narrated it.

### E. Execute

Run the chosen approach. The execution phase lives in the skill's `references/<approach>.md` file or the skill's main workflow. Validate continuously (typecheck/lint/test for code skills; cross-source correlation for investigate; format conversion for sync).

### F. Validate

Run the validator gate (`scripts/post-checks.sh` or skill-specific). If validators fail, **stop** and report. Don't paper over a failure with "minor warnings".

### G. Report (per `shared/narration.md`)

Throughout phases A–F, the skill **narrates** each non-trivial step live so the user can intervene — phase boundaries, auto-defaulted picks, side effects, refusals, posting confirmations. See `shared/narration.md` for the glyph set + format.

At the end, emit `<task_dir>/report.md` (resolved in Phase 0 per `shared/paths.md`). The exact section list is in `shared/narration.md` — required: TL;DR, Risk/Blockers/Follow-ups (write "none" explicitly if empty), What got done, What got skipped (explicit "none" if empty), Decisions made, Evidence, Next-best action.

Also print a 10-line summary block to the user-facing chat with a pointer to the full `report.md`.

## Hand-off rules

- **To `/adk-explain`**: user uncertainty about which option to pick, or unfamiliar terminology in the prompt. Pass: the question, the options, the context summary.
- **To `/adk-document`**: any other skill that produced findings the user wants written up.
- **To `/adk-sync`**: any other skill whose output the user wants published.
- **Between investigate sub-flows**: composite skills (RCA, experiment) call peer sub-flows directly via shared workflow files.

## Anti-patterns

- Asking 5+ questions upfront. Cap at 3 (only fires in `-i` mode; auto mode asks none).
- Presenting 6 approaches. Cap at 4.
- Picking the default silently without logging AND without narrating it. Every auto-defaulted pick must hit the decision log AND be printed live to the user.
- Skipping validation in auto mode. Validation is non-negotiable in both modes.
- Auto-publishing in auto mode. Shared-state writes (Slack post, PR comment, Confluence update) are gated by per-invocation confirmation regardless of `-i`, per constitution §I.4.
- Treating auto as "silent". Auto != silent. The agent narrates every non-trivial decision so the user can interrupt; it just doesn't WAIT.
