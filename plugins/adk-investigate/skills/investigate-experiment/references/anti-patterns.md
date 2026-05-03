# `investigate-experiment` — anti-patterns

## "Statsig says ship; let's ship"

- Statsig's pulse is one source. The DD guardrails and the Mixpanel project-level check are the other two. A clean Statsig win can hide a perf regression that hits all users equally (so it doesn't show up in the experiment splice's relative numbers).
- **Fix:** never recommend ship without all three sources agreeing. Apply the rubric.

## Treating Mixpanel and Statsig as the same metric automatically

- Statsig measures `checkout_completed` per its own definition (event name + filter rules). Mixpanel measures `checkout_completed` per ITS definition. The two definitions can drift over time (a new filter rule in one system, a renamed property in the other).
- **Fix:** when Mixpanel's project-level number doesn't match the Statsig direction, surface it as a "metric-definition divergence — verify before shipping". Don't silently treat the divergence as Mixpanel "missing" the win.

## Ignoring DD guardrails

- The product team is excited about a 4% conversion lift. The platform team is alarmed about an 85ms p99 regression. Both are real.
- **Fix:** the report has a dedicated `Datadog guardrails` section. A regression there with `p<0.1` is a veto.

## Ignoring sample size on Statsig

- "Lift +12%! Ship!" with `n=200 per arm`. That's a noisy number; the effect is suggestive, not real.
- **Fix:** include `n per arm` in the Statsig section. Apply the `pulse-evaluation.md` rubric for power thresholds.

## Recommending ship from a 2-day pulse

- Even with `n=10,000`, 2 days hides week-of-day variance. Conversion on a Tuesday and a Saturday can differ by 30%.
- **Fix:** require ≥7 days in experiment (or ≥1 full business cycle for products with longer cycles) before recommending ship.

## Pasting raw Statsig / Mixpanel / DD numbers without reconciliation

- Three tables of numbers without a `Reconciliation` table is just data. The verdict needs the comparison.
- **Fix:** the report has a `Reconciliation` table that puts all three sources side by side per metric.

## Hand-rolling the verdict

- "I think we should iterate because the lift seems suspicious." Vibes-driven, not rubric-driven.
- **Fix:** apply `three-source-verdict.md` mechanically. The verdict is `ship | iterate | kill` based on rules; reasoning is the rubric inputs, not opinion.

## Not naming the discrepancy

- Statsig +4.2%, Mixpanel +0.5%. The verdict is `iterate` due to disagreement.
- But the report just says "Mixpanel doesn't agree" without explaining what the operator should investigate.
- **Fix:** the `Reconciliation` section names probable causes for each disagreement type ("metric definition divergence — pull both definitions and diff", "splice imbalance — check whether the experiment cohort is unrepresentative").

## Toggling the gate

- This skill is read-only. The verdict is the deliverable; the gate flip happens in the Statsig console.
- **Fix:** the report's `Follow-up` section names the next step but does NOT execute it.

## Forgetting the linked repo

- The experiment links to `acme/storefront` per `statsig.md.common_experiments[].repo`. Recent commits in that repo can explain unexpected movement (e.g. a tracking change).
- **Fix:** include "Recent commits in linked repo" as a context section, especially when the verdict is `iterate` due to disagreement.
