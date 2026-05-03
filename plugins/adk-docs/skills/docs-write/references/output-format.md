# `docs-write` — output format

## Per-turn status banner

```
[adk-docs:docs-write] task=<slug> phase=<0|1|2|3|4> doc-type=<readme|adr|runbook|migration|freeform> audience=<engineer|pm|em|mixed> mode=<auto|interactive|fix>
```

## Draft shape

`.temp/task-<slug>/draft.md` ends with a validation block. The skill's
validator reads this block to gate `--fix` promotion.

```markdown
<rest of the doc>

<!-- validation
claims:
  - path: src/main/kotlin/com/acme/checkout/CartService.kt
    lines: 42-58
    claim: add-to-cart is idempotent on (cartId, sku)
  - path: build.gradle.kts
    lines: 14-18
    claim: Spring Boot 3.2
  - path: docker-compose.yml
    lines: 22-30
    claim: requires Postgres 15
audience: engineer
template: readme
external-quotes: 0
todos-verify: 0
-->
```

## Evidence map

`.temp/task-<slug>/sources.md`:

```markdown
# sources — <slug>

| Claim | File | Lines | Evidence |
| --- | --- | --- | --- |
| Runs on Spring Boot 3.2 | build.gradle.kts | 14-18 | `version "3.2.3"` |
| Local run command | scripts/run.sh | 1-12 | `./gradlew :app:bootRun` |
| Requires Postgres 15 | docker-compose.yml | 22-30 | `image: postgres:15-alpine` |

## Unverified (surfaced to the user)

| Claim | Reason |
| --- | --- |
| p99 < 500ms | No SLO file; `docs.md.slo_thresholds` is empty |
```

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-write report — <slug>

## Result
Authored README for `acme/checkout-api`. Under --fix, written to
`README.md` and staged.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | doc type | readme | prompt matched "README for …" |
| 1 | target path | README.md | repo root, no existing README |
| 3 | audience | engineer | docs.md.audience_default |
| 3 | template | readme | matches doc type |

## Validation evidence
- 12 claims, all cited to files (see sources.md)
- 0 external quotes
- 0 TODOs pending verification

## Residual risk / follow-ups
- `docs.md.slo_thresholds.checkout_p99_ms` is empty; the "Performance"
  section is left blank. Resolve before next README refresh.

## Artifact index
.temp/task-<slug>/
  prompt.txt          verbatim user prompt
  sources.md          evidence map
  draft.md            the draft
  report.md           this file
README.md             canonical target (under --fix)
```

## Status glossary

- `phase=0` — prompt expansion + slug creation
- `phase=1` — preflight (adk-info --check, target-path resolution)
- `phase=2` — gather source of truth (build evidence map)
- `phase=3` — draft in `.temp/task-<slug>/draft.md`
- `phase=4` — validate + optional `--fix` promotion
