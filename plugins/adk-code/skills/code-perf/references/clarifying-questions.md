# `code-perf` — clarifying questions

Asked one at a time, only when the answer changes the plan. Under `--auto`, defaults apply silently.

## Phase 0 — prompt expand

1. **Service / endpoint: `<resolved>`. Correct?**
   - _Default under `--auto`:_ resolve via `datadog.md` aliases; surface in Decisions.

2. **Metric: `<latency p99 / memory RSS / build time / LCP / etc.>`. Correct?**
   - _Default under `--auto`:_ infer from the prompt; surface in Decisions.

3. **Budget: `<value>` (from `--budget` flag). Correct?**
   - _Default under `--auto`:_ proceed.

4. **No budget specified. Default to "match the pre-regression baseline" or "improve by 50%"?**
   - _Default under `--auto`:_ "match the pre-regression baseline" if there's a known regression; else "improve by 50%". Record in Decisions.

## Phase 1 — preflight

5. **Working tree dirty. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if unrelated.

6. **On `<branch>`. Create `perf/<slug>` or stay?**
   - _Default under `--auto`:_ create if protected.

7. **Datadog MCP unreachable. Use staging trace fallback or stop?**
   - _Default under `--auto`:_ STOP and ask. The skill REQUIRES measurements; without DD it can't measure prod.

## Phase 2 — measure

8. **Time window for the baseline: last 1h / last 24h / last 7d?**
   - _Default under `--auto`:_
     - Hot regression (the user named a deploy / time): pick a window that covers the regression boundary (typically 24h).
     - Budget work (no specific incident): last 7d.

9. **Env: prod / staging / local?**
   - _Default under `--auto`:_ prod for production metrics; local for benchmarks.

10. **The baseline is unstable (wide variance across the window). Pick a different protocol or accept noise?**
    - _Default under `--auto`:_ surface; if variance > ±20%, STOP — the measurement is not signal.

## Phase 3 — identify

11. **Bottleneck hypothesis: `<one sentence>`. Confidence: `<low|med|high>`. Correct?**
    - _Default under `--auto`:_ proceed if confidence ≥ medium. STOP and ask if low.

12. **Multiple plausible bottlenecks (e.g. DB query AND large response body). Which to fix first?**
    - _Default under `--auto`:_ pick the one with the largest single contribution to total latency. Record in Decisions.

13. **The bottleneck is in a third-party library. Workaround locally or upgrade the library?**
    - _Default under `--auto`:_ workaround in this task; flag the upgrade as a separate `code-migrate` follow-up.

## Phase 4 — fix

14. **The fix introduces a cache. Define the invalidation strategy: TTL, size cap, manual invalidate, or per-batch?**
    - _Default under `--auto`:_ surface; ask. Cache invalidation is one of the two hard problems; defaults are dangerous.

15. **The fix introduces complexity. Trade-off OK?**
    - _Default under `--auto`:_ if the predicted gain is ≥ 30%, proceed; else surface and ask.

## Phase 5 — verify

16. **Metric did NOT move after the fix. Re-diagnose, or accept (rare)?**
    - _Default under `--auto`:_ re-diagnose (loop back to Phase 3). After 2 wrong diagnoses, STOP regardless of mode.

17. **Metric moved in the WRONG direction (got slower). Revert?**
    - _Default under `--auto`:_ STOP. Always. Revert.

18. **(If `--budget`) Budget not met but metric improved. Continue, or iterate?**
    - _Default under `--auto`:_ surface the gap; iterate up to 2 more times; then STOP with partial improvement reported.

## Phase 6 — guardrail

19. **Guardrail type: perf test / CI budget / DD monitor / multiple?**
    - _Default under `--auto`:_ pick by perf type (see decision tree). Record in Decisions.

20. **Guardrail threshold: `<value>` (1.5x the new measurement). Correct?**
    - _Default under `--auto`:_ 1.5x for prod-monitored; 2x for CI gates (more tolerance for noise). Record.

## Phase 7 — report

21. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip; offer-depth.

## Anti-rules

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #7 DD-unreachable, #10 unstable-baseline, #11 low-confidence-diagnosis, #14 cache-invalidation, #16 metric-didn't-move-after-2-tries, #17 metric-wrong-direction — those gate even under `--auto`).
- Surface defaults before asking.
