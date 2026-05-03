# `investigate-mixpanel` — anti-patterns

## Reporting raw event counts without a baseline

- "`checkout_completed` last 7d: 12,401". So what? Up from what? Down from what?
- **Fix:** every count has a baseline column. "12,401 (vs 11,890 prior 7d, +4.3%)".

## Inferring product failure from a funnel drop

- "Conversion `signup → first_export` dropped from 18% to 9%." Sounds like a regression.
- But `first_export` was renamed to `first_share` last week. The funnel is broken, not the product.
- **Fix:** when a step's count drops abruptly (>50% from baseline), check (a) the Lexicon for renames, (b) the deploy timeline for SDK / track() changes. Flag "possible event-tracking change" before concluding "product regression".

## Treating low-traffic funnels as conclusive

- "Funnel converts at 12% (n=73)". `n=73` is suggestive at best.
- For ship/iterate decisions, the threshold is hundreds of users per step, not dozens.
- **Fix:** flag any step with `n < 100`. The skill's report has a `Low-traffic warnings` section that lists every flagged step.

## Treating Mixpanel as billing's source of truth

- "Revenue last week: $47,891 per Mixpanel." That's the *tracked* revenue. The DB has the *real* revenue.
- Mixpanel can drop events (network blips, ad blockers, SDK bugs). The DB is the ledger.
- **Fix:** if the operator asks for an exact revenue / refund / order count, redirect to `/adk-investigate:investigate-snowflake` or production DB. Mixpanel is for trends, not for the ledger.

## Single-user diagnostics

- "Why didn't user X convert?" — Mixpanel can show user X's event timeline, but a single user is a story, not data.
- **Fix:** if the operator wants single-user investigation, redirect to the production DB or the application's own user-history endpoint. Mixpanel is for n>>1.

## Comparing across event-schema changes

- The team renamed `pageview` to `page_viewed` 30 days ago. Comparing "pageviews last 30d" vs "pageviews last 90d" mixes pre-rename and post-rename data → garbage numbers.
- **Fix:** when window spans a known event-schema change, restrict to post-change window or report both halves separately.

## Skipping the Lexicon check

- Querying for `checkout_complete` (without the trailing `d`) returns 0. The skill silently reports "0 checkouts!". Panic ensues.
- **Fix:** validate event names against `~/.config/adk/mixpanel.md.common_events` first. If the event isn't there, fetch the Lexicon (`Get-Lexicon-URL`) and confirm before reporting zero.

## Querying with no window

- Mixpanel returns "all time" data, which is meaningless and slow.
- **Fix:** default `--time` is `last 7d`. Never run with no window.

## Ignoring weekly seasonality

- "DAU last Tue vs DAU yesterday (Sat)" — comparing weekday traffic to weekend traffic. The drop is seasonal, not a product issue.
- **Fix:** prefer same-day-last-week as the baseline; explicitly call out when the comparison spans different day-of-week buckets.

## Forgetting the Mixpanel UI link

- The prose summary is for orientation. The link is the deliverable. Without it, the operator has to re-construct the funnel / report in the Mixpanel UI from scratch.
- **Fix:** every result row has a Mixpanel UI link.

## Claiming causation from a single funnel run

- "Funnel converts at 18%" — that's the funnel, not the cause of the conversion.
- **Fix:** for cause-investigation, segment the funnel by `country / device / experiment_variant / signup_date_bucket` and surface where the conversion differs. The "why" lives in the segment delta.
