# `prompt-expand` output format

Written to `.temp/task-<slug>/skill-plan.md`.

```markdown
# skill-plan — <slug>

## Prompt
> <verbatim user prompt>

## Restated intent
<one sentence>

## Confidence
<low | medium | high> — <one sentence why>

## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| repo | "checkout" | acme/checkout-api | repos.md (verified) |
| service | "checkout" | checkout-api | datadog.md.service_aliases (verified) |
| time | "yesterday" | 2026-05-02T00:00..23:59 | NL parse (inferred) |
| env | (omitted) | prod | datadog.md.default_env (verified) |

## Links
| URL | Type | Status |
| --- | --- | --- |
| https://acme.atlassian.net/browse/CHK-1234 | Jira | will queue context-gather |
| https://github.com/acme/checkout-api/pull/2841 | GitHub PR | will queue context-gather |

## Recommended chain
1. `/adk-core:context-gather <links> --auto`
2. `/adk-investigate:investigate-incident "checkout 5xx since 13:00" --service checkout-api --window "last 2h"`
3. (if root cause is code) `/adk-code:code-bugfix "<root-cause>" --auto`

## Alternatives considered
- `/adk-investigate:investigate-datadog "5xx in checkout" --time "last 2h"` — narrower; skips Slack scrape.
- `/adk-investigate:investigate-rca` — heavier; use for post-mortem prep, not active triage.

## Missing inputs
- (None) — all entities resolved.

OR

- `--severity-bar` — not set in `~/.config/adk/review.md`. Default Blocker/Critical/Should-Have applies.
- Confluence space for the publish step — set `default_confluence_space` in `~/.config/adk/docs.md`.
```

## Sections

- **Prompt** — verbatim, blockquoted.
- **Restated intent** — one sentence.
- **Confidence** — `low` / `medium` / `high` with rationale.
- **Resolved entities** — table with verified/inferred per row.
- **Links** — table; mark `will queue context-gather` for those that will.
- **Recommended chain** — numbered list of skill invocations with exact flags.
- **Alternatives considered** — at least one fallback chain.
- **Missing inputs** — explicit list (or `(None)` if all clear).
