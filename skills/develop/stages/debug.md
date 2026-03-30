# Debug Mode

Systematic debugging for bugs, test failures, and unexpected behavior. Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Gather evidence, reproduce bug, trace data flow; Root cause analysis replaces proposal |
| 2. Approach Selection | skip | Debugging follows a fixed methodology; Fix is validated by tests, not iteration |
| 3. Planning | skip | Single targeted fix, not a plan |
| 4. Execute | yes | Four-phase debugging methodology |
| 5. Validate & Learn | yes | Verify fix, check for regressions |

## Exploration Guidance

Gather evidence before doing anything:
- Read error messages and stack traces completely
- Reproduce the bug consistently
- Check recent changes (`git diff`, `git log`)
- Identify the affected component and data flow

## Execution Instructions

### The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed the root cause investigation, you cannot propose fixes.

### Phase A: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** — don't skip past errors or warnings. They often contain the exact solution. Read stack traces completely.

2. **Reproduce Consistently** — can you trigger it reliably? What are the exact steps? If not reproducible, gather more data — don't guess.

3. **Check Recent Changes** — git diff, recent commits, new dependencies, config changes, environmental differences.

4. **Gather Evidence in Multi-Component Systems** — for each component boundary: log what enters, log what exits, verify environment propagation, check state at each layer. Run once to gather evidence showing WHERE it breaks.

5. **Trace Data Flow** — where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not at symptom.

### Phase B: Pattern Analysis

1. **Find Working Examples** — locate similar working code in the same codebase
2. **Compare Against References** — read reference implementations completely, don't skim
3. **Identify Differences** — list every difference between working and broken, however small
4. **Understand Dependencies** — what settings, config, environment does this need?

### Phase C: Hypothesis and Testing

1. **Form Single Hypothesis** — state clearly: "I think X is the root cause because Y"
2. **Test Minimally** — make the SMALLEST possible change to test the hypothesis. One variable at a time.
3. **Verify Before Continuing** — did it work? Yes -> Phase D. No -> form NEW hypothesis. Don't add more fixes on top.

### Phase D: Implementation

1. **Create Failing Test Case** — simplest possible reproduction, automated if possible. MUST have before fixing.
2. **Implement Single Fix** — address the root cause. ONE change at a time. No "while I'm here" improvements.
3. **Verify Fix** — test passes? No other tests broken? Issue actually resolved?

**If 3+ fixes failed:** STOP and question the architecture. Each fix revealing new problems in different places indicates an architectural problem, not a bug. Discuss with the user before attempting more fixes.

### Red Flags — STOP and Return to Phase A

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time" | Systematic debugging is FASTER than guess-and-check. |
| "I see the problem" | Seeing symptoms is not understanding root cause. |
| "One more fix attempt" | 3+ failures = architectural problem. Question the pattern. |

## Validation Criteria

Run the self-review loop (up to 10 iterations):
1. Failing test now passes
2. No other tests broken
3. Fix addresses root cause, not symptom
4. No unnecessary changes bundled with the fix
5. All tests pass, linter clean, type-checker clean
6. Monitoring/logging added if the bug was hard to diagnose
7. Stop when all checks pass

## Output Format

```markdown
## Debugging Summary

Bug: <description>

### Root Cause
<explanation of the root cause>

### Investigation Path
1. <what was checked>
2. <what was found>
3. <what pointed to root cause>

### Fix
- File: <path>
- Change: <what was changed and why>

### Verification
- Failing test: <test name> — now passes
- Regression: no other tests broken
- Tests: <pass/fail count>
- Lint: <clean/issues>
```
