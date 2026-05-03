# `code-test` — output format

## Per-turn status

```
[adk-code:code-test] task=<slug> phase=<0|1|2|3|4|5|6> tests-added=<N> behaviors-covered=<M> coverage-delta=<+P%>
```

## `.temp/task-<slug>/behaviors.md` (Phase 3)

```markdown
# Behaviors — <slug>

## Target
<repo-relative path>

## Test type
unit | integration | e2e

## Behaviors

### B1. <one-sentence behavior>
- Happy path: <one-sentence test case>
- Boundary: <one-sentence test case>
- Error: <one-sentence test case>
- Test file location: <repo path>

### B2. <one-sentence behavior>
…

## Behaviors NOT covered (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/report.md` (Phase 6)

```markdown
# code-test report — <slug>

## Result
Added <N> tests covering <M> behaviors on <target>.

## Tests added
| File | Test name | Behavior asserted | Fail-first evidence |
| --- | --- | --- | --- |
| services/cart/discount.test.ts | "rejects expired codes" | B1.error | mutated SUT to skip expiry check; saw red; restored; saw green |
| services/cart/discount.test.ts | "applies same-day codes until midnight" | B1.boundary | … |
…

## Behaviors covered
| # | Behavior | Trio (file::tests) |
| --- | --- | --- |
| B1 | Expired codes are rejected | discount.test.ts::3 tests |
| B2 | Single-use codes apply once | discount.test.ts::3 tests |
…

## Behaviors NOT covered (deliberate)
- <bullet> — <reason>
- e2e for the same flow — out of scope; covered by manual QA today.

## Coverage delta (if --coverage)
| File | Lines (before → after) | Branches (before → after) |
| --- | --- | --- |
| services/checkout/discount.ts | 50% → 88% | 35% → 79% |

## Validation evidence
| Command | Exit | Notes |
| --- | --- | --- |
| `pnpm test --filter checkout-api` | 0 | 199 passed (was 187) |
| `pnpm typecheck` | 0 | clean |
| `pnpm lint` | 0 | clean |
| `pnpm test --coverage` | 0 | see delta above |
Full logs: `.temp/task-<slug>/validation/per-skill/code-test.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | test type | unit | target is pure function with no external deps |
| 3 | trio shape for B1.boundary | "midnight cutoff" | most-relevant boundary for expiry check |

## Residual risk / follow-ups
- <bullet> — <reason>
- 3 remaining branches in error handling not covered — would require mock-injection; little signal.

## NOT done (deliberate)
- <bullet> — <reason>

## Next steps
1. `/adk-review:review-code-changes` before push.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  behaviors.md
  validation/per-skill/code-test.md
  report.md
```

## Hand-off note shape

```
Result: <N> tests added; <M> behaviors covered.
Validation: <test-command> exit 0; <count> passed (was <baseline-count>).
Coverage (if requested): lines <before>% → <after>%, branches <before>% → <after>%.
Next: /adk-review:review-code-changes <slug>   # before push
```

Plus the offer-depth question.
