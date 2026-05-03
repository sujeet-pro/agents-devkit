# `temp-folder` — slug examples

## Good slugs (derived from prompts)

| Prompt | Slug |
| --- | --- |
| "fix the bug where checkout times out at p99" | `bug-where-checkout-times-out-p99` |
| "review my PR for the new pricing experiment" | `review-my-pr-new-pricing-experiment` |
| "investigate the search latency spike" | `investigate-search-latency-spike` |
| "write a runbook for auth-token rotation" | `runbook-auth-token-rotation` |
| "RCA for yesterday's checkout outage" | `rca-yesterdays-checkout-outage` |

## Empty / fallback

| Prompt | Slug |
| --- | --- |
| `""` | `task-20260503-134242` (date-time fallback) |
| `"the the the"` (all stop-words) | `task-20260503-134242` |

## Disambiguation (--date)

| Prompt | Slug (with --date) |
| --- | --- |
| "fix checkout bug" | `2026-05-03-fix-checkout-bug` |

## Bad slugs (rejected by the convention)

| Bad | Why |
| --- | --- |
| `Fix-Checkout-Bug` | uppercase |
| `fix_checkout_bug` | underscore (use kebab) |
| `fix checkout bug` | space |
| `fix-the-checkout-bug-where-the-customer-sees-zero-active-users-and-the-dashboard-renders-wrong` | too long (>6 words) |
| `fix-checkout-bug!` | punctuation |
| `task-20260503-134242` (when descriptive is available) | use prompt-derived slug instead |

## Re-use within a session

Once a slug is assigned, every subsequent skill in the same task reuses it. The dispatcher passes `--slug <slug>` to every subagent.

## Listing all task workspaces

```bash
ls -d .temp/task-*/
# .temp/task-bug-where-checkout-times-out-p99/
# .temp/task-review-my-pr-new-pricing-experiment/
# ...
```
