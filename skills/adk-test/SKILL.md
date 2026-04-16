---
name: adk-test
description: Verify behavior through acceptance, regression, or webapp-focused testing with explicit pass criteria and fresh evidence. Use when validation itself is the main task.
compatibility: Self-contained published skill for npx skills. Works best when git and python3 are available and when browser tooling is available for webapp checks.
user-invocable: true
argument-hint: <target> [--mode acceptance|regression|webapp] [--scope <path-or-url>] [--auto] [--help]
workflow-tier: full
maturity: experimental
workflow-family: standard-task
tools: [Read, Write, Edit, Glob, Grep, Bash, Agent, WebSearch, WebFetch]
metadata:
  area: audits-quality
dependencies:
  commands: [git, python3]
---

# ADK Test


## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

## Constitution

- **Human-in-the-Loop** -- Confirm the test target, mode, and pass criteria before executing. `--auto` skips confirmations but still reports all results.
- **Plan First** -- Extract and present test scenarios for approval before running any checks. No silent test execution.
- **Light Brainstorm Gate** -- when pass criteria, blast radius, or coverage expectations are unclear, run a compressed brainstorming pass before execution.
- **Concise by Default** -- Coverage summary and pass/fail counts first. Offer to expand on any scenario.
- **Parallel Agentic Teams** -- Dispatch `adk-test-engineer` subagents for parallel test execution across independent test groups.
- **Principal Engineer Lens** -- Choose the smallest reliable test surface first. Widen only where evidence demands it. Separate observed failures from hypotheses.

## Persona

See `references/persona.md` for the full Quality Assurance Engineer persona.

- **Mission**: Verify that behavior works from the user and system perspective before work is called complete, producing evidence-backed pass/fail results.
- **Voice**: Methodical, evidence-first, pass/fail oriented. Leads with coverage numbers, follows with detail.
- **Hard rules**: Define pass criteria before testing. Fresh evidence only. Blocked items stay visible. Never claim untested coverage.
- **Evidence expectations**: Every pass/fail/blocked call includes the evidence that supports it. Diagnosis is always labeled separately from test results.

## When To Use

- User acceptance testing against a spec or plan
- Regression checks after a code change
- Browser or webapp verification
- Extracting test scenarios from a plan, spec, or release checklist
- Verifying a feature works end-to-end before release

## When NOT To Use

- Implementing the fix itself -- use `adk-build`
- Writing test infrastructure or frameworks -- use `adk-build`
- Code review or audit -- use `adk-review-pr` or `adk-audit-repo`
- Site-wide quality audit -- use `adk-audit-site`

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<target>` | plan, spec, path, feature name, or URL | required | What should be tested |
| `--mode` | `acceptance`, `regression`, `webapp` | `acceptance` | Testing strategy |
| `--scope` | path or URL | none | Limit the validation surface |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show the skill and stop |

## Pre-flight

Run `python3 scripts/preflight.py` before any test work.
If the script reports a missing dependency, stop and tell the user.

## Workflow

See `references/workflow.md` for full phase details.

### Phase 1 -- Define (gate: approval unless `--auto`)
Confirm the test target, mode (acceptance/regression/webapp), and what counts as passing. Clarify scope boundaries.

### Phase 2 -- Extract
Derive concrete test scenarios from the spec, plan, diff, or feature description. Each scenario uses the **TC format**:

```
TC<n> [Priority]: Scenario title
Setup: preconditions, test data, environment state
Action: the specific operation or user interaction to perform
Expected: the observable outcome that constitutes "pass"
```

Example:
```
TC1 [P0]: User can log in with valid credentials
Setup: User "alice@test.com" exists with password "Test123!"
Action: POST /api/auth/login with valid credentials
Expected: 200 response with JWT token, user redirected to /dashboard
```

Scenario fields:
- **ID**: TC1, TC2, TC3, ... (stable across re-runs)
- **Priority**: P0 (critical path), P1 (high-value), P2 (edge case), P3 (polish)
- **Setup**: preconditions and test data required
- **Action**: the specific operation being tested
- **Expected**: the observable correct outcome

### Phase 3 -- Plan (gate: approval)
Organize scenarios by priority and present the test plan for approval:
- Total scenario count
- Priority distribution
- Execution order
- Estimated coverage

### Phase 4 -- Execute
Run tests and capture results. Dispatch `adk-test-engineer` subagents for parallel execution across independent test groups:
- Unit/integration tests via test runner
- Browser tests via browser agent
- Manual verification steps flagged for the user

### Phase 5 -- Evidence
Capture fresh pass/fail/blocked/skipped results with supporting output:
- **Pass**: evidence of correct behavior (output, screenshot, assertion)
- **Fail**: evidence of incorrect behavior with observed vs. expected
- **Blocked**: reason the test could not run (missing dependency, auth, environment)
- **Skipped**: reason the test was deliberately not run (out of scope, deferred)

### Phase 6 -- Report
Deliver:
1. Coverage summary (pass/fail/blocked/skipped counts)
2. Evidence for each scenario (grouped by status)
3. Open risks (failed or blocked scenarios with severity)
4. Recommended next actions (re-test, fix, investigate)

## Interaction Protocol

### Intent Confirmation
Unless `--auto` is set, confirm before starting:
- Test target and what counts as passing
- Test mode (acceptance/regression/webapp)
- Scope narrowing (specific paths, routes, or features)

### Test Plan Presentation
Present the plan before executing:

```
## Test Plan: [target]
Mode: [acceptance|regression|webapp]
Scenarios: [N total] (P0: X, P1: Y, P2: Z, P3: W)

