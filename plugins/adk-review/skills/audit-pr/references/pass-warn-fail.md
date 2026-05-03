# `audit-pr` — Pass / Warn / Fail rubric

The verdict model. NEVER conflate with `review-pr`'s 6-tier severity (Blocker / Critical / Should-Have / May-Have / Nitpick / Question).

## Per-check verdicts

Each check emits exactly one of:

| Verdict | Meaning | Action expected |
| --- | --- | --- |
| **PASS** | Check ran; passed. | None. Move on. |
| **WARN** | Check ran; produced a non-blocking concern. | Consider; non-blocking; may be auto-fixable. |
| **FAIL** | Check ran; produced a blocking concern. | Address before merge. |
| **N/A** | Check did NOT run because trigger didn't match (e.g. a11y on a backend-only diff) OR a required tool isn't installed. | Surface install command if tool is missing. |
| **INCONCLUSIVE** | Check ran but couldn't determine a verdict (e.g. timeout; tool crash; flaky output). | Re-run; surface the failure to the user. |

## Per-check threshold definitions

See `references/check-catalog.md` for each check's exact pass/warn/fail thresholds.

## Overall verdict

The overall verdict aggregates per-check verdicts:

```python
def overall_verdict(per_check: dict[str, str]) -> str:
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "N/A": 0, "INCONCLUSIVE": 0}
    for v in per_check.values():
        counts[v] += 1
    if counts["FAIL"] > 0:
        return "FAIL"
    if counts["INCONCLUSIVE"] > 0:
        return "INCONCLUSIVE"
    if counts["WARN"] > 0:
        return "WARN"
    if counts["N/A"] > 0:
        return "MIXED"
    return "PASS"
```

| Overall | Conditions | User-facing summary |
| --- | --- | --- |
| **PASS** | All ran checks Pass; no N/A. | "All N checks Pass. Ready to merge per the audit." |
| **MIXED** | Pass + at least one N/A; no Warn / Fail / Inconclusive. | "Pass for run checks (N); some checks N/A (M; install commands listed)." |
| **WARN** | At least one Warn; no Fail / Inconclusive. | "Some warnings; non-blocking. Consider addressing or proceed." |
| **FAIL** | At least one Fail. | "One or more checks failed. Address before merge." |
| **INCONCLUSIVE** | At least one Inconclusive; no Fail. | "Some checks couldn't determine a verdict (timeout / flake). Re-run recommended." |

## Why these states (and not severity tiers)

`audit-pr` is a gate. Gates are binary at the top level (open / closed); per-check verdicts are nuanced. The 4-state model (PASS/WARN/FAIL/N/A + INCONCLUSIVE) maps naturally to:

- Lights on a build: green (PASS), yellow (WARN), red (FAIL), gray (N/A or INCONCLUSIVE).
- CI status: success (PASS), neutral (WARN/N/A), failure (FAIL).

Severity tiers (B/C/S/M/N/Q) make sense for `review-pr` (where each finding is qualitatively different and the author needs to know which to address first). They don't map to gating questions like "is the lint clean?" — that's binary (or near-binary).

## When to downgrade or override

Under `-i`:

- A WARN can be downgraded to PASS for THIS run (recorded in `results.md`). Common when the operator knows a context the check doesn't (e.g. "this lint warning is intentional pending the framework upgrade").
- A FAIL can be overridden (recorded in `results.md`) for non-critical checks. Common when the operator is shipping behind a flag and will address in a follow-up.
- `secrets-in-diff: FAIL` can NEVER be overridden via `-i`. The skill refuses.
- `tests-added: FAIL` CAN be overridden (the operator may have integration-test coverage that the heuristic misses).

Under `--auto`:

- No overrides. Verdicts stand.

Overrides are surfaced in `results.md` and `report.md` with the user's reason.

## When `--fix` re-runs the check

After applying a fix (Phase 5b), the affected check is re-run. The new verdict overrides the old one in `results.md`; the pre-fix verdict is preserved in `results.pre-fix.md` so the user can diff.

Example:

| Pre-fix | Post-fix | Status |
| --- | --- | --- |
| WARN | PASS | "fix succeeded" |
| WARN | WARN | "fix didn't fully clear" — surface as "partial; manual touch needed" |
| FAIL | PASS | "fix succeeded" |
| FAIL | WARN | "fix improved but didn't fully clear" |
| FAIL | FAIL | "fix didn't help" — surface; user reverts the auto-fix |

## What about INCONCLUSIVE?

INCONCLUSIVE is reserved for cases where the check ran but couldn't determine PASS/WARN/FAIL:

- **Timeout.** The check exceeded its timeout (default: 60s for fast checks; 300s for build/test checks).
- **Tool crash.** The tool exited with a non-typical exit code (e.g. SIGSEGV).
- **Flaky output.** The output is structurally invalid (e.g. malformed JSON; missing expected sections).

INCONCLUSIVE is NOT used for:

- Missing tool → that's `N/A`.
- Trigger didn't match → that's `N/A`.
- Tool ran but found issues → that's the appropriate verdict (PASS/WARN/FAIL).

INCONCLUSIVE is surfaced in the report with the failure mode + a re-run suggestion.

## Anti-patterns

- **Treating N/A as PASS.** The user needs to know what wasn't checked.
- **Treating WARN as FAIL.** Don't gate on style.
- **Treating INCONCLUSIVE as FAIL.** A flaky check is not a real failure.
- **Sneaking "Blocker" / "Critical" wording in.** That's `review-pr`'s vocabulary; this skill is Pass/Warn/Fail.
- **Computing overall verdict from a half-finished run.** Wait for all checks to complete before computing. (Even under `--fail-fast`, surface the in-progress state, not a premature verdict.)
- **Hiding overrides.** Every `-i` override is recorded with reason + timestamp.
