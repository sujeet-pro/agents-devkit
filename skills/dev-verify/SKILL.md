---
name: dev-verify
description: Use before claiming work is complete so you have fresh verification evidence for tests, builds, or runtime behavior
user_invocable: true
arguments:
  - name: scope
    description: "Verification scope: full, tests, build, behavior (default: full)"
    required: false
  - name: target
    description: "Specific file, directory, or test pattern to verify"
    required: false
---

# Verification Before Completion

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

Every completion claim needs fresh evidence. Do not rely on prior test runs or cached results.

## Preflight

Before running verification, run:

`zsh scripts/check-skill-deps.zsh dev-verify`

Detect the project's test runner, linter, type-checker, and build tool from configuration files (`package.json`, `Makefile`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.).

## Required Child Agents

When the platform supports child agents, run at least these in parallel:

- **Test runner**: executes the full test suite (or targeted tests when `target` is specified). Reports pass/fail counts, failure details, and coverage when available.
- **Build and static analysis runner**: executes the linter, type-checker, and build command. Reports each as clean or lists specific failures with file and line references.
- **Behavioral verifier**: identifies the specific behavior or output changed by the current work (from the git diff). Runs a targeted verification of that behavior — specific test files, a curl against a local server, a CLI invocation, or a manual inspection.

## Workflow

1. **Detect tools.** Identify the test runner, linter, type-checker, and build tool from project configuration.
2. **Launch verification agents.** Run test, build/static-analysis, and behavioral passes in parallel.
3. **Collect results.** Merge all verification output.
4. **Report.** Present a structured verification summary.

## Output

```
## Verification Summary

### Tests
- Runner: <test framework>
- Result: <pass count>/<total count> passed
- Failures: <list if any>

### Static Analysis
- Lint: <clean or N issues>
- Types: <clean or N issues>
- Build: <success or failure>

### Behavioral Check
- Changed behavior: <description>
- Verification method: <what was run>
- Result: <confirmed working or issue found>

### Verdict: <PASS or FAIL with blockers listed>
```

## Adjacent Skills

- `/devkit:dev-implement` for the full implementation flow that calls this skill
- `/devkit:pr-finalize` for branch finalization with verification and review
- `/devkit:dev-debug` for investigating verification failures
