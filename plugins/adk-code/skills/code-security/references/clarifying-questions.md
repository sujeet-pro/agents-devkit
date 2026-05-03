# `code-security` — clarifying questions

Asked one at a time, only when the answer changes the plan. Under `--auto`, defaults apply silently.

## Phase 0 — prompt expand

1. **Vulnerability / hardening goal: `<one sentence>`. Correct?**
   - _Default under `--auto`:_ proceed.

2. **CVE id: `<id>`. Correct? (NVD entry summary: `<…>`)**
   - _Default under `--auto`:_ proceed with the WebFetched advisory.

3. **Repo: `<resolved>`. Correct?**
   - _Default under `--auto`:_ proceed.

## Phase 1 — preflight

4. **Working tree dirty. Stash, abort, or include?**
   - _Default under `--auto`:_ stash if unrelated; STOP if overlap.

5. **On `<branch>`. Create `secure/<slug>` or stay?**
   - _Default under `--auto`:_ create if protected.

6. **Tests RED on HEAD. STOP — fix baseline first?**
   - _Default under `--auto`:_ STOP. Always.

## Phase 2 — threat model

7. **Threat model (5 lines): `<paste>`. Correct?**
   - _Default under `--auto`:_ proceed.

8. **Threat actor: `<actor>` (unauthenticated external / authenticated user / admin / insider / supply-chain)?**
   - _Default under `--auto`:_ infer from the prompt + the affected surface; record in Decisions.

9. **Acceptable residual risk: `<…>`. Correct?**
   - _Default under `--auto`:_ proceed; flag if residual risk is high.

## Phase 3 — boundary

10. **Input boundary: `<path>:<line>`. Correct?**
    - _Default under `--auto`:_ proceed; surface alternatives in Decisions if multiple plausible boundaries exist.

11. **Output / privileged action: `<path>:<line>`. Correct?**
    - _Default under `--auto`:_ proceed.

12. **Mitigation will live at the input boundary, NOT in 4 layers. Confirm?**
    - _Default under `--auto`:_ proceed; the constitution mandates boundary-only.

## Phase 4 — REPRODUCE

13. **Exploit test (behavior asserted): `<one sentence>`. Correct?**
    - _Default under `--auto`:_ proceed; surface in Decisions.

14. **Exploit test PASSED unexpectedly on HEAD. The bug may be already fixed, env-specific, or my reproducer is wrong. Investigate?**
    - _Default under `--auto`:_ STOP. Always.

15. **Exploit test confidence: `<low|med|high>`. Correct?**
    - _Default under `--auto`:_ if low, STOP and ask. Even under `--auto`.

## Phase 5 — APPLY

16. **Mitigation: `<one sentence>`. Approve?**
    - _Default under `--auto`:_ proceed.

17. **The mitigation library `<X>` is not currently used in this repo. Add it, use a different one, or roll my own?**
    - _Default under `--auto`:_ use an existing library if any matches the need (e.g. `zod` for input validation, `express-rate-limit` for rate-limit). Surface the addition.

18. **Mitigation applied; exploit test still RED. Re-think boundary or re-think mitigation?**
    - _Default under `--auto`:_ try once more; if 2nd attempt still red, STOP.

## Phase 6 — VALIDATE

19. **A pre-existing test went RED. Regression. Investigate?**
    - _Default under `--auto`:_ STOP. Always.

## Phase 7 — security-reviewer

20. **Blocker finding: `<…>`. Fix in this diff or escalate?**
    - _Default under `--auto`:_ fix in this diff (loop back to Phase 5). Never ship a Blocker.

21. **Critical finding: `<…>`. Fix in this diff or follow-up?**
    - _Default under `--auto`:_ fix in this diff if the change is small; else flag as follow-up + add to residual risk.

22. **Should-have finding: `<…>`. Fix in this diff or follow-up?**
    - _Default under `--auto`:_ flag as follow-up.

## Phase 8 — REPORT

23. **Disclosure status: `<internal-only / coordinated / public>`. Correct?**
    - _Default under `--auto`:_ if CVE is already public → public; else coordinated. Operator handles actual disclosure timing.

24. **Report ready. Anything to redo?**
    - _Default under `--auto`:_ skip; offer-depth.

## Anti-rules

- Never ask 3 questions stacked.
- Never ask under `--auto` (except #6 baseline-red, #14 exploit-test-passed-unexpectedly, #15 low-confidence-on-test, #18 mitigation-applied-but-test-still-red-after-2-tries, #19 regression, #20 blocker-finding — those gate even under `--auto`).
- Surface defaults before asking.
- Never ask the operator to provide working exploit details in a public channel — keep all such asks in the local conversation.
