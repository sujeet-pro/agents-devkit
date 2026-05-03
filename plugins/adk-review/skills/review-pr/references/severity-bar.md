# `review-pr` — severity bar

The canonical 6-tier severity rubric. Honors `~/.config/adk/review.md.severity_bar` overrides.

## Tiers

| Tier | Letter | Meaning | Author response expected |
| --- | --- | --- | --- |
| **Blocker** | **B** | Ship-stopping. The PR cannot land in this state. | Fix before merge. |
| **Critical** | **C** | Serious bug, vulnerability, or design flaw — likely to cause real harm in production. | Fix this PR or open a follow-up with explicit owner + ETA. |
| **Should-Have** | **S** | Real defect or omission, but not ship-stopping. | Address in this PR if low-cost; otherwise file a follow-up. |
| **May-Have** | **M** | Nice improvement; the PR is OK without it. | Optional. |
| **Nitpick** | **N** | Style / readability; no functional impact. | Optional, often ignored. |
| **Question** | **Q** | Not a finding — a clarifying question or invitation to discuss. | Reply in conversation. |

## Default rubric (per dimension)

### Correctness

| Tier | Triggers |
| --- | --- |
| Blocker | Data loss; data corruption; auth bypass; crash on common path; deadlock; infinite loop on input the user can supply; off-by-one with security implication. |
| Critical | Race condition with concrete repro; silent exception swallow; wrong nullability that crashes a less-common path; broken error handling on a critical branch; off-by-one without security implication. |
| Should-Have | Missing edge-case branch (empty list, max int, etc.); inconsistent error message format; unreachable code (dead branch). |
| May-Have | Refactor-shaped improvement (extract helper, rename variable for clarity). |
| Nitpick | Comment style; ordering of imports; unused variable. |
| Question | "Is the upstream contract guaranteed to send a non-null `id` here?" |

### Security

| Tier | Triggers |
| --- | --- |
| Blocker | Secret committed to the diff (any provider); auth bypass; SQL injection with concrete attack vector; broken access control with a concrete privilege escalation; insecure deserialization with attacker-controlled payload; remote code execution. |
| Critical | XSS with stored / DOM vector; SSRF on user-supplied URL; CSRF on state-changing endpoint; missing input validation on a public boundary; broken cryptography (MD5 / SHA-1 for security purposes; reused IV; hardcoded key). |
| Should-Have | Missing constant-time compare on token; unsafe path concatenation that's currently scoped but easy to misuse; missing rate-limiting on an enumeration-prone endpoint. |
| May-Have | Defense-in-depth suggestion (e.g. add CSP header); explicit timeout on a network call. |
| Nitpick | Mostly N/A — security findings rarely degrade to Nitpick. |
| Question | "Is this endpoint reachable from outside the VPN?" |

### Performance

| Tier | Triggers |
| --- | --- |
| Blocker | n+1 query on the **hot path** with measured / observed regression; unbounded loop on user input; sync I/O on the hot path causing observed timeout. |
| Critical | n+1 query on a non-hot path or hot path without observed regression; allocation in tight loop; missing index implied by the query pattern; cache-busting on a hot read. |
| Should-Have | Per-request work that should be per-process (e.g. compiled regex inside a handler); inefficient algorithm where O(n²) → O(n log n) is straightforward. |
| May-Have | Memoization opportunity; concurrency win on independent calls. |
| Nitpick | Micro-optimization with no measured impact. |
| Question | "What's the expected cardinality of `orders` here?" |

### Tests

| Tier | Triggers |
| --- | --- |
| Blocker | Disabled / skipped a test that should be passing; introduced a flake; removed a regression test for a known bug. |
| Critical | New behavior with NO test coverage at all; change to a critical path (auth, payment, data write) with no integration test. |
| Should-Have | New branch (e.g. error path) without a test; missing boundary case (empty / max). |
| May-Have | Could add a property-based test for the data shape. |
| Nitpick | Test description doesn't match the assertion. |
| Question | "Should this be unit + integration, or just unit?" |

### Docs

| Tier | Triggers |
| --- | --- |
| Blocker | Removed documentation for a public API still in use; changed a documented contract without doc update. |
| Critical | New public API / endpoint / CLI flag without docs; behavior change not reflected in CHANGELOG. |
| Should-Have | README / runbook not updated for a behavior change; docstring missing on a new exported function. |
| May-Have | Add an example to the README. |
| Nitpick | Typo in a comment. |
| Question | "Is this a public-API change or internal?" |

### Style

| Tier | Triggers |
| --- | --- |
| Blocker | (rare) violates a CI-enforced rule that would fail the build. |
| Critical | (rare) violates a lint rule the repo runs but lint missed. |
| Should-Have | Inconsistency vs the file's own conventions (e.g. snake_case in a camelCase file). |
| May-Have | Could rename for clarity. |
| Nitpick | Whitespace; trailing newline. |
| Question | "Is the team OK with mixed `for...of` and `forEach` here?" |

## Honoring `~/.config/adk/review.md`

The user's `review.md` may override the default rubric:

```yaml
severity_bar:
  blocker:
    - secret_in_diff
    - sql_injection
    - auth_bypass
    - data_loss_risk
    - n_plus_one_in_loop_over_1000  # custom for our org
  critical:
    - n_plus_one_query
    - unbounded_loop
    - silent_exception_swallow
  should_have:
    - missing_test_for_new_branch
    - hardcoded_value_should_be_config
ignore_in_repos:
  acme/legacy-monolith:
    - style_consistency
    - test_coverage_threshold
post_only_blockers_under_auto: false
```

**Override semantics:**

1. `severity_bar.<tier>` lists categories whose **floor** is that tier. If a finding's category appears in `severity_bar.blocker`, it's at least Blocker; the dimension default may push it higher (rare), never lower.
2. `ignore_in_repos[<repo>]` drops findings whose category appears in the list **for that repo only**. The skill never silently drops findings from a repo that isn't listed.
3. `post_only_blockers_under_auto: true` causes the post stage (Phase 6a) to filter to Blocker + Critical only. Should-Have and below are still in `findings.md` but not posted; surface in `report.md` as `withheld`.

## Sortord (always)

Within `findings.md` and within a posted review:

```
Blocker (in dimension order: security, correctness, perf, tests, docs, style)
Critical (same dimension order)
Should-Have (same dimension order)
May-Have (same dimension order)
Nitpick (same dimension order)
Question (same dimension order)
```

Order matters. The author should see the Blocker before any Nitpick.

## Confidence

Independent of severity. Every finding ships:

- `low` — pattern-match suggests the issue, but verifying needs runtime data.
- `med` — code reading supports the issue; could be wrong if a constraint we missed makes it OK.
- `high` — the issue is concretely reproducible from the code alone.

Low-confidence Should-Have / May-Have findings are usually safer to file as `Question` to invite the author to confirm or refute.
