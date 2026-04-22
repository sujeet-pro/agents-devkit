---
name: adk-build-migrate
description: Migrate a framework, runtime, library version, or build tool with explicit breaking-change analysis, scoped per-file changes, and validation between groups. Use when the change is a version bump or tool replacement that has API or behavior implications across the codebase. Do not use for simple package upgrades with no API changes (use adk-build-deps) or for new features (use adk-build-feature).
---

# ADK Build / Migrate

Standalone task skill under the `adk-build` category router. Replaces a framework, runtime, library version, or build tool with a methodical, validated migration.

## When to use

- Major-version upgrade with breaking changes (Express 4 -> 5, React 17 -> 19, Node 18 -> 22).
- Replacing a build tool (Webpack -> Vite, npm -> pnpm).
- Replacing a library family (Moment -> date-fns, Redux -> Zustand).
- Cross-cutting language version bump (Python 3.10 -> 3.13, TS 4.x -> 5.x with strictness changes).

## When NOT to use

- Patch / minor upgrade with no API change -> `adk-build-deps`
- Single feature add or bug fix -> `adk-build-feature`
- Restructure with no behavior change -> `adk-build-refactor`
- Test-only adjustments to keep up with a migration -> `adk-build-test` (called from this skill)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<from -> to>` | yes | What is being migrated |
| `<scope>` | optional | Path or service to limit |
| `<plan path>` | optional | Existing migration plan to follow |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate `from`, `to`, scope, and rollback strategy. Approval gate unless `--auto`.
2. **Research breaking changes** - pull the official upgrade / migration guide. Capture the breaking-change inventory with citations (delegate to `adk-plan-research` if the surface is large).
3. **Inventory call sites** - grep the repo for usages of every changed API. Group by module / file family.
4. **Plan in groups** - cut migration into groups of files that can change together and be validated together. Order by risk (lowest first).
5. **Pin and prepare** - update the package version (or runtime), add any required compatibility shims, run baseline tests to capture starting state.
6. **Migrate group by group** - apply per-group changes; run validation; commit before moving on.
7. **Remove shims** - once all groups are migrated, remove temporary compat layers.
8. **Final validation (per `build-migrate-validator.md`)** - full test suite, type-check, build, smoke checks for behavior parity.
9. **Report** - what changed, what behavior changed (intentionally), what risk remains, rollback steps.

## Breaking-change inventory template

```markdown
## Breaking changes: <from> -> <to>
- <API or behavior> - <change> - <doc URL> - <our usage count>
- <API or behavior> - <change> - <doc URL> - <our usage count>
```

Every row needs a usage count from the actual repo. Zero usages still warrant a row marked `not used` so reviewers know it was checked.

## Group sizing

- Keep each group to ~5-15 files when possible.
- Each group must compile, type-check, and have its own validation pass.
- Mark groups that touch shared infrastructure as serial (cannot parallelize).
- Prefer to land independent groups in separate commits.

## Rollback story

Every migration plan must have a rollback path:

- How to revert the dependency or runtime version.
- Which compat shims to keep until rollback risk is gone.
- How to detect "we should roll back" in production (signal + threshold).

## Output format

```
## Migration: <from> -> <to>

## Breaking Changes Addressed
- <API> - <change> - <usage count>

## Groups Migrated
1. <group> - files: <count> - validation: <command> PASS
2. <group> - files: <count> - validation: <command> PASS

## Compat Shims
- <shim> - <removal slice>

## Validation
- Tests: <command> - PASS / FAIL
- Type-check: <command> - PASS / FAIL
- Build: <command> - PASS / FAIL

## Behavior Changes (Intentional)
- <bullet>

## Rollback
- <one-line revert path>

## Remaining Risk
- <open item>

Need more detail on any section?
```

## Anti-patterns

- "Big-bang" migration with no intermediate validations.
- Skipping the breaking-change inventory because "we'll find issues by running tests".
- Mixing migration with new feature work in the same change.
- Leaving compat shims in the codebase after the migration is done.
- No rollback plan because "the old version is right there in git".
- Marking the migration done while tests are skipped or excluded.

## Examples

```
adk-build-migrate "Express 4 -> Express 5" --scope src/
```

```
adk-build-migrate "Webpack 5 -> Vite 5" --scope ./
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-migrate-clarifying-questions.md`) and reports the choices.

1. **What is the source and target (framework, version, runtime)?** — _How to pick:_ Be specific: 'React 17 → React 19', 'Node 18 → Node 22', 'Webpack → Vite'. Vague targets cause vague plans.
2. **Is downtime acceptable, or does the system stay live throughout?** — _How to pick:_ Downtime allowed → simpler cutover. Live → compatibility shims + dual-write/dual-read for stateful systems.
3. **Are there codemods or migration tools published by the upstream?** — _How to pick:_ Yes → use them; treat as one step. No → write a migration script committed to the repo.

**Default report:** Step-by-step plan + per-step rollback + current step status + remaining steps + risk notes.

**Detailed report (on request or `--verbose`):** Add: compatibility-shim inventory with removal deadlines, deprecated-API call sites, performance delta per step, traffic-shift plan if applicable.

**Artifact:** `migration-runbook` — Markdown runbook + a series of step-scoped commits in the repo. Runbook sections: Source, Target, Why, Steps (each with commands + rollback + validation), Compatibility Shims, Removal Plan, Risks.

**Artifact path:** .temp/plans/migrate-<slug>.md (runbook), .temp/notes/migrate-<slug>-step-<i>.md (per-step evidence)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-migrate-clarifying-questions.md`) and reports the choices.

1. **What is the source and target (framework, version, runtime)?** — _How to pick:_ Be specific: 'React 17 → React 19', 'Node 18 → Node 22', 'Webpack → Vite'. Vague targets cause vague plans.
2. **Is downtime acceptable, or does the system stay live throughout?** — _How to pick:_ Downtime allowed → simpler cutover. Live → compatibility shims + dual-write/dual-read for stateful systems.
3. **Are there codemods or migration tools published by the upstream?** — _How to pick:_ Yes → use them; treat as one step. No → write a migration script committed to the repo.

## Default vs detailed output

**Default report:** Step-by-step plan + per-step rollback + current step status + remaining steps + risk notes.

**Detailed report (on request or `--verbose`):** Add: compatibility-shim inventory with removal deadlines, deprecated-API call sites, performance delta per step, traffic-shift plan if applicable.

**Artifact:** `migration-runbook` — Markdown runbook + a series of step-scoped commits in the repo. Runbook sections: Source, Target, Why, Steps (each with commands + rollback + validation), Compatibility Shims, Removal Plan, Risks.

**Artifact path:** .temp/plans/migrate-<slug>.md (runbook), .temp/notes/migrate-<slug>-step-<i>.md (per-step evidence)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/build-migrate-anti-patterns.md` | Things to avoid when running this skill. |
| `references/build-migrate-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/build-migrate-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/build-migrate-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/build-migrate-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/build-migrate-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/build-migrate-persona.md` | The agent persona that drives this skill. |
| `references/build-migrate-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/build-migrate-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/build-migrate-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
