# `investigate-mixpanel` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in the report's `Decisions` section.

## Phase 0 questions

1. **Event names: I see `<list>`. Are these the right events?**
   - _When asked:_ any event in the prompt isn't in `mixpanel.md.common_events` AND isn't in the cached Lexicon.
   - _Default under `--auto`:_ confirm via Lexicon; if not found, run anyway and flag any zero-count result as "possible typo — verify event name".

2. **Time window: `<resolved>`. OK?**
   - _When asked:_ no `--time` flag and no NL window in the prompt.
   - _Default under `--auto`:_ `mixpanel.md.default_window` (typically `last 7d`).

3. **Funnel / cohort id: `<resolved>` from `common_funnels` / `common_cohorts`. Right?**
   - _When asked:_ multiple candidates match; OR the prompt gave ad-hoc steps that don't match a saved funnel.
   - _Default under `--auto`:_ pick the highest-priority match; if ad-hoc, build it.

4. **`--use`: I'm picking `<usage-summary|funnel|cohort>` because `<reason>`. Override?**
   - _When asked:_ ambiguous prompt (e.g. mentions both a funnel and a cohort).
   - _Default under `--auto`:_ pick by the decision tree.

## Phase 2 questions

5. **Baseline: prior-equal-window or same-period-last-week?**
   - _When asked:_ window is < 7d (where week-alignment doesn't apply).
   - _Default under `--auto`:_ same-period-last-week if window is multi-day; prior-equal-window otherwise.

6. **Step <N> has n=`<count>` (< 100). Continue and flag, or pick a wider window?**
   - _When asked:_ only under `-i`. Under `--auto`, continue and flag.
   - _Default under `--auto`:_ continue, with explicit `Low-traffic warning` in the report.

## Phase 3 questions

7. **Found `<N>` follow-up queries. Run any now?**
   - _When asked:_ only under `-i`. Under `--auto`, list them, do not run.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered earlier in this session, don't re-ask.
- Don't ask "are you sure?" before a read-only query.
