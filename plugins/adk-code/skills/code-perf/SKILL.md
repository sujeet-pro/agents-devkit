---
name: code-perf
description: |
  Diagnose and fix a performance regression or hit a stated performance budget — measure first, identify the bottleneck with quoted profiler / trace evidence, apply the smallest correct fix, verify the win with re-measurement, and add a guardrail (perf test, CI budget, Datadog monitor) so the regression cannot silently recur. Use when the user says "X is slow", "Y times out", "we need to hit Zms p99", "memory keeps growing", or pastes an APM trace. Do NOT use for correctness bugs (use `/adk-code:code-bugfix`), general feature work (use `/adk-code:code-write`), refactors that don't have a measurement target (use `/adk-code:code-refactor`), or migrations (use `/adk-code:code-migrate`). Performance work without measurement is guesswork; do not use this skill in measure-free mode.
metadata:
  category: build
  kind: task
  layer: 5
  modes: [auto, interactive]
  needs_meta_info: [datadog, repos]
argument-hint: "<perf-target-or-symptom> [--budget <metric>=<value>] [-i]"
---

# code-perf — diagnose and fix a perf regression / hit a perf budget

A Principal Engineer's "X is slow" skill. Measure first, fix second, re-measure to confirm the win, add a guardrail.

## When to use

- "checkout API p99 jumped from 250ms to 1.2s after Tuesday's deploy"
- "the dashboard takes 8 seconds to load"
- "memory usage keeps growing on the workers"
- "hit p99 < 500ms on `/api/products`"
- "the build takes 6 minutes; can we get it under 2?"
- The user pastes an APM trace, a flame graph, or a profile output.

## When NOT to use

| If the prompt is about | Use instead |
| --- | --- |
| A correctness bug | `/adk-code:code-bugfix` |
| New feature work | `/adk-code:code-write` |
| Pure refactor with no measurement | `/adk-code:code-refactor` |
| Library / framework upgrade (which may improve perf as a side effect) | `/adk-code:code-migrate` |
| API contract change | `/adk-code:code-api` |
| Security mitigation that happens to be slow | `/adk-code:code-security` |

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| "X is slow" / "Y times out" | Default match. |
| "p99 / p95 / p50 of … " + a service / endpoint | Default match. |
| "hit ≤ <ms> on <endpoint>" | Budget-driven. |
| "memory usage on …" / "OOM in …" | Memory variant. |
| "build / CI is slow" | Build-perf variant. |
| Paste of an APM trace, flame graph, profiler output | Treat as evidence; fold into Phase 2. |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<perf-target-or-symptom>` | yes | the verbatim user request |
| `--budget <metric>=<value>` | optional | e.g. `--budget p99=500ms` or `--budget rss=300MB` |
| `--auto` | optional | (default) skip per-phase approval gates |
| `-i` / `--interactive` | optional | per-phase approval; mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  - Restate: "Hit budget X on Y" or "Diagnose regression in Y".
  - Resolve repo via repos.md.
  - Resolve service tag via datadog.md service_aliases (e.g.
    "checkout" → "checkout-api").
  - Pick task slug; create .temp/task-<slug>/.

Phase 1 — preflight
  - git status clean (dirty → ask).
  - tests / typecheck / lint commands resolved.
  - Baseline check: tests green on HEAD.
  - If the work needs Datadog: bin/adk-mcp-health for DD reachability;
    DD_API_KEY + DD_APP_KEY present.

Phase 2 — MEASURE (capture baseline)
  - Capture the current performance signal:
      - Endpoint perf: DD APM p50/p95/p99 over a representative window.
      - Function-level perf: a benchmark / profiler run; flame graph if
        available.
      - Memory: heap snapshot, RSS over time, `top` / `ps` output.
      - Browser perf: Lighthouse / Chrome DevTools perf trace.
  - Save to .temp/task-<slug>/measurement-baseline.md.
  - Approval gate (under -i) before moving to identify.

Phase 3 — IDENTIFY (bottleneck with evidence)
  - Profile / trace / inspect to identify the bottleneck.
  - QUOTE the relevant trace / profiler output (≤15 words per quote).
  - Save to .temp/task-<slug>/bottleneck.md.
  - Hypothesis confidence: low / medium / high.
  - Approval gate unless --auto.

Phase 4 — FIX (smallest correct change)
  - Spawn implementer subagent with bottleneck.md.
  - Apply the smallest correct change.
  - Run tests; confirm no regression.

Phase 5 — VERIFY (re-measure)
  - Re-run the same measurement protocol from Phase 2.
  - Capture before/after to .temp/task-<slug>/measurement-after.md.
  - If the fix didn't move the metric, STOP — diagnosis was wrong; loop
    back to Phase 3.

Phase 6 — GUARDRAIL (so the regression can't silently recur)
  - Add ONE of:
      a. A perf test in the test suite (e.g. assert "operation completes
         in <Xms" with a generous threshold).
      b. A CI budget check (e.g. webpack-bundle-analyzer threshold,
         lighthouse-ci threshold).
      c. A Datadog monitor (alert on p99 > Yms over a 5-min window).
  - Document the chosen guardrail.

Phase 7 — REPORT
  - .temp/task-<slug>/report.md: budget / symptom, before / after, the
    fix, the guardrail, residual risk.
```

