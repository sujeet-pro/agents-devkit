# ADK Test Workflow

## Phase 1 -- Define
**Gate: approval unless `--auto`**

1. Confirm the test target (spec, plan, path, feature name, or URL)
2. Confirm the test mode: `acceptance`, `regression`, or `webapp`
3. Define what counts as passing (explicit pass criteria)
4. Identify scope boundaries (what is in, what is out)
5. If `--auto`, log the resolved target, mode, and pass criteria, then proceed

**Approval prompt**: "Test [target] in [mode] mode. Pass criteria: [criteria]. Scope: [boundaries]. Proceed?"

## Phase 2 -- Extract

1. Read the source material: spec, plan, diff, feature description, or live behavior
2. Derive concrete test scenarios using the **TC format**, each with:
   - **ID**: TC1, TC2, TC3, ... (stable across re-runs)
   - **Description**: what behavior is being verified
   - **Setup**: preconditions, test data, environment state required
   - **Action**: the specific operation or user interaction to perform
   - **Expected**: the observable outcome that constitutes "pass"
   - **Priority**: P0 (critical path), P1 (high-value), P2 (edge case), P3 (polish)
3. Systematically extract edge cases from the spec:
   - Empty/null inputs, boundary values (min, max, off-by-one)
   - Error paths: invalid input, unauthorized access, network failure
   - Concurrent operations: race conditions, duplicate submissions
   - State transitions: expired tokens, deleted resources, locked accounts
4. Map scenarios to acceptance criteria or requirements when available
5. Flag scenarios that require browser, external services, or manual steps

## Phase 3 -- Plan
**Gate: approval**

1. Organize scenarios by priority (P0 first, then P1, P2, P3)
2. Group into independent test groups for parallel execution
3. Present the plan:
   - Total scenario count
   - Priority distribution (P0: X, P1: Y, P2: Z, P3: W)
   - Execution order and grouping
   - Estimated coverage and known gaps
4. Identify scenarios that will need subagent dispatch (browser tests, parallel groups)
5. Get explicit approval before proceeding to execution

**Plan format**:
```
## Test Plan: [target]
Mode: [mode] | Scenarios: [N] | Groups: [M]
| ID | Scenario | Setup | Action | Expected | Priority | Group |
| --- | --- | --- | --- | --- | --- | --- |
| TC1 | Login valid | User exists | POST /login | 200 + JWT | P0 | A |
| TC2 | Login wrong pw | User exists | POST wrong pw | 401 + error | P1 | A |
| TC3 | Empty email | -- | POST empty | 400 + validation | P2 | A |
```

## Phase 4 -- Execute

1. Execute test groups, dispatching `adk-test-engineer` subagents for parallel groups:
   - Each subagent receives its scenario subset, pass criteria, and scope
   - Each subagent returns structured results: pass/fail/blocked/skipped with evidence
2. For `webapp` mode, dispatch browser agent for visual and interaction tests
3. Run sequential groups in priority order (P0 first)
4. If a P0 scenario fails, complete the current group but flag the failure immediately
5. Collect all raw output, screenshots, and assertion results

**Subagent contract**: Each subagent receives scenario IDs, descriptions, expected outcomes, and scope. Returns per-scenario status with evidence.

## Phase 5 -- Evidence

1. Compile results from all execution sources (direct, subagents, browser)
2. For each scenario, record using TC format:
   - **Pass**: `TC<n> [PASS]` with Setup, Action, Expected, Actual (matches), and Evidence (tool output, screenshot, assertion)
   - **Fail**: `TC<n> [FAIL]` with Setup, Action, Expected, Actual (DIFFERS -- state the specific deviation), and Evidence
   - **Blocked**: `TC<n> [BLOCKED]` with the specific reason (e.g., "Stripe test keys not in `.env`", not "config issue")
   - **Skipped**: `TC<n> [SKIPPED]` with the explicit reason (e.g., "deferred to next sprint per user", not "skipped")
3. Verify evidence is fresh (from this run, not cached or stale)
4. Cross-reference results against the original test plan to ensure no silent gaps
5. Every TC in the plan must appear in results -- missing TCs are reported as BLOCKED with reason "not executed"

## Phase 6 -- Report

1. Coverage summary: pass/fail/blocked/skipped counts and percentages
2. Results grouped by status:
   - Pass: scenario ID, description, evidence summary
   - Fail: scenario ID, description, expected vs. observed
   - Blocked: scenario ID, description, blocking reason
   - Skipped: scenario ID, description, skip reason
3. Open risks: failed and blocked scenarios with severity and impact assessment
4. Diagnosis section (always separate from results): root-cause hypotheses for failures
5. Recommended next actions: re-test, fix, investigate, expand coverage
6. Offer to re-test specific scenarios or expand to additional coverage areas

## Validation Rules

- Every scenario has a recorded status (pass, fail, blocked, or skipped)
- Pass/fail calls are backed by fresh evidence from this test run
- Blocked and skipped scenarios remain visible in the final report
- Diagnosis and fix ideas are labeled separately from test outcomes
- Coverage claims match the scenarios actually exercised
- No silent skips -- if a planned scenario was not run, it must appear as blocked or skipped
- If runtime verification could not run, the report says so explicitly
