# `code-migrate` — clarifying questions

Asked one at a time, only when the answer changes the plan. Under `--auto`, defaults apply silently and are listed in the final report's Decisions table.

## Phase 0 — prompt expand

1. **From `<X>` to `<Y>` — correct?**
   - _Default under `--auto`:_ proceed with the inferred versions; flag in Decisions if "latest" was resolved.

2. **The user said "latest". Resolved to `<resolved-Y>` (via npm registry / GitHub releases). OK?**
   - _Default under `--auto`:_ resolve + record in Decisions. Surface the resolution in the report.

3. **Skipping intermediate versions (`<X>` to `<Y>` skips `<X+1>`). The guide recommends one major at a time. Continue or split?**
   - _Default under `--auto`:_ surface the recommendation in residual risk and continue. Operator may split later.
   - If the gap spans 3+ majors (e.g. React 16 → 19), STOP and ask. Even under `--auto`.

4. **Migrating to `<alpha|beta|rc>` release. Confirm?**
   - _Default under `--auto`:_ STOP and ask. Pre-release migrations need explicit operator opt-in.

## Phase 1 — preflight

5. **Working tree dirty: `<file list>`. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if unrelated; STOP if changes overlap with the migration scope.

6. **On `<branch>`. Create `migrate/<slug>` or stay?**
   - _Default under `--auto`:_ create `migrate/<slug>` if protected.

7. **Baseline RED. STOP — fix baseline first?**
   - _Default under `--auto`:_ STOP. Always.

## Phase 2 — read upstream migration guide

8. **The migration guide is at `<url>`. Fetch?**
   - _Default under `--auto`:_ proceed with the canonical URL.

9. **The guide is paywalled / 404 / unreachable. STOP or use alternative source?**
   - _Default under `--auto`:_ STOP and ask. Alternative sources (blog posts, StackOverflow) are NOT authoritative.

10. **The guide notes `<runtime semantic change>`. This requires more careful review. Recommend `-i` for the first pass.**
    - _Default under `--auto`:_ proceed under `--auto` but FLAG in residual risk: "this migration has runtime semantic changes; recommend running tests in production-like environment before merging".

## Phase 3 — inventory

11. **`<rule>` has `<count>` matches. Verify the inventory pattern is correct?**
    - _Default under `--auto`:_ proceed; surface unusually low/high counts in residual risk for human review.

12. **The inventory found `<count>` matches; the migration guide implies `<expected>`. Discrepancy. Investigate?**
    - _Default under `--auto`:_ surface; usually proceed (the guide is generic; our codebase may use the pattern more or less). Flag for the report.

## Phase 4 — plan groups

13. **Group sequence: `<list>`. Approve, edit, or change?**
    - _Default under `--auto`:_ proceed with the proposed sequence.

14. **The plan adopts `<optional>` rules in addition to required ones. Adopt or skip?**
    - _Default under `--auto`:_ skip optional rules (don't adopt). List as residual risk for follow-up `code-write`.
    - Exception: rules the guide explicitly says are "highly recommended" — adopt under `--auto`, with Decision-table entry.

## Phase 5 — execute

15. **Group `<N>` failed: `<error>`. Smallest fix, REVERT and re-plan, or skip this group (and document)?**
    - _Default under `--auto`:_ try smallest fix once. If still red, STOP and surface. Never skip a required group under `--auto` without operator approval.

16. **Implementer wants to touch `<file>` outside the group's planned set. Allow?**
    - _Default under `--auto`:_ STOP and ask. Scope creep gates even under `--auto`.

## Phase 6 — final validation

17. **Build failed: `<error>`. Iterate, accept, or escalate?**
    - _Default under `--auto`:_ iterate up to 3 times; escalate.

18. **Test count is now `<N>`, was `<M>` at baseline. Why?**
    - _Default under `--auto`:_ if the migration explicitly added/removed tests (e.g. some migration codemod auto-generates new tests), the count change is expected. Otherwise STOP and investigate.

19. **Smoke check failed. Investigate, accept, or escalate?**
    - _Default under `--auto`:_ STOP. The smoke check is the runtime signal; failures here often indicate semantic changes.

## Phase 7 — report

20. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip; offer-depth.

## Anti-rules for asking

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #4 pre-release, #7 baseline-red, #9 guide-unreachable, #15 group-failed-after-fix, #16 scope-creep, #18 unexpected test-count change, #19 smoke-check-failed — those gate even under `--auto`).
- If the user already answered, don't re-ask.
- Surface the default before asking.
