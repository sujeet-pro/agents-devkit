---
name: dev-debug
description: Use when investigating bugs, test failures, or unexpected behavior so you find root cause before applying fixes
arguments:
  - name: issue
    description: "Description of the bug, test failure, or unexpected behavior"
    required: false
  - name: forensics
    description: "Enable forensics mode for post-mortem investigation of a past incident (default: false)"
    required: false
  - name: resume
    description: "Path to a previous debug session to resume"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
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

## Persistent Debug State

Save debug session state to `.temp/debug/<issue-slug>.md` so debugging can resume across sessions:

```markdown
---
issue: <brief description>
created: <ISO-8601>
updated: <ISO-8601>
status: investigating | hypothesis-testing | root-cause-found | fixed | deferred
---

# Debug Session: <issue>

## Evidence Collected
- <evidence 1>
- <evidence 2>

## Hypotheses
### Hypothesis 1: <description>
- Status: [testing|confirmed|disproved]
- Evidence for: <list>
- Evidence against: <list>
- Test performed: <what was tried>

## Root Cause
<identified root cause, or "still investigating">

## Fix Applied
<description of fix, or "pending">
```

When `resume` is provided, load the debug session and continue from where it left off.

## Interactive Hypothesis Loop

Present each hypothesis to the user for confirmation before testing:

```text
## Hypothesis [N] - Confidence: NN%

Claim: "I believe <X> happens because <Y>"

Evidence for:
- <supporting evidence>

Evidence against:
- <contradicting evidence>

Test plan: <how to confirm or disprove>

Action: [T]est this hypothesis | [R]efine it | [S]kip to next | [I] need more evidence first
```

After testing, present results:
```text
## Hypothesis [N] Result

Test: <what was tested>
Result: [CONFIRMED ✓ | DISPROVED ✗ | INCONCLUSIVE ?]
New evidence: <what we learned>

Next: [P]roceed to fix | [N]ew hypothesis | [I]nvestigate deeper
```

## Forensics Mode

When `forensics=true`, run post-mortem investigation of a past incident:
1. **Collect artifacts**: logs, error reports, git history around the incident time
2. **Build timeline**: reconstruct the sequence of events
3. **Identify contributing factors**: what conditions made this possible
4. **Root cause analysis**: use the 5 Whys technique
5. **Present findings**:
```text
## Forensics Report

Timeline:
1. <event at time T>
2. <event at time T+1>

Contributing factors:
- <factor 1>
- <factor 2>

Root cause: <identified cause>

Recommendations:
- <how to prevent recurrence>
```

## Adjacent Skills

- `/devkit:dev-verify` — run after applying a fix to verify correctness
- `/devkit:session-handoff` — pause a long debug session and hand off context
