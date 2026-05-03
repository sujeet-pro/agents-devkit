# `code-refactor` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are listed in the final report's Decisions table.

## Phase 0 — prompt expand

1. **The move I will make: `<one sentence — extract / rename / dedupe / split / inline / move>`. Correct?**
   - _Default under `--auto`:_ proceed with the inferred move; flag in Decisions if the user disagrees post-hoc.

2. **The scope: `<files / call-sites / packages>`. Anything missing?**
   - _Default under `--auto`:_ proceed with the discovered scope; if a later step finds a missed call-site, surface as scope-creep gate (#9 below).

3. **Slug `<proposed>` looks right?**
   - _Default under `--auto`:_ proceed.

## Phase 1 — preflight

4. **Working tree dirty: `<file list>`. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if changes are unrelated; STOP and ask if they overlap with the refactor scope.

5. **On `<branch>`. Create `refactor/<slug>`, or stay here?**
   - _Default under `--auto`:_ create `refactor/<slug>` if the current branch is protected.

6. **Baseline is RED. A refactor on a red baseline is unverifiable. STOP — fix the baseline first?**
   - _Default under `--auto`:_ STOP. Always.

## Phase 2 — read

7. **Existing test coverage on the affected behavior is THIN (`<count>` tests, `<percent>%` lines). Do you want to run `code-test` first to establish a safety net?**
   - _Default under `--auto`:_ proceed with current coverage; surface the gap in residual risk. Override only if coverage is essentially zero — then STOP and ask.

## Phase 3 — plan

8. **Micro-step list: `<list>`. Approve, edit, or change?**
   - _Default under `--auto`:_ proceed with the list as written.

9. **Out-of-plan call-site discovered while editing: `<file>`. Include in this refactor, or list as follow-up?**
   - _Default under `--auto`:_ if it's the same symbol being renamed/moved, include (it's part of the same logical change). If it's adjacent / unrelated, surface as follow-up.

## Phase 4 — execute

10. **Step `<N>` failed. Smallest fix, REVERT, or escalate?**
    - _Default under `--auto`:_ try smallest fix once; if still red, REVERT. If revert doesn't restore green or the step has been re-attempted twice, STOP regardless of mode.

11. **The micro-step list seems too long (>10 steps). Should this be split into multiple `code-refactor` tasks?**
    - _Default under `--auto`:_ flag in residual risk; continue with current task. The operator decides at PR time whether to split.

## Phase 5 — validate

12. **A snapshot test required `--update`. The refactor changed observable output. STOP — is this intentional?**
    - _Default under `--auto`:_ STOP. Always. A snapshot change is a behavior change; this is not a refactor.

13. **Test count is now `<N>`, was `<M>` at baseline. Why?**
    - _Default under `--auto`:_ if the difference is consistent with the move ("moved 4 tests to a new file"), proceed with a note. If unexplained, STOP and surface.

14. **Validation failed: `<error>`. Iterate, accept, or escalate?**
    - _Default under `--auto`:_ iterate up to 3 times, then escalate.

## Phase 6 — report

15. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip the question; offer-depth at the end.

## Anti-rules for asking

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #6 baseline-red, #9 scope-creep, #10 step-failed-after-fix-and-revert, #12 snapshot-changed, #13 test-count-changed-unexplained — those gate even under `--auto`).
- If the user already answered, don't re-ask.
- Surface the default before asking, so the user can say "default is fine".
- Be specific. "Refactor failed" is not a question; "Step 3 failed because `tsc` reports `Cannot find module 'x'` — likely a missed import update. Should I fix the import or revert step 3?" is.
