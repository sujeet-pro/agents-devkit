# `investigate-datadog` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in the final report's `Decisions` section.

## Phase 0 questions

1. **Service: `<resolved>` (from `datadog.md.service_aliases`). Right one?**
   - _When asked:_ shorthand resolves to multiple candidates, or the resolved tag isn't in `service_aliases` (so we're inferring).
   - _Default under `--auto`:_ pick the verified-aliased candidate; if none, use the literal shorthand and mark `inferred`.

2. **Time window: `<resolved>`. OK?**
   - _When asked:_ no `--time` and the prompt has no NL window phrase.
   - _Default under `--auto`:_ `datadog.md.default_window` (typically `last 1h`).

3. **Environment: `<resolved>`. OK?**
   - _When asked:_ never (don't ask) under `--auto` unless the user's prompt explicitly mentioned a non-`prod` env.
   - _Default under `--auto`:_ `datadog.md.default_env` (typically `prod`). Cross-env (`*`) requires explicit `--env "*"` opt-in.

4. **`--use`: I'm picking `<investigate|dashboard-summary|alert-triage>` because `<reason>`. Override?**
   - _When asked:_ the prompt is ambiguous (e.g. mentions a dashboard name AND a metric).
   - _Default under `--auto`:_ pick by the decision tree in `how-it-works.md`.

## Phase 2 questions

5. **Built query: `<query>`. Run it?**
   - _When asked:_ only under `-i`. Under `--auto`, run silently.
   - _Default under `--auto`:_ run.

6. **Dashboard tile count: `<N>` tiles. Summarize all, or top-K by anomaly score?**
   - _When asked:_ dashboard has > 12 tiles.
   - _Default under `--auto`:_ summarize all if ≤12; top-12 by anomaly score otherwise.

## Phase 3 questions

7. **Found `<N>` follow-up queries. Run any now?**
   - _When asked:_ only under `-i`. Under `--auto`, list them in the report and stop.
   - _Default under `--auto`:_ list, do not run. The operator decides.

## Phase 4 questions

8. **Report ready. Anything to redo?**
   - _Default under `--auto`:_ `(no)`. Surface a one-line result; offer depth.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers (resolved entity ≠ ambiguous entity).
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered the same question earlier in this session, don't re-ask.
- Don't ask "are you sure?" before a read-only query — there's nothing to be sure about.
