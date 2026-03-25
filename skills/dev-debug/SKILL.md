---
name: dev-debug
description: Use when investigating bugs, test failures, or unexpected behavior so you find root cause before applying fixes
---

# Systematic Debugging

## Core Rule

Do not propose fixes before you understand the failure. ALWAYS find root cause, NEVER fix symptoms.

## Phase 1: Investigation

Gather evidence before forming any hypothesis.

1. **Read the error** — full message, stack trace, logs. Don't skim.
2. **Reproduce** — confirm the failure happens consistently. Note exact steps.
3. **Check recent changes** — `git log`, recent PRs, config changes. What changed?
4. **Find a working reference** — does it work in another branch, environment, or test? What's different?

Do NOT skip to a fix because the answer "seems obvious."

## Phase 2: Pattern Analysis

Understand the system around the failure.

1. **Map the data flow** — trace the failing value from origin to error site.
2. **Read the relevant code completely** — don't claim to understand a function without reading it.
3. **Identify assumptions** — what does each layer assume about its inputs?
4. **Check dependencies** — are external services, configs, or environment variables involved?

## Phase 3: Hypothesis

Form one hypothesis at a time.

1. **State it explicitly** — "I believe X happens because Y."
2. **Design a test** — how would you confirm or disprove this?
3. **Test it** — add logging, write a minimal repro, or use a debugger.
4. **If wrong, STOP** — go back to Phase 1. Do NOT add another fix on top.

Single hypothesis rule: never test multiple theories at once. That's shotgun debugging.

## Phase 4: Implementation

Only after you understand root cause.

1. **Fix at the source** — not where the error surfaces.
2. **Verify** — run the failing test/scenario. Confirm it passes.
3. **Check for collateral** — run the full test suite. Did you break anything else?
4. **Consider defense-in-depth** — can you add validation at multiple layers?

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| "Add a retry/sleep" without understanding why it's needed | Masks timing bugs; they return under load |
| Fixing where the error appears instead of where it originates | Symptom fix; root cause remains |
| Stacking fixes when the first one didn't work | Shotgun debugging; obscures the real issue |
| "Works on my machine" → skip investigation | Environment difference IS the bug |
| Skipping Phase 1 for "simple" bugs | Simple-looking bugs often have deep causes |

## Child-Agent Pattern

When the platform supports child agents, run in parallel:

- a **reproduction pass** — confirm and characterize the failure
- a **recent-changes pass** — review git history and PRs for related changes
- a **root-cause / instrumentation pass** — add logging, trace data flow

Merge the evidence before choosing a fix.

## Technique References

Load these when the debugging scenario calls for them:

| Technique | File | When to Use |
|-----------|------|-------------|
| Root cause tracing | `root-cause-tracing.md` | Bug manifests deep in call stack; need to trace backward to origin |
| Condition-based waiting | `condition-based-waiting.md` | Flaky tests with arbitrary sleeps/timeouts |
| Defense-in-depth | `defense-in-depth.md` | After finding root cause; want to make the bug structurally impossible |
| Test pollution bisection | `find-polluter.sh` | Unknown test creates unwanted files or state |
