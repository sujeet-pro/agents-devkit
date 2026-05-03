# `investigate-experiment` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 0 questions

1. **Experiment: `<resolved>` from `statsig.md.common_experiments`. Right one?**
   - _When asked:_ multiple candidates match; OR no match in meta-info (so we're inferring).
   - _Default under `--auto`:_ pick the verified candidate; if none and the literal id is given, use it as `inferred`.

2. **Window: `<resolved>`. OK?**
   - _When asked:_ no `--window` flag.
   - _Default under `--auto`:_ `since experiment_start`.

3. **Guardrails: `<list>`. OK?**
   - _When asked:_ `statsig.md.exposure_metric_conventions.guardrail_metrics` is unset.
   - _Default under `--auto`:_ `[error_rate, p99_latency_ms]`.

## Phase 2 questions

4. **About to make 3 parallel calls (Statsig pulse + Mixpanel + DD). Run?**
   - _When asked:_ only under `-i`. Under `--auto`, run.

## Phase 3 questions

5. **Mixpanel disagrees with Statsig direction by >50%. Continue with verdict (iterate) OR pause to investigate divergence first?**
   - _When asked:_ disagreement detected.
   - _Default under `--auto`:_ continue with verdict = `iterate` and surface probes in the report. Operator can run probes and re-invoke.

## Phase 4 questions

6. **Verdict: `<ship|iterate|kill>`. Reasoning: `<rubric inputs>`. Agree, or override?**
   - _When asked:_ only under `-i`. Under `--auto`, the rubric output is final.

## Phase 5 questions

7. **Report ready. Anything to redo?**
   - _Default under `--auto`:_ `(no)`.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered earlier, don't re-ask.
- Don't ask "are you sure?" before a read-only call.
- NEVER ask "should I ship the gate?" — this skill never ships; it only recommends.
