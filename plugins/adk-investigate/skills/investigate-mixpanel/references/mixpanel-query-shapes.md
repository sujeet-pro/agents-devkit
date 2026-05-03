# `investigate-mixpanel` — query shapes

The Mixpanel workspace MCP exposes 24 tools. This skill uses three primary shapes:

- `Get-Events` — list + count events (often grouped).
- `Run-Query` — arbitrary JQL / formula / segmentation.
- `Get-Report` — fetch a saved report (funnel, retention, dashboard tile).

## Get-Events

| Use | Args | Notes |
| --- | --- | --- |
| Top N events in window | `--window <window> --top 20 --by event_name` | Returns count per event in the window. |
| Count for one event | `--window <window> --event <name>` | Returns the count. Pair with prior-window for delta. |
| Group by property | `--window <window> --event <name> --group-by <prop>` | Useful for "checkout_completed by country" |

## Run-Query (arbitrary JQL / formula)

| Use | Shape |
| --- | --- |
| DAU | `unique(user_id)` over `[event_name in any]` |
| WAU | same with weekly window |
| Top property values | aggregate by property |
| Per-event funnel | `funnel(steps=[<event>, <event>, ...])` |
| Retention | `retention(cohort=<def>, return_event=<event>, days=[1,7,30])` |

Example formula for DAU comparison:

```text
unique(user_id) where time >= now-1d and time < now
unique(user_id) where time >= now-8d and time < now-7d   # baseline (same day last week)
```

## Get-Report (saved reports)

| Use | Args |
| --- | --- |
| Saved funnel by id | `--report-id <id> --window <window>` |
| Saved retention by id | `--report-id <id> --window <window>` |
| Saved dashboard tile | `--report-id <tile-id> --window <window>` |

For an ad-hoc funnel (not saved), build it via `Run-Query`:

```text
funnel(
  steps=["signup_completed", "first_export", "checkout_completed"],
  window="last 7d",
  conversion_window=86400        # 1 day to convert each step
)
```

## Common composite shapes

| Goal | Shape |
| --- | --- |
| "DAU now vs same day last week" | Two `Run-Query unique(user_id)` calls; one for yesterday, one for 7d-ago. |
| "Funnel A → B → C now vs prior 7d" | One `Get-Report` (or ad-hoc funnel) for now; one for prior. |
| "Retention of cohort X vs all_users" | `Run-Query retention()` for cohort X; same for `all_users`. |
| "Top events for cohort X" | `Get-Events --top 20 --filter "cohort:<id>"`. |

## Defaults from `~/.config/adk/mixpanel.md`

| Default | From key | Used when |
| --- | --- | --- |
| `--window last 7d` | `mixpanel.md.default_window` | no `--time` flag |
| `--identity-property user_id` | `mixpanel.md.identity_property` | uniqueness in queries |
| Project context | `mixpanel.md.project_id` | every call |

## Failure modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Zero count for an event you "know" exists | Typo OR event renamed | Check `mixpanel.md.common_events` AND fetch Lexicon (`Get-Lexicon-URL`). |
| Funnel returns 0 for step 2 | Step 2 event not tracked OR conversion window too short | Confirm event in Lexicon; widen `conversion_window`. |
| Retention curve is flat at 100% | Cohort definition matches return event | Re-define cohort to exclude the return event from cohort criteria. |
| Slow query | No window OR too-wide window | Always pin window; default `last 7d`. |
