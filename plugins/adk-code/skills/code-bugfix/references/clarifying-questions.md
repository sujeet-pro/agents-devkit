# `code-bugfix` — clarifying questions

Asked in order, one at a time, **only when the answer changes the diagnosis or patch**. Under `--auto`, defaults apply silently and are listed in the final report's Decisions table.

## Phase 0 — prompt expand

1. **The bug looks like: `<restated symptom>`. Correct?**
   - _Default under `--auto`:_ proceed with the restatement; flag in Decisions if the user disagrees.

2. **Repo: `<resolved-repo>` from `repos.md`. Correct?**
   - _Default under `--auto`:_ proceed with the cwd-resolved repo.

3. **The reproducer condition. From the prompt I see: `<conditions>`. Anything missing?**
   - _Default under `--auto`:_ proceed with the conditions extracted from the prompt; if none, treat as exploratory and surface "could not extract a precise reproducer condition — using observed symptom".

## Phase 1 — preflight

4. **Working tree dirty: `<file list>`. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if changes are unrelated; STOP and ask if they overlap with the suspected area.

5. **On `<branch>`. Create `fix/<slug>`, or stay here?**
   - _Default under `--auto`:_ create `fix/<slug>` if the current branch is protected.

6. **Baseline is unexpectedly red on: `<list>`. Continue anyway?**
   - _Default under `--auto`:_ STOP and ask. Always.

## Phase 2 — REPRODUCE

7. **The failing test I will write asserts: `<one sentence>`. Correct?**
   - _Default under `--auto`:_ proceed with the inferred assertion. The user will see the test in the report; if it doesn't capture the intended bug, they say so post-hoc.

8. **The test PASSED unexpectedly. The bug is not reproducing. Possible reasons: env-specific, version mismatch, already-fixed in HEAD, or my reproducer is wrong. Which?**
   - _Default under `--auto`:_ STOP and ask. Always — `--auto` does NOT default-proceed here. Without a red reproducer, there is nothing to fix.

9. **The bug is intermittent (flake-shaped). Probability of failure: `<estimate>`. Continue?**
   - _Default under `--auto`:_ note the flakiness in `reproducer.md`; continue with extra runs in CI for the regression test (e.g. `it.repeats(50)`).

## Phase 3 — DIAGNOSE

10. **Root cause: `<one sentence>`. Confidence: `<low|med|high>`. Patch plan: `<one sentence>`. Approve?**
    - _Default under `--auto`:_ proceed with the documented diagnosis if confidence ≥ medium.
    - If confidence is LOW, surface and STOP — even under `--auto`. Patching with low-confidence diagnosis usually means symptom-patching.

11. **The cause is upstream (out-of-repo). Workaround locally, or wait for upstream fix?**
    - _Default under `--auto`:_ apply local workaround with documented WHY in a code comment + tracking the upstream issue in residual risk.

## Phase 4 — PATCH

12. **Implementer wants to touch `<file>` (not in plan.md). Allow?**
    - _Default under `--auto`:_ STOP and ask. Scope creep gates even under `--auto`.

13. **The patch is applied but the reproducer still fails. Re-diagnose, or try a different patch?**
    - _Default under `--auto`:_ re-diagnose (loop back to Phase 3). After 2 wrong patches, STOP regardless of mode.

## Phase 5 — VALIDATE

14. **A different test (not the reproducer) is now red — regression. Investigate, or roll back?**
    - _Default under `--auto`:_ STOP. Always. Regression-on-fix means the patch is wrong or the diagnosis is incomplete.

15. **Test failed with `<error>`. Iterate, accept, or escalate?**
    - _Default under `--auto`:_ iterate up to 3 times, then escalate.

## Phase 6 — REPORT

16. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip the question; offer-depth at the end.

## Anti-rules for asking

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #6 baseline-red, #8 reproducer passed unexpectedly, #10 low-confidence diagnosis, #12 scope creep, #14 regression-on-fix — those gate even under `--auto`).
- If the user already answered, don't re-ask.
- Surface the default before asking, so the user can say "default is fine".
- Confidence-aware: state your confidence on the diagnosis. Low confidence = ask, even under `--auto`.
