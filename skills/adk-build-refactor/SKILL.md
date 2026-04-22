---
name: adk-build-refactor
description: Restructure code without changing observable behavior - rename, extract, inline, dedupe, simplify, reshape modules - while keeping tests green throughout. Use when the goal is a cleaner shape, not a new behavior or bug fix. Do not use when behavior changes (use adk-build-feature), framework versions change (use adk-build-migrate), or only tests change (use adk-build-test).
---

# ADK Build / Refactor

Standalone task skill under the `adk-build` category router. Improves code structure with a behavior-preserving sequence of small, individually validated steps.

## When to use

- Rename, extract, inline, or move code while preserving behavior.
- Deduplicate parallel implementations.
- Simplify a tangled module without changing what it does.
- Replace an internal abstraction with a clearer one (signatures change, behavior does not).

## When NOT to use

- Behavior changes -> `adk-build-feature`
- Framework / runtime / library version migration -> `adk-build-migrate`
- Only tests change -> `adk-build-test`
- Dependency cleanup only -> `adk-build-deps`
- UI / frontend restructure -> `adk-frontend-feature`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<refactor>` | yes | What to restructure (e.g. "extract auth helpers from controllers") |
| `<scope>` | optional | Path to limit reads and changes |
| `<safety bar>` | optional | `tests-required` (default) / `manual-only` (when no tests exist) |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate what changes structurally and what must NOT change behaviorally. Approval gate unless `--auto`.
2. **Baseline** - run the existing test suite (or document the manual baseline) and capture green status. No refactor starts on red.
3. **Map** - inventory call sites, public APIs, and dependents that the refactor will touch. Read; do not guess.
4. **Plan** - cut into small behavior-preserving steps (rename -> move -> extract -> inline). Each step ends with passing tests.
5. **Step-by-step execute** - apply one step, run tests, commit (or stage), repeat. Never batch two structural changes between validations.
6. **Validate (per `build-refactor-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/build-refactor-<slug>-validator.md` before the final report.
7. **Diff review** - re-read the cumulative diff for accidental behavior changes (extra checks added, error messages changed, defaults changed).
7. **Report** - changed files; final test status; what was renamed / moved / extracted; what callers must update if any public API changed.

## Behavior-preservation rules

- Tests must be green before, between, and after each step.
- Do not "improve" error messages or default values during refactor; that is a feature change - extract it.
- If you must change a public API, list every external caller in the report.
- New abstractions added during refactor must be used somewhere right now; do not leave dead code "for future use".
- If a refactor exposes a real bug, stop, surface it, and let the user choose to fix in a separate `adk-build-feature` pass.

## Common refactor patterns

| Pattern | When | Notes |
| --- | --- | --- |
| Rename | Naming is misleading | Keep semantic meaning; update all call sites in one step |
| Extract function / module | Unit is too large or duplicated | Verify behavior preserved by tests at each extraction |
| Inline | Indirection adds no value | Inline first, then simplify |
| Move | File is in the wrong place | Move alone; do not also rename in the same step |
| Replace conditional with polymorphism | Branch explosion on type tag | Tests must cover each branch first |
| Introduce parameter object | Long parameter list with cohesion | Migrate callers one at a time |
| Dedupe | Two near-identical code paths | Extract common, keep differences explicit |

## Output format

```
## Refactor: <summary>

## Behavior Preserved
- Tests: <command> - PASS
- Manual checks: <bullets if any>

## Changed Files
- `path/to/file.ts` - <one-line description>

## Public API Changes
- <none, or list with caller impact>

## Steps Taken
1. <step>
2. <step>

## Remaining Risk
- <open item>

Need more detail on any section?
```

## Anti-patterns

- Mixing a behavior change into a refactor pass. Split it.
- Refactoring on red. Stabilize tests first.
- Renaming and moving in the same step. One change per validation.
- Adding "extension points" or interfaces with one implementation. YAGNI.
- Marking the refactor done while the diff still has commented-out code.
- Skipping the baseline test run. Without it you cannot prove behavior preservation.

## Examples

```
adk-build-refactor "Extract HTTP retry helper from each controller into src/http/retry.ts" --scope src/controllers/
```

```
adk-build-refactor "Inline the single-call AuthFacade and delete it" --scope src/auth/
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-refactor-clarifying-questions.md`) and reports the choices.

1. **What is the single concern of this refactor: rename, extract, inline, dedupe, simplify, restructure modules?** — _How to pick:_ Pick exactly one. Multi-concern refactors hide regressions. If multiple are needed, run the skill multiple times in series.
2. **Is the touched code covered by tests today?** — _How to pick:_ Yes → proceed. No → write characterization tests first (capture current behavior even if quirky), then refactor.
3. **What is the acceptable blast radius (file, module, package, repo-wide)?** — _How to pick:_ Smaller is safer. Repo-wide rename = one commit per package + automation; never a single mega-commit.

**Default report:** Result + before/after test output (identical) + changed-files table + remaining cleanup opportunities.

**Detailed report (on request or `--verbose`):** Add: per-commit diff summary, complexity metric delta (LOC, cyclomatic, duplication), reasoning for each structural choice.

**Artifact:** `behavior-preserving-diff` — Series of small commits, each compiling and passing tests, with before/after test output captured in .temp/notes/.

**Artifact path:** .temp/plans/refactor-<slug>.md (plan), .temp/notes/refactor-<slug>-before.txt + -after.txt (test output snapshots)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-refactor-clarifying-questions.md`) and reports the choices.

1. **What is the single concern of this refactor: rename, extract, inline, dedupe, simplify, restructure modules?** — _How to pick:_ Pick exactly one. Multi-concern refactors hide regressions. If multiple are needed, run the skill multiple times in series.
2. **Is the touched code covered by tests today?** — _How to pick:_ Yes → proceed. No → write characterization tests first (capture current behavior even if quirky), then refactor.
3. **What is the acceptable blast radius (file, module, package, repo-wide)?** — _How to pick:_ Smaller is safer. Repo-wide rename = one commit per package + automation; never a single mega-commit.

## Default vs detailed output

**Default report:** Result + before/after test output (identical) + changed-files table + remaining cleanup opportunities.

**Detailed report (on request or `--verbose`):** Add: per-commit diff summary, complexity metric delta (LOC, cyclomatic, duplication), reasoning for each structural choice.

**Artifact:** `behavior-preserving-diff` — Series of small commits, each compiling and passing tests, with before/after test output captured in .temp/notes/.

**Artifact path:** .temp/plans/refactor-<slug>.md (plan), .temp/notes/refactor-<slug>-before.txt + -after.txt (test output snapshots)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/build-refactor-anti-patterns.md` | Things to avoid when running this skill. |
| `references/build-refactor-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/build-refactor-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/build-refactor-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/build-refactor-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/build-refactor-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/build-refactor-persona.md` | The agent persona that drives this skill. |
| `references/build-refactor-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/build-refactor-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/build-refactor-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
