# `prompt-expand` — worked examples

## Example 1 — bugfix with context

**Input:** `/adk-core:prompt-expand "fix the checkout 5xx that started at 13:00 https://acme.slack.com/archives/C123/p1715..."`

**Output (`skill-plan.md`):**

```markdown
# skill-plan — fix-checkout-5xx-13-00

## Prompt
> fix the checkout 5xx that started at 13:00 https://acme.slack.com/archives/C123/p1715...

## Restated intent
Investigate the checkout-api 5xx surge starting at 13:00, identify root cause, and apply the fix.

## Confidence
medium — multi-verb (investigate + fix); one Slack link to read first.

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| service | "checkout" | checkout-api | datadog.md.service_aliases (verified) |
| repo | (inferred from service) | acme/checkout-api | repos.md (verified) |
| time | "started at 13:00" | last 2h centered on 13:00 today | NL parse (inferred) |

## Links
| URL | Type | Status |
| --- | --- | --- |
| https://acme.slack.com/archives/C123/p1715... | Slack | will queue context-gather |

## Recommended chain
1. `/adk-core:context-gather <links> --auto`
2. `/adk-investigate:investigate-incident "checkout 5xx since 13:00" --service checkout-api --window "last 2h"`
3. (if root cause is code) `/adk-code:code-bugfix "<root-cause>" -i`

## Alternatives considered
- `/adk-investigate:investigate-rca` — heavier; for post-mortem, not active triage.
- Skip step 1 if the user says the Slack thread is just the report, not new info.

## Missing inputs
- (None)
```

## Example 2 — bare PR URL

**Input:** `/adk-core:prompt-expand https://github.com/acme/checkout-api/pull/2841`

**Output:**

```markdown
## Restated intent
Review the linked GitHub PR.

## Confidence
high — bare PR URL is unambiguous.

## Recommended chain
1. `/adk-review:review-pr https://github.com/acme/checkout-api/pull/2841`

## Alternatives considered
- `/adk-review:review-pr <url> --fix` if the user wants auto-apply on the local checkout (only works for own PRs).

## Missing inputs
- (None)
```

## Example 3 — ambiguous

**Input:** `/adk-core:prompt-expand "fix the api"`

**Output:**

```markdown
## Confidence
low — "the api" matches 3 repos in repos.md.

## Recommended chain
(blocked — ambiguous)

## Missing inputs
- Repo / service: which API? Options: checkout-api, search-api, pricing-api.
- Symptom: what is broken?
```
