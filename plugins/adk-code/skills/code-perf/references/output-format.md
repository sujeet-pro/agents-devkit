# `code-perf` — output format

## Per-turn status

```
[adk-code:code-perf] task=<slug> phase=<0|1|2|3|4|5|6|7> baseline=<captured|pending> bottleneck=<identified|pending> fix=<applied|pending> verified=<yes|no> guardrail=<added|pending>
```

## `.temp/task-<slug>/measurement-baseline.md` (Phase 2)

```markdown
# Baseline measurement — <slug>

## Tool / protocol
<one paragraph: which tool, which command/protocol, sample size>

## Window (for production metrics)
- Start: <ISO timestamp>
- End: <ISO timestamp>
- Env: prod / staging / local

## Headline numbers
| Metric | Value | Notes |
| --- | --- | --- |
| p99 | 1240ms | service:checkout-api, env:prod |
| p95 | 320ms | |
| p50 | 80ms | |

## Evidence (links / IDs)
- Datadog dashboard: <URL>
- Slowest trace ID: <id>
- Profile dump: <path or attachment>

## Sample data (≤15-word quotes only)
- "p99 spike from 250ms to 1240ms post 2026-04-30 deploy"
```

## `.temp/task-<slug>/bottleneck.md` (Phase 3)

```markdown
# Bottleneck — <slug>

## Hypothesis (one sentence)
<the cause, named specifically>

## Evidence
- Quote (≤15 words): "<verbatim trace/profile/metric output>"
- Quote (≤15 words): "<another, if multi-evidence>"
- Source: DD trace <id> / profile dump <path> / Lighthouse run <id>

## Confidence
high | medium | low

## Proposed fix (one sentence)
<the smallest correct change>

## Why this fix matches the evidence
<one paragraph>

## Alternatives considered
- <alt 1> — rejected because <reason>
- <alt 2> — rejected because <reason>
```

## `.temp/task-<slug>/measurement-after.md` (Phase 5)

```markdown
# After measurement — <slug>

## Tool / protocol
<same as baseline>

## Window
<same as baseline OR documented difference (e.g. "staging post-deploy")>

## Headline numbers
| Metric | Before | After | Δ |
| --- | --- | --- | --- |
| p99 | 1240ms | 240ms | -81% |
| p95 | 320ms | 165ms | -48% |
| p50 | 80ms | 78ms | unchanged |

## Same trace shape
<note any change in trace structure: "47 sequential getUser → 1 batched getUsers">
```

## `.temp/task-<slug>/plan.md` (Phase 4)

```markdown
# Fix plan — <slug>

## Summary
<one sentence>

## Files touched
| Path | Lines | Action | Why |
| --- | --- | --- | --- |
| services/checkout/recent-buyers.ts | 47-58 | edit | replace per-buyer getUser loop with batched getUsers |

## Validation plan
- Tests: full affected-package suite — green.
- Re-measurement: re-run the protocol from Phase 2.
- Guardrail: <type> — <details>.
```

## `.temp/task-<slug>/report.md` (Phase 7)

```markdown
# code-perf report — <slug>

## Result
<one sentence: "Hit p99 < 500ms on /api/checkout (was 1240ms)" or "Reduced RSS leak: stable at 220MB after 1000 docs">

## Before / After
| Metric | Before | After | Δ |
| --- | --- | --- | --- |
| p99 | 1240ms | 240ms | -81% |

## Bottleneck
<one sentence with the quoted evidence>

## Fix
| File | +N / -M | Role |
| --- | --- | --- |
| services/checkout/recent-buyers.ts | +3 / -8 | replace N+1 with batched query |

## Guardrail
<type>: <where added> with threshold <value>
- Perf test: tests/checkout-perf.test.ts asserts p99 < 400ms with 50-buyer cart.
- Recommended: Datadog monitor on `p99:trace.checkout-api.request{env:prod} > 500` over 5m.

## Validation evidence
| Command | Exit | Notes |
| --- | --- | --- |
| `<test command>` | 0 | full affected suite green |
| `<measurement re-run>` | — | see measurement-after.md |
Full logs: `.temp/task-<slug>/validation/per-skill/code-perf.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 2 | window | last 24h | covers the regression deploy |
| 6 | guardrail type | perf test + DD monitor recommendation | both signals (CI + prod) |

## Residual risk / follow-ups
- Other endpoints with similar N+1 pattern (orders/timeline, recommendations) — sweep with `audit-repo`.
- DD monitor not yet created; operator should via DD UI.

## NOT done (deliberate)
- <bullet> — <reason>

## Next steps
1. `/adk-review:review-code-changes` before push.
2. (recommended) Create the DD monitor in DD UI; alert message + runbook link.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  measurement-baseline.md
  bottleneck.md
  plan.md
  measurement-after.md
  validation/per-skill/code-perf.md
  report.md
```

## Hand-off note shape

```
Result: <metric: before → after>
Bottleneck: <one sentence>
Fix: <files>
Guardrail: <type>
Next: /adk-review:review-code-changes <slug>
```

Plus the offer-depth question.
