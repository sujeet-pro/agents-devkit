---
title: 'build-feature'
description: 'Implement a new feature, fix a bug with root-cause analysis, or enhance existing behavior - with a short plan, scoped reads, smallest correct change, and repo-native validation. Use when the deliverable is a code change that adds, changes, or fixes behavior. Do not use for restructuring without behavior change (use adk-build-refactor), framework upgrades (use adk-build-migrate), or test-only work (use adk-build-test).'
skill_name: build-feature
category: router
---
# ADK Build / Feature

Standalone task skill under the `@adk:build` (a.k.a. `adk-build`) category router. Delivers the smallest correct implementation that satisfies the requirement, backed by evidence and validation.

## When to use

- Build a new feature or component.
- Fix a bug after root-cause analysis.
- Enhance or extend existing behavior.
- Validate whether a prior change is actually complete (verify mode).
- Debug a reported failure with systematic hypothesis testing (debug mode).

## When NOT to use

- Behavior unchanged, structure changes -> `@adk:build-refactor` (a.k.a. `adk-build-refactor`)
- Framework / library version migration -> `@adk:build-migrate` (a.k.a. `adk-build-migrate`)
- Test authoring only -> `@adk:build-test` (a.k.a. `adk-build-test`)
- Dependency hygiene -> `@adk:build-deps` (a.k.a. `adk-build-deps`)
- UI / frontend feature -> `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`)
- Reviewing existing changes -> `@adk:review-local` (a.k.a. `adk-review-local`)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task>` | yes | What to build, fix, or verify |
| `<mode>` | optional | `implement` (default) / `debug` / `verify` |
| `<plan>` | optional | Path to a roadmap or plan to follow |
| `<scope>` | optional | Path to limit reads and changes |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - clarify task, mode, scope, validation target. Approval gate unless `--auto`.
2. **Scope** - read only the relevant code:
   - `implement`: target code + immediate dependencies.
   - `debug`: error context, stack trace, recent `git log`, related tests.
   - `verify`: validation targets and existing test coverage.
3. **Plan** - write or refine a short ordered plan. Approval gate unless `--auto` or change is trivial single-file. In `debug`, list 2-3 hypotheses ranked by likelihood. In `verify`, skip this phase.
4. **Implement** - apply the smallest correct change in the smallest readable diff. Stay inside scope; flag any necessary out-of-scope work.
5. **Validate** - run the smallest relevant repo-native checks first (target test, lint on changed files, type-check on touched module). Never claim success without command output.
6. **Report** - changed files with one-line diff summary; validation evidence; remaining risk; offer depth on request.

## Mode flows

```mermaid
flowchart LR
    implement[implement] --> validate
    debug[debug] --> hypothesize --> isolate --> fix --> validate
    verify[verify] --> validate
    validate --> report
```

### Debug mode (additional discipline)

1. Capture the failure: error message, stack trace, repro steps, expected vs. actual.
2. Hypothesize: 2-3 plausible root causes ranked by likelihood; check recent commits.
3. Test hypotheses: trace execution flow, add strategic logs, check edge cases (null, empty, boundary).
4. Isolate root cause: distinguish trigger from cause; verify it explains all symptoms.
5. Fix: minimal change targeting the root cause; add regression test.
6. Verify: reproduce the original failure first, then confirm fix removes it.

Common bug patterns to keep in mind:

- Logic: off-by-one, boolean inversion, missing null check, encoding.
- Concurrency: race, deadlock, shared mutable state, unhandled rejection.
- Resources: memory / file-handle / connection leak; unbounded growth.
- Integration: API contract drift, serialization, timezone, timeout.

### Verify mode

No code changes. Run the validations that prove the prior change is complete and correct. Report gaps if found and recommend the next action.

## Slicing discipline

- Implement in thin vertical slices: one logical change, validated, then expand.
- Never write more than ~100 lines without running validation.
- Each slice leaves the codebase buildable and testable.
- Commit (or stage) after each verified slice with a descriptive message.
- For multi-slice features, gate incomplete UI behind a feature flag.

## Output format

```
## Summary
<1-2 sentence result>

