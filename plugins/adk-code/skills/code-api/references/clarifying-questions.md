# `code-api` — clarifying questions

Asked one at a time, only when the answer changes the design. Under `--auto`, defaults apply silently and are listed in the final report's Decisions table.

## Phase 0 — prompt expand

1. **Contract type: `<REST / RPC / SDK / CLI / types>`. Correct?**
   - _Default under `--auto`:_ infer from existing artifacts in the repo + the prompt. Surface in Decisions.

2. **Status: NEW or EVOLUTION? If EVOLUTION, what's the existing artifact?**
   - _Default under `--auto`:_ NEW unless existing artifact found.

3. **`--breaking` flag set / unset. The design implies `<breaking?>`. Confirm?**
   - _Default under `--auto`:_ if implied breaking but flag NOT set → STOP and ask. Always.

## Phase 1 — preflight

4. **Working tree dirty. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if unrelated.

5. **On `<branch>`. Create `api/<slug>` or stay?**
   - _Default under `--auto`:_ create if protected.

6. **External consumers identified: `<list>`. Anything missing?**
   - _Default under `--auto`:_ proceed with the discovered list; flag in residual risk if confidence is low.

## Phase 2 — use cases

7. **Top use cases I extracted: `<list>`. Add, remove, reorder?**
   - _Default under `--auto`:_ proceed with 3 inferred use cases. If only 1 was inferable, STOP and ask.

8. **For use case `<N>`, the caller is `<X>`. Correct?**
   - _Default under `--auto`:_ proceed.

9. **Use case I didn't capture: `<X>`. Should this be in scope?**
   - _Default under `--auto`:_ proceed without; flag in NOT-done.

## Phase 3 — candidates

10. **Sketched candidates: `<A, B, C>`. Anything to add or remove?**
    - _Default under `--auto`:_ proceed with 2-3 sketched.

11. **Candidates feel too similar. Widen search?**
    - _Default under `--auto`:_ widen automatically; the goal is genuine alternatives, not variations.

## Phase 4 — pick

12. **Picked Candidate `<X>` because `<rationale>`. Correct?**
    - _Default under `--auto`:_ proceed; record in Decisions.

13. **Trade-offs accepted: `<list>`. OK?**
    - _Default under `--auto`:_ proceed; record.

14. **Hyrum's Law caveats: `<guaranteed>` vs `<observable but unsupported>`. Anything to move between?**
    - _Default under `--auto`:_ proceed.

15. **Validation strategy: boundary-only at `<entry point>`. Internal trust assumed. OK?**
    - _Default under `--auto`:_ proceed.

## Phase 5 — produce artifact

16. **Artifact will be saved to `<path>`. Working-tree edit or `.temp/`?**
    - _Default under `--auto`:_ if the repo has an existing OpenAPI / .proto / .d.ts location, edit there. Otherwise save to `.temp/` and recommend in the report.

17. **Artifact format-validation failed: `<error>`. Fix or escalate?**
    - _Default under `--auto`:_ fix; if 2 attempts fail, STOP.

## Phase 6 — deprecation plan (if `--breaking`)

18. **Deprecation window: `<default 1 major + 90 days>`. OK?**
    - _Default under `--auto`:_ use default; record.

19. **Communication plan: release notes + Slack post + (if applicable) partner email. Confirm?**
    - _Default under `--auto`:_ use default; the operator does the actual posting.

## Phase 7 — report

20. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip; offer-depth.

## Anti-rules

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #3 breaking-implied-without-flag, #7 only-1-use-case-inferable, #17 artifact-format-fails-after-2-tries — those gate even under `--auto`).
- Surface defaults before asking.
- The most-valuable gate is #12 (candidate selection); preserve operator agency here in `-i` mode.
