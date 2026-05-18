# shared/advisor.md — the advisor-strategy wrapper

> Every skill includes this. The shape: **understand → clarify → present options → defer → execute → validate → report**. Never execute without going through it.

Reference: https://claude.com/blog/the-advisor-strategy

## Phases

### A. Understand

1. Restate the user's goal in one sentence. Quote the input.
2. Identify the **intent verb** (implement / review / investigate / document / sync / explain / improve / setup).
3. Identify entities mentioned: repo, service, PR, ticket, dashboard, experiment, dataset, channel, user.
4. Resolve entities against `~/.config/adk/overrides.yaml` + `<repo>/.adk/overrides.yaml` if present. Surface ambiguity.

### B. Clarify (the question-first phase)

Apply `shared/question-first.md` in full. Cap at 3 user-facing questions.

Outcomes:
- User answers → log each answer to `~/.config/adk/learning/decisions.jsonl` as a `user-answered` fork.
- User says "you decide" / "I don't know" → either (a) load default from overrides, or (b) hand off to `/adk-explain` with the topic and resume.
- Under `--auto`: pick the recommended default, log it as an `auto-defaulted` fork; surface what was assumed in the final report.

### C. Present approaches

Present 2–4 viable approaches with **one-line trade-offs each**. Mark one as recommended (based on overrides + decision-log history + repo conventions). Wait for choice.

Example (for `/adk-implement` against a Jira ticket):

```
1. Vertical slice — minimum viable: ship the happy path now, defer edge cases to a follow-up.   [Recommended for this team based on your past 8 similar tickets]
2. Full implementation — happy path + 3 edge cases + tests, single PR.   [Slower but no follow-up debt]
3. Spike first — exploratory PR marked draft, no tests, get reviewer eyes early.   [If you're unsure about the design]
```

### D. Defer

Wait. Default-on-silence only if `overrides.yaml.defaults.question_first.silent: true` for this skill AND the chosen approach is the marked recommendation.

### E. Execute

Run the chosen approach. The execution phase lives in the skill's `references/<approach>.md` file or the skill's main workflow. Validate continuously (typecheck/lint/test for code skills; cross-source correlation for investigate; format conversion for sync).

### F. Validate

Run the validator gate (`scripts/post-checks.sh` or skill-specific). If validators fail, **stop** and report. Don't paper over a failure with "minor warnings".

### G. Report

Emit `<repo>/.temp/<task-slug>/report.md`. Lead with risk + outcomes + diffs. Always include:
- What got done.
- What got skipped (and why — e.g., "Slack MCP unreachable, scrape skipped").
- What needs human follow-up.
- Decision log location.
- Pointer to next-best skill (e.g., after `/adk-investigate`, suggest `/adk-document --type rca` if the symptom is post-incident).

## Hand-off rules

- **To `/adk-explain`**: user uncertainty about which option to pick, or unfamiliar terminology in the prompt. Pass: the question, the options, the context summary.
- **To `/adk-document`**: any other skill that produced findings the user wants written up.
- **To `/adk-sync`**: any other skill whose output the user wants published.
- **Between investigate sub-flows**: composite skills (RCA, experiment) call peer sub-flows directly via shared workflow files.

## Anti-patterns

- Asking 5+ questions upfront. Cap at 3. If you need more, run two rounds.
- Presenting 6 approaches. Cap at 4.
- Picking the default silently without logging it. **Every** default-on-silence pick must hit the decision log.
- Skipping validation under `--auto`. Validation is non-negotiable.
- Auto-publishing under `--auto`. Shared-state writes are gated by per-invocation confirmation even under `--auto`, per constitution §I.
