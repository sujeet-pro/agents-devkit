---
title: Advisor strategy
description: The plan → clarify → present → defer → execute → validate → report wrapper every skill composes. Reference — Anthropic's "advisor strategy" blog post.
order: 7
---

# Advisor strategy

> Reference: [The advisor strategy](https://claude.com/blog/the-advisor-strategy) — Anthropic.

Every adk skill wraps `shared/advisor.md`. The shape: **understand → clarify → present options → defer → execute → validate → report**. Never execute without going through it.

## The seven phases

### A. Understand

1. Restate the user's goal in one sentence. Quote the input.
2. Identify the intent verb (implement / review / investigate / document / sync / explain / improve / setup).
3. Identify entities mentioned: repo, service, PR, ticket, dashboard, experiment, dataset, channel, user.
4. Resolve entities against `~/.config/adk/overrides.yaml` + `<repo>/.adk/overrides.yaml`. Surface ambiguity.

### B. Clarify

[Question-first](./question-first.md) — up to 3 user-facing questions about scope, constraints, scale.

Outcomes:
- User answers → log each as `user-answered` fork.
- User says "you decide" / "I don't know" → load default OR hand off to `/adk-explain`.
- Under `--auto` + silent-default permission: pick recommended default, log as `auto-defaulted` fork; surface in final report.

### C. Present approaches

Present 2–4 viable approaches with **one-line trade-offs each**. Mark one as recommended.

Example for `/adk-implement` against a Jira ticket:

```
1. Vertical slice — minimum viable: ship the happy path now, defer edge cases.
   [Recommended for this team based on your past 8 similar tickets]
2. Full implementation — happy path + 3 edge cases + tests, single PR.
   [Slower but no follow-up debt]
3. Spike first — exploratory PR marked draft, no tests, get reviewer eyes early.
   [If you're unsure about the design]
```

### D. Defer

Wait for user choice.

Default-on-silence only if `overrides.yaml.defaults.question_first.silent: true` for this skill AND the chosen approach is the marked recommendation.

### E. Execute

Run the chosen approach. Skill-specific work happens here. The execution phase lives in the skill's `references/<approach>.md` file or the skill's main workflow. Validate continuously.

### F. Validate

Run the validator gate (`scripts/post-checks.sh` or skill-specific). If validators fail, **stop** and report. Don't paper over with "minor warnings".

### G. Report

Emit `<repo>/.temp/<task-slug>/report.md`. Lead with risk + outcomes + diffs. Always include:
- What got done.
- What got skipped (and why — e.g., "Slack MCP unreachable, scrape skipped").
- What needs human follow-up.
- Decision log location.
- Pointer to next-best skill.

## Hand-off rules

- **To `/adk-explain`**: user uncertainty about which option to pick, or unfamiliar terminology. Pass: the question, the options, the context summary.
- **To `/adk-document`**: any skill that produced findings the user wants written up.
- **To `/adk-sync`**: any skill whose output the user wants published.
- **Between investigate sub-flows**: composite skills (RCA, experiment) call peer sub-flows directly via shared workflow files.

## Anti-patterns

- Asking 5+ questions upfront. Cap at 3; if you need more, run two rounds.
- Presenting 6 approaches. Cap at 4.
- Picking the default silently without logging it. Every default-on-silence pick must hit the decision log.
- Skipping validation under `--auto`. Validation is non-negotiable.
- Auto-publishing under `--auto`. Shared-state writes are gated by per-invocation confirmation even under `--auto`.

## Why this works

- **Plan → clarify** reduces re-do rate. The 30 seconds spent up front saves 30 minutes later.
- **Present options** turns "ship X" prompts into informed decisions. The user picks based on real trade-offs, not the agent's first guess.
- **Defer** keeps the user in control of consequential choices.
- **Validate** catches failures at the smallest scope, not after a 20-minute downstream cascade.
- **Report** with risk-first ordering surfaces what the user needs to see, not what the agent did most recently.

## Next

- [Decision logs](./decision-logs.md) — how the Q&A turns into training data
- [Plan/Act mode](./plan-act-mode.md) — tool-level enforcement of the plan/execute split
