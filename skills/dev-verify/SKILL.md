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
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
  - name: plan
    description: "Path to plan file to extract expected deliverables from"
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

## Goal-Backward Verification

The automated checks above (tests, lint, types, build) confirm that code is *correct*. Goal-backward verification confirms that code is *complete* — that every planned deliverable actually exists, does real work, is connected, and carries live data.

Run this layer **after** the automated verification passes. If a `plan` argument is provided, extract expected deliverables from the plan file. Otherwise, infer deliverables from the git diff and any linked issue or PR description.

### 4-Level Verification Cascade

Every expected deliverable must pass all four levels in order. Stop at the first failure.

| Level | Check | Pass criteria | Failure status |
|-------|-------|---------------|----------------|
| 1. Exists | File or component is present on disk | Path resolves to an existing file | `MISSING` |
| 2. Substantive | Not a stub or placeholder | >20 meaningful lines, no empty returns, no placeholder text, no TODO-only content | `STUB` |
| 3. Wired | Imported AND used by at least one other module | At least one import/require referencing this module from another file; not orphaned | `ORPHANED` |
| 4. Data flowing | Upstream data sources produce real data; props/args are connected to live state | Data sources return non-hardcoded values; component props are bound to store/context/API responses | `HOLLOW` |

### Stub Detection Patterns

Use these concrete patterns when evaluating Level 2 (Substantive):

- **Empty function bodies**: functions whose body is only `{}`, `pass`, `return`, `return null`, `return undefined`, or `return None`
- **TODO-only content**: files or functions where the only non-whitespace content is `// TODO`, `# TODO`, `/* TODO */`, or similar markers
- **Placeholder text**: presence of "Lorem ipsum", "Sample data", "Test content", "placeholder", "FIXME: implement" as the primary content
- **Render-nothing components**: React/Vue/Svelte components that return `null`, an empty fragment, or only a bare `<div />` / `<div></div>` with no meaningful children
- **Hardcoded API responses**: route handlers or API functions that return static/literal objects without reading from any data source, database, or external service

### Interactive Deliverable Verification

For each expected deliverable, produce a structured assessment. When `mode` is `interactive` (the default), prompt the user for an action on each non-VERIFIED deliverable. When `mode` is `auto-approve`, automatically choose `[F]ix now` for STUB/ORPHANED/HOLLOW and flag MISSING for investigation.

```
## Deliverable [N/total] - <expected outcome>

Level 1 (Exists): ✓/✗ <path or MISSING>
Level 2 (Substantive): ✓/✗ <line count, stub patterns found>
Level 3 (Wired): ✓/✗ <import count, usage sites>
Level 4 (Data flowing): ✓/✗ <data source status>

Overall: [VERIFIED|MISSING|STUB|ORPHANED|HOLLOW]

Action: [F]ix now | [D]efer | [A]ccept as-is | [I]nvestigate
```

After all deliverables are assessed, append a **Goal-Backward Summary** to the Verification Summary output:

```
### Goal-Backward Verification
- Deliverables checked: <total>
- Verified: <count>
- Missing: <count>
- Stubs: <count>
- Orphaned: <count>
- Hollow: <count>

### Goal-Backward Verdict: <PASS or FAIL with list of non-verified deliverables>
```

The overall verification verdict is PASS only when **both** the automated checks and the goal-backward checks pass.

## Adjacent Skills

- `/devkit:dev-implement` for full implementation with built-in verification, including goal-backward checks
- `/devkit:pr-finalize` for branch finalization with verification and review
- `/devkit:dev-debug` for investigating verification failures
- `/devkit:verify-uat` for user acceptance testing after technical verification passes
