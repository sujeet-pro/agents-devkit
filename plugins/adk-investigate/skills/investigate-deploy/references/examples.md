# `investigate-deploy` — worked examples

## Example 1 — recent deploys for current repo

**Prompt:** `/adk-investigate:investigate-deploy --window 2h` (run from inside `~/code/acme/checkout-api`)

**Phase 0:**
- Repo: resolved from CWD `git remote get-url origin` → `acme/checkout-api`.
- Workflow: `repos.md.repos[acme/checkout-api].deploy_workflow` = `deploy.yml`.
- Window: `last 2h`.

**Phase 2:**

```bash
gh run list --repo acme/checkout-api --workflow=deploy.yml --limit 50 \
  --json status,conclusion,createdAt,event,headBranch,headSha,actor,url,name,displayTitle
```

**Phase 4 excerpt:**

```markdown
# Deploy timeline: acme/checkout-api (last 2h)

## Summary
- 4 deploys in window
- 0 failed
- 0 near-symptom (no --symptom-time set)

## Timeline (newest first)
| Time (UTC) | Status | Duration | SHA | Author | Title | URL |
| --- | --- | --- | --- | --- | --- | --- |
| 13:42 | success | 4m 12s | `e7f2a91` | bob | "fix: bump retry count" | [run](https://github.com/acme/checkout-api/actions/runs/123456789) |
| 12:58 | success | 4m 03s | `a3f9c2e` | alice | "deploy v3 checkout funnel" | [run](https://github.com/acme/checkout-api/actions/runs/123456788) |
| 12:11 | success | 3m 48s | `b1c4d77` | carol | "chore: dependency bump" | [run](https://github.com/acme/checkout-api/actions/runs/123456787) |
| 11:38 | success | 4m 22s | `d8e5f01` | bob | "feat: new pricing engine" | [run](https://github.com/acme/checkout-api/actions/runs/123456786) |

## Failed deploys
None in window.

## Cross-source: Datadog deploy events
| Time (UTC) | DD event | Matched gh run |
| --- | --- | --- |
| 13:42 | deploy.checkout-api | `e7f2a91` |
| 12:58 | deploy.checkout-api | `a3f9c2e` |
| 12:11 | deploy.checkout-api | `b1c4d77` |
| 11:38 | deploy.checkout-api | `d8e5f01` |

All 4 gh runs matched DD events. Timeline coherent.

## Follow-up
- For incident triage: `/adk-investigate:investigate-incident "<symptom>" --service checkout-api --window last 2h`.
```

---

## Example 2 — deploys near a reported symptom

**Prompt:** `/adk-investigate:investigate-deploy acme/storefront --window 4h --symptom-time 2026-05-03T13:02:00Z`

**Phase 0:**
- Repo: `acme/storefront`.
- Workflow: `repos.md.repos[acme/storefront].deploy_workflow` = `release.yml`.
- Window: `last 4h`.
- Symptom: `2026-05-03T13:02:00Z`.

**Phase 2:** as Example 1.

**Phase 3:** tag rows where `abs(createdAt - symptom_time) <= 30min`.

**Phase 4 excerpt:**

```markdown
# Deploy timeline: acme/storefront (last 4h, symptom at 2026-05-03T13:02 UTC)

## Summary
- 6 deploys in window
- 0 failed
- 1 near-symptom candidate

## Timeline (newest first)
| Time (UTC) | Status | Duration | SHA | Author | Title | Δ-symptom | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 14:30 | success | 5m 11s | `a1` | alice | "doc update" | +88m | [run](...) |
| 13:01 | success | 4m 02s | `b2` | bob | "feat: shipping cost calc v2" | **-1m (NEAR-SYMPTOM)** | [run](...) |
| 12:15 | success | 3m 55s | `c3` | carol | "chore: bump deps" | -47m | [run](...) |
| 11:30 | success | 5m 22s | `d4` | dave | "fix: legacy promo edge case" | -92m | [run](...) |
| 11:00 | success | 4m 41s | `e5` | erin | "test: add unit tests" | -2h 2m | [run](...) |
| 10:45 | success | 3m 30s | `f6` | frank | "chore: tidy" | -2h 17m | [run](...) |

## Failed deploys
None in window.

## Near-symptom candidates (sorted by abs(Δ))
| Time (UTC) | SHA | Author | Title | Δ |
| --- | --- | --- | --- | --- |
| 13:01 | `b2` | bob | "feat: shipping cost calc v2" | -1m |

This deploy ran 1 minute before the symptom. **This is a candidate, not a confirmed cause.** Confirm correlation by:
- `/adk-investigate:investigate-datadog "errors in storefront last 4h"` — find log/metric signal that matches the new code path.
- `gh pr view <pr>` — inspect what changed in `b2`.
- `/adk-investigate:investigate-incident "<symptom>" --service storefront --window 4h` — multi-source triage.
```

---

## Example 3 — failed deploy surfaced

**Prompt:** `/adk-investigate:investigate-deploy acme/search-api --window 6h`

**Phase 4 excerpt:**

```markdown
# Deploy timeline: acme/search-api (last 6h)

## Summary
- 3 deploys in window
- **2 failed**
- 0 near-symptom (no --symptom-time set)

## Timeline (newest first)
| Time (UTC) | Status | Duration | SHA | Author | Title | URL |
| --- | --- | --- | --- | --- | --- | --- |
| 14:20 | success | 4m 11s | `f9` | frank | "fix CI for search-api" | [run](...) |
| 14:05 | **FAILURE** | 2m 03s | `g8` | grace | "feat: BM25 tuning" | [run](...) |
| 13:42 | **FAILURE** | 1m 48s | `h7` | henry | "feat: filter expansion" | [run](...) |

## Failed deploys (highlight)
| Time | Status | SHA | Author | Title | Likely cause | URL |
| --- | --- | --- | --- | --- | --- | --- |
| 14:05 | failure | `g8` | grace | "feat: BM25 tuning" | inspect run logs | [run](...) |
| 13:42 | failure | `h7` | henry | "feat: filter expansion" | inspect run logs | [run](...) |

## Follow-up
- Inspect the failed runs' logs via the URLs above.
- Confirm prod state matches successful deploy at 14:20 (`f9`); two preceding failures may have caused partial rollouts.
```