See `references/workflow.md` for the detailed step list.

## Persona

> "Measure first, fix second, re-measure third." Never trust intuition about where the bottleneck is. Always re-measure after the fix. Add a guardrail so the regression cannot silently recur. Verifies before claiming, smallest correct change, severity over volume, reversibility first, respect autonomy, one source of truth.

See `references/persona.md`.

## Constitution

**Must do:**

1. Capture before/after measurements with the same protocol.
2. Identify the bottleneck with quoted (≤15 words) trace / profiler / metric evidence.
3. Apply the smallest correct fix.
4. Re-measure and confirm the win (the metric moved in the right direction).
5. Add a guardrail (perf test, CI budget, or DD monitor).
6. State confidence on the diagnosis (low / med / high). Low confidence → STOP and surface.

**Must not do:**

1. Optimize without measuring.
2. Ship a fix without re-measurement.
3. Skip the guardrail (the regression will silently come back).
4. Apply micro-optimizations on cold paths (premature optimization).
5. Trade readability for a 1% win.
6. Push, commit, or open a PR.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "I refactored this; it should be faster." Without measurement, that's a guess.
- Premature optimization on cold paths.
- Trading readability for a 1% win.
- Skipping the guardrail; the regression silently recurs.
- Quoting a vague metric ("it feels faster") instead of a measured one.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + ISO timestamp |
| `.temp/task-<slug>/measurement-baseline.md` | Phase 2 baseline |
| `.temp/task-<slug>/bottleneck.md` | Phase 3 identification with quoted evidence |
| `.temp/task-<slug>/measurement-after.md` | Phase 5 post-fix re-measurement |
| `.temp/task-<slug>/plan.md` | The fix plan + the guardrail design |
| `.temp/task-<slug>/validation/per-skill/code-perf.md` | Implementer + measurement evidence |
| `.temp/task-<slug>/report.md` | Final report |

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Measure-first persona + status banner |
| `references/workflow.md` | Detailed Phase 0–7 stage list |
| `references/modes.md` | What `--auto` and `-i` mean for `code-perf` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 4 worked examples (latency, memory, browser, build) |
| `references/output-format.md` | Shape of `measurement-*.md`, `bottleneck.md`, `report.md` |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase validation gates (esp. before/after measurements) |
| `references/how-it-works.md` | Mermaid diagrams: measure-fix-verify cycle |
| `references/clarifying-questions.md` | Questions Phase 0/3 may ask under `-i` |
| `references/measurement-protocol.md` | Per-tool measurement recipes (DD APM, profilers, Lighthouse, etc.) |

## Additional links

The skill may WebFetch / use these for extra context when relevant:

- Datadog APM dashboards (URL from `~/.config/adk/datadog.md` `common_dashboards`).
- The repo's existing perf tests / benchmarks.
- Vendor docs for the framework's perf-tuning guides (e.g. React Profiler, Spring Boot Actuator).