## Mode
<implement | debug | verify>

## Changed Files
- `path/to/file.ts` - <one-line description>

## Validation
<command output, or explicit "not verified" with reason>

## Remaining Risk
- <open item>

Need more detail on any section?
```

## Hard rules

- Plan before non-trivial code changes.
- Read the code before proposing a change to it.
- Preserve user work in progress.
- Use repo-native validation; do not invent commands.
- Never say "tests pass" or "bug fixed" without fresh evidence.
- Prefer simple, readable solutions over clever ones.
- If a claim cannot be verified, say so explicitly.

## Anti-patterns

- Implementing without reading the relevant code first.
- Skipping the plan for multi-file changes.
- Claiming validation passed without running it.
- Fixing symptoms instead of root causes in debug mode.
- Over-engineering: abstractions, config layers, extensibility the task did not require.
- Mixing feature work with unrelated refactoring in the same change.
- Writing 200+ lines before any validation runs.

## Examples

```
adk-build-feature "Add retry logic to the HTTP client" --scope src/http/
```

```
adk-build-feature "Users report 500s on /api/health" --mode debug
```

```
adk-build-feature "Confirm the pagination fix works" --mode verify --scope src/api/pagination.ts
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-feature-clarifying-questions.md`) and reports the choices.

1. **Is this an implement, debug, or verify task?** — _How to pick:_ Implement = building from spec/roadmap. Debug = a failure exists and we need root cause + fix. Verify = no code change, prove a prior change is correct.
2. **What is the validation target (tests to pass, behavior to demonstrate, metric to hit)?** — _How to pick:_ Pick the smallest signal that proves correctness. Prefer existing tests > new test > manual repro.
3. **Can the work be split into thin vertical slices, or must it land atomically?** — _How to pick:_ Split unless the change is trivially atomic (one function, one config). Slicing reduces blast radius and gives faster validation.

**Default report:** Result + changed-files table (path + one-line diff summary) + validation evidence + remaining risk.

**Detailed report (on request or `--verbose`):** Add: per-slice plan with validation each slice, hypothesis log if debug mode, ruled-out approaches with reason.

**Artifact:** `code-change-set` — Diff (committed or staged) + test output + lint output + type-check output. Plan/notes mirrored in .temp/.

**Artifact path:** .temp/plans/feature-<slug>.md (plan), .temp/notes/feature-<slug>-debug.md (hypothesis log if debug). Code lands in the repo proper, validated commit-by-commit.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-feature-clarifying-questions.md`) and reports the choices.

1. **Is this an implement, debug, or verify task?** — _How to pick:_ Implement = building from spec/roadmap. Debug = a failure exists and we need root cause + fix. Verify = no code change, prove a prior change is correct.
2. **What is the validation target (tests to pass, behavior to demonstrate, metric to hit)?** — _How to pick:_ Pick the smallest signal that proves correctness. Prefer existing tests > new test > manual repro.
3. **Can the work be split into thin vertical slices, or must it land atomically?** — _How to pick:_ Split unless the change is trivially atomic (one function, one config). Slicing reduces blast radius and gives faster validation.

## Default vs detailed output

**Default report:** Result + changed-files table (path + one-line diff summary) + validation evidence + remaining risk.

**Detailed report (on request or `--verbose`):** Add: per-slice plan with validation each slice, hypothesis log if debug mode, ruled-out approaches with reason.

**Artifact:** `code-change-set` — Diff (committed or staged) + test output + lint output + type-check output. Plan/notes mirrored in .temp/.

**Artifact path:** .temp/plans/feature-<slug>.md (plan), .temp/notes/feature-<slug>-debug.md (hypothesis log if debug). Code lands in the repo proper, validated commit-by-commit.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/build-feature-anti-patterns.md` | Things to avoid when running this skill. |
| `references/build-feature-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/build-feature-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/build-feature-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/build-feature-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/build-feature-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/build-feature-persona.md` | The agent persona that drives this skill. |
| `references/build-feature-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/build-feature-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/build-feature-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