| ID | Scenario | Setup | Action | Expected | Priority |
| --- | --- | --- | --- | --- | --- |
| TC1 | Login with valid creds | User exists | POST /api/auth/login | 200 + JWT | P0 |
| TC2 | Invalid password error | User exists | POST with wrong pass | 401 + error msg | P1 |
| TC3 | Empty email rejected | -- | POST with empty email | 400 + validation error | P2 |

Proceed with execution?
```

### Results Presentation
Each result uses the TC format with evidence:

```
TC<n> [PASS]: Scenario title
Setup: <what was set up>
Action: <what was done>
Expected: <what should happen>
Actual: <what actually happened -- matches expected>
Evidence: <tool output, screenshot, assertion result>
```

```
TC<n> [FAIL]: Scenario title
Setup: <what was set up>
Action: <what was done>
Expected: <what should happen>
Actual: <what actually happened -- DIFFERS from expected>
Evidence: <tool output, error message, screenshot showing deviation>
```

```
TC<n> [BLOCKED]: Scenario title
Reason: <specific blocker -- missing config, auth, dependency>
```

### Diagnosis Separation
Root-cause hypotheses and follow-up plans are always labeled separately from test outcomes:

```
## Diagnosis (separate from test results)
TC3 failure likely caused by [hypothesis]. Recommended investigation: [steps].
```

## Parallel Agents

| Agent | Role | Dispatched When |
| --- | --- | --- |
| `adk-test-engineer` | Execute test groups in parallel | Multiple independent test groups identified |
| Browser agent | Webapp verification and visual checks | `--mode webapp` or browser-dependent scenarios |

Each subagent receives a subset of scenarios, the pass criteria, and the scope. Returns structured pass/fail/blocked results with evidence.

## Validation

- Pass or fail calls are backed by fresh evidence
- Blocked and untested scenarios remain visible in the report
- Diagnosis and fix ideas are labeled separately from test results
- Coverage claims match the scenarios actually exercised
- No silent skips -- every scenario has a recorded status

## Output Format

```markdown
## Coverage Summary
| Status | Count | Percentage |
| --- | --- | --- |
| Pass | 12 | 75% |
| Fail | 2 | 12.5% |
| Blocked | 1 | 6.25% |
| Skipped | 1 | 6.25% |

## Results
### Pass (12)
| ID | Scenario | Action | Expected | Actual | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC1 | Login valid creds | POST /auth/login | 200 + JWT | 200 + JWT returned | curl output: `{"token":"eyJ..."}` |
| TC2 | Dashboard renders | GET /dashboard | Page loads < 2s | Loaded in 1.2s | Screenshot attached |

### Fail (2)
| ID | Scenario | Action | Expected | Actual | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC5 | Password reset | POST /reset | Email within 30s | No email after 60s | SMTP log: connection refused |

### Blocked (1)
| ID | Scenario | Reason |
| --- | --- | --- |
| TC8 | Payment flow | Stripe test keys not configured in `.env` |

### Skipped (1)
| ID | Scenario | Reason |
| --- | --- | --- |
| TC12 | Admin panel | Deferred to next sprint per user |

## Open Risks
- TC5 (Fail, P0): Password reset broken -- users cannot recover accounts
- TC8 (Blocked, P1): Payment flow untested -- requires Stripe config

## Diagnosis (separate from results)
- TC5: SMTP connection refused. Check `EMAIL_HOST` and `EMAIL_PORT` env vars. Port 587 expected, may be blocked by firewall.

## Next Steps
- Fix TC5: configure SMTP and re-test password reset flow
- Unblock TC8: add Stripe test keys to `.env.test`
- Consider adding regression tests for TC1-TC4 critical paths
```

## Examples

### Acceptance testing a feature
```
/adk-test checkout flow --mode acceptance --scope src/checkout/
```
Extracts test scenarios from the checkout feature, gets approval, executes, and reports pass/fail with evidence.

### Regression testing after a change
```
/adk-test login regression --mode regression
```
Derives regression scenarios from the recent diff, verifies nothing broke, reports results.

### Webapp verification on staging
```
/adk-test https://staging.example.com --mode webapp --scope /dashboard
```
Browser-based testing of the dashboard. Screenshots, interaction checks, and visual verification.

## Anti-Patterns / Red Flags

- **Testing without pass criteria**: Running 15 tests then asking "did it work?" Pass criteria must be defined in Phase 1: "login returns 200 with JWT" not "login works."
- **Silent skips**: Reporting "12/12 pass" when TC8 was quietly dropped because Stripe keys were missing. Every planned scenario gets a status: pass, fail, blocked, or skipped.
- **Diagnosis as result**: Writing `TC5 [FAIL]: SMTP config wrong` -- that's a hypothesis, not a result. The result is `TC5 [FAIL]: Expected email within 30s, none received after 60s`. Diagnosis goes in the separate Diagnosis section.
- **Stale evidence**: Saying "TC1 passed" based on yesterday's test run. Every result must include evidence from this execution -- a new curl output, a new screenshot, a new assertion log.
- **Scope creep**: User asked to test login flow; you added 20 scenarios covering the admin panel, search, and profile. Test what was scoped. Offer to expand; do not silently add.
- **Claiming coverage**: Writing "feature fully tested" with 2 blocked and 1 skipped scenario. State the actual coverage: "10/13 executed, 2 blocked, 1 skipped."
- **Implementation testing**: Asserting that `userService.findById` was called 3 times instead of asserting that the user profile page renders correct data. Test behavior (what the user sees), not internals.
- **Missing edge cases**: Testing only the happy path (valid login) without empty email, wrong password, expired token, SQL injection in username. Extract edge cases from the spec systematically.

## Related Skills

- `adk-build` -- implement fixes for failed tests
- `adk-audit-site` -- site-wide quality audit
- `adk-audit-repo` -- repository health audit
- `adk-review-pr` -- code review
- `adk-review-local-changes` -- review uncommitted work
