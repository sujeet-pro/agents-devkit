# `investigate-statsig` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 0 questions

1. **Experiment / gate: `<resolved>` from `statsig.md.common_experiments` / `common_gates`. Right one?**
   - _When asked:_ multiple candidates match; OR the named entity isn't in meta-info (so we're inferring).
   - _Default under `--auto`:_ pick the verified-aliased candidate; if none, use the literal name and mark `inferred`.

2. **Time window: `<resolved>`. OK?**
   - _When asked:_ no `--window` flag and `--use` requires one (`audit-log`, `pulse`).
   - _Default under `--auto`:_ `last 60m` for `audit-log`; `since experiment_start` for `pulse`.

3. **`--use`: I'm picking `<...>` because `<reason>`. Override?**
   - _When asked:_ ambiguous prompt (e.g. mentions an experiment AND audit log).
   - _Default under `--auto`:_ pick by the decision tree.

## Phase 2 questions

4. **About to call `<MCP tool>` with args `<args>`. Run?**
   - _When asked:_ only under `-i`. Under `--auto`, run silently.

## Phase 3 questions (for `--use pulse`)

5. **Recommendation: `<ship | iterate | kill>`. Reason: `<rubric inputs>`. Agree, or override with reasoning?**
   - _When asked:_ only under `-i`. Under `--auto`, the rubric output is final and shown in the report's Decisions section.

6. **Sample size `n=<count>` per arm. Power-target unset; assume default (5% MDE @ 80% power) or user-specified?**
   - _When asked:_ no power target in `statsig.md`.
   - _Default under `--auto`:_ assume 5% MDE @ 80% power; flag the assumption.

## Phase 3 questions (for `--use audit-log`)

7. **Found `<N>` entries. Surface all, or top `<K>` by recency / by relevance to symptom?**
   - _When asked:_ N > 25.
   - _Default under `--auto`:_ top 10 by recency (or by abs-time-delta from symptom if symptom timestamp is in scope).

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered earlier in this session, don't re-ask.
- Don't ask "are you sure?" before a read-only call.
