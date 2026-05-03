# `review-code-changes` — severity bar

Same 6-tier rubric as `review-pr`. Honors `~/.config/adk/review.md.severity_bar` overrides. Cross-reference: `/adk-review:review-pr` `references/severity-bar.md` is the canonical version; this file mirrors the rubric for self-review use.

## Tiers

| Tier | Letter | Meaning | Action expected |
| --- | --- | --- | --- |
| **Blocker** | **B** | Ship-stopping. Don't push. | Fix before commit/push. |
| **Critical** | **C** | Serious bug, vulnerability, or design flaw — likely real harm in production. | Fix this branch or open a follow-up with explicit owner + ETA. |
| **Should-Have** | **S** | Real defect or omission, but not ship-stopping. | Address before push if low-cost; otherwise file a follow-up. |
| **May-Have** | **M** | Nice improvement; the change is OK without it. | Optional. |
| **Nitpick** | **N** | Style / readability; no functional impact. | Optional, often deferred to next pass. |
| **Question** | **Q** | Not a finding — a clarifying question for self / future-self. | Resolve in your own head before push, or invite a peer's input. |

## Self-review-specific tier rubrics

Same as `review-pr` for the per-dimension tables (correctness / security / performance / tests / docs / style). The full reference for the tables lives at `/adk-review:review-pr` `references/severity-bar.md`.

A few self-review-specific nuances:

### `Question` is more useful in self-review

When reviewing your own work, you don't have a peer to ask, so a `Question` finding is often resolved by re-reading the code with the question in mind. Common self-`Question` triggers:

- "Did I cover the empty-list case?"
- "Is the upstream contract guaranteed to send a non-null `id` here?"
- "Should this be unit + integration, or just unit?"
- "Am I sure the lock at line 102 covers this read?"

If you can answer the question by re-reading, do so and re-tier (often to nothing, or to a `May-Have`). If you can't, file the `Question` and either resolve before push or surface to a peer.

### Severity inflation is the bigger risk in self-review

The peer-review failure mode is severity inflation — peers tend to be lenient ("don't be that reviewer"). The self-review failure mode is the OPPOSITE — you tend to be lenient on your own code.

**Counter-rule: tier the same finding the same way you'd tier a peer's.** If you'd tell `@alice` "this is a Blocker", it's a Blocker on your own code too.

### `dirty_during_review` annotation

Findings on files that were modified during the review (between Phase 2 and Phase 3) are annotated. The annotation does NOT change the severity, but the user should re-run for accuracy.

## Honoring `~/.config/adk/review.md`

Same semantics as `review-pr`:

```yaml
severity_bar:
  blocker:
    - secret_in_diff
    - sql_injection
    - auth_bypass
    - data_loss_risk
  critical:
    - n_plus_one_query
    - unbounded_loop
  should_have:
    - missing_test_for_new_branch
ignore_in_repos:
  acme/legacy-monolith:
    - style_consistency
    - test_coverage_threshold
```

- `severity_bar.<tier>` lists categories whose **floor** is that tier.
- `ignore_in_repos[<repo>]` drops findings whose category is in the ignore list, for that repo only.

## `post_only_blockers_under_auto`

`review.md`'s `post_only_blockers_under_auto: true` is a `review-pr`-shaped flag (it controls comment posting). For `review-code-changes`, since there's no posting, the flag is interpreted as `report_only_blockers_under_auto`: under `--auto`, only Blocker + Critical findings appear in the at-a-glance section of `report.md`. The full `findings.md` still has all findings.

## Sort order (always)

Within `findings.md`:

```
Blocker (in dimension order: security, correctness, perf, tests, docs, style)
Critical (same dimension order)
Should-Have (same dimension order)
May-Have (same dimension order)
Nitpick (same dimension order)
Question (same dimension order)
```

Within a tier, findings are also tagged with their scope source (branch / staged / unstaged / untracked) and within a tier+dimension, ordered by source priority: untracked → unstaged → staged → branch (newest work first, since that's most likely to have rough edges).

## Confidence

Same `low | med | high` axis as `review-pr`. Independent of severity. Low-confidence Should-Have / May-Have findings often degrade to `Question`.
