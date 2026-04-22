# `validate-browser` — severity ladder

| Severity | Verify-fix | Visual-check | Console-audit | Interaction-test | a11y-audit |
| --- | --- | --- | --- | --- | --- |
| Blocker | bug repros after fix | >5% pixel diff or layout broken | console error | step assertion failed (HARD) | axe `impact: critical` |
| Critical | console error reduced but still present | 0.5–5% pixel diff | failed network request 5xx | step soft assertion failed | axe `impact: serious` |
| Should | DOM correct but extra warnings | <0.5% pixel diff (within tolerance — pass) | console warning | screenshot looks off | axe `impact: moderate` |
| May | n/a | n/a | blocked third-party | n/a | axe `impact: minor` |
| Nitpick | n/a | n/a | deprecation warning | n/a | best-practice rule |

## Verdict

- Any Blocker → FAIL.
- Any Critical → FAIL by default; pass with `--accept-critical` flag (rare).
- Should/May/Nitpick → PASS but listed in report.

The parent skill (e.g. `auto`'s D2 phase) honors the verdict to decide whether to loop back to Phase C.
