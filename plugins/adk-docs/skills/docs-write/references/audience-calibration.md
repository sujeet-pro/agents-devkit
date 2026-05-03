# Audience calibration

`docs-write` calibrates the prose to one of four audiences (set via
`--audience <value>` or `~/.config/adk/docs.md.audience_default`).

## Rubric

| Dimension | engineer | pm | em | mixed |
| --- | --- | --- | --- | --- |
| Implementation detail | full | omit | summary | full in body; omit in TL;DR |
| Code snippets | verbatim | none | minimal | verbatim in body |
| Env vars + run commands | exact | named only if blocker | named only if blocker | exact in body |
| Outcomes vs mechanisms | mechanism-first | outcome-first | outcome-first | outcome first; mechanism after |
| Trade-off discussion | short | short | long | short in body; long dedicated section |
| TL;DR at top | optional | yes | yes | yes (3 sentences, for pm/em) |
| Glossary | none | as needed | as needed | as needed |

## `engineer`

- Default; the Principal Engineer reader.
- Concrete paths, verbatim code, exact commands.
- "Runs on JVM 21 (Temurin). Start with `./gradlew :app:bootRun`."
- Implementation detail is the point; don't strip it.

## `pm`

- Outcome-first; 1-paragraph outcome summary at top.
- Minimal code; link to the engineer-calibrated section instead of
  duplicating detail inline.
- "Checkout handles 2k orders/min at p99 420ms. SLO target 500ms.
  Dashboard: <link>."
- Avoid jargon without a parenthetical ("SLO = service level
  objective, our p99 latency budget").

## `em`

- Trade-off and decision-context first. Risk, ownership, timeline.
- "This refactor unblocks the Q3 checkout-redesign launch. Risk: the
  shared session cache changes eviction order; mitigated by a 2-week
  dual-write behind `FEATURE_CHECKOUT_CACHE_V2`."
- Less code than engineer; more decision context than pm.

## `mixed`

- 3-sentence TL;DR at top (serves pm + em).
- Then full engineer-calibrated body (serves engineer).
- Never "skip this section if …" language — let the TL;DR satisfy the
  pm/em audience; the body is for the engineer who needs to act.

## Calibration smell tests

- An engineer-calibrated doc should let a new teammate run the service
  locally without asking anyone. If you can't do that with the doc,
  the audience is really `mixed` or the doc is incomplete.
- A pm-calibrated doc should let a PM skim in < 2 minutes and know
  what shipped, what's next, and what the measurement is. If it has
  a code block in the top half, the calibration drifted.
- An em-calibrated doc should let an EM decide whether to prioritize
  this item in the next sprint. If it doesn't surface "who owns it"
  and "when does it land", the calibration drifted.

## Audience interacts with doc type

| Doc type | Typical audience |
| --- | --- |
| README | engineer (rarely mixed) |
| ADR | engineer (sometimes mixed for cross-team decisions) |
| Runbook | engineer (the runbook reader is the on-call) |
| Migration guide | engineer or mixed |
| API reference | engineer |
| Design doc | mixed |
| Release notes / FAQ | pm or mixed |

When the prompt's doc type and audience conflict (e.g. "runbook for
pm"), stop and ask: runbooks are for responders; if the deliverable is
really a "what does the team do?" overview, that's a design doc or a
team-page on Confluence.
