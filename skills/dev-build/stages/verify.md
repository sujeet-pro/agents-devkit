# Verify Mode

Verification before claiming work is complete, fixed, or passing. Requires running verification commands and confirming output before making any success claims.

**Core principle:** Evidence before claims, always. Claiming work is complete without verification is dishonesty, not efficiency.

## Workflow

This stage uses the **Quick Action** workflow: confirm → execute → verify.

## Exploration Guidance

Identify what needs verification:
- What claims are being made? (tests pass, build succeeds, requirements met)
- What commands prove each claim?
- What is the scope? (targeted files or full suite)

## Execution Instructions

### The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

### The Gate Function

```
BEFORE claiming any status:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

### Verification Requirements

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Requirements met | Line-by-line checklist | Tests passing |

### Parallel Verification

When child agents are available, launch verification agents in parallel:
- **Test runner**: execute full or scoped test suite
- **Lint checker**: run linter on affected files
- **Type checker**: run type-checker
- **Build verifier**: run build command

Merge results and report.

### Red Flags — STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification
- About to commit/push/PR without verification
- Trusting agent success reports without independent verification
- Relying on partial verification

## Validation Criteria

Run the self-review loop (up to 10 iterations):
1. Every claim has been verified with fresh evidence
2. No "should pass" or "looks correct" language remains
3. All test output has been read and parsed
4. Exit codes have been checked
5. If requirements checklist exists, every item verified line-by-line

## Output Format

```markdown
## Verification Report

### Claims Verified
| Claim | Command | Result | Evidence |
|-------|---------|--------|----------|
| Tests pass | `npm test` | 34/34 pass | exit 0 |
| Lint clean | `npm run lint` | 0 errors | exit 0 |
| Types clean | `npx tsc --noEmit` | 0 errors | exit 0 |
| Build | `npm run build` | success | exit 0 |

### Requirements Checklist
- [x] <requirement 1>: verified by <evidence>
- [x] <requirement 2>: verified by <evidence>

### Status: VERIFIED / ISSUES FOUND
```
