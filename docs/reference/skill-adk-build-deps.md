---
title: 'adk-build-deps'
description: 'Inventory, upgrade, deduplicate, audit, or remove dependencies in the repo with explicit risk per change and per-package validation. Use when the deliverable is a dependency hygiene change - patch / minor upgrades, lockfile cleanups, security advisories, unused-dep removal. Do not use for major-version migrations with API changes (use adk-build-migrate).'
skill_name: adk-build-deps
category: task
---
# ADK Build / Deps

Standalone task skill under the `adk-build` category router. Produces a focused dependency change with explicit per-package risk, lockfile correctness, and validated outcomes.

## When to use

- Patch or minor upgrade of one or more packages.
- Resolve a security advisory (`npm audit`, `pip-audit`, `cargo audit`).
- Remove unused dependencies after a refactor.
- Deduplicate the lockfile after an upgrade.
- Pin or unpin a transitive dep that is causing churn.

## When NOT to use

- Major-version upgrade with breaking API -> `adk-build-migrate`
- Adding a new dep as part of a feature -> `adk-build-feature` (and call this skill if the dep choice itself is non-trivial)
- Audit of dependency health (no changes) -> `adk-audit-repo`
- Switching package managers (`npm` -> `pnpm`) -> `adk-build-migrate`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `upgrade` / `audit-fix` / `remove-unused` / `dedupe` / `pin` |
| `<packages>` | optional | Specific packages; default is "all eligible per action" |
| `<scope>` | optional | Path or workspace |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate action, packages, scope, and acceptable risk (`patch-only` / `minor-ok` / `with-deprecations`). Approval gate unless `--auto`.
2. **Inventory** - read `package.json` / `requirements.txt` / `pyproject.toml` / `Cargo.toml` and the lockfile. Identify the package manager.
3. **Plan changes per package** - for each package: current version, target version, range of changelog entries to read, risk classification (`safe` / `attention` / `breaking`).
4. **Read changelogs / advisories** - for each non-`safe` change, pull the changelog or advisory entries and capture the relevant lines.
5. **Apply** - run the upgrade / removal / dedupe in the package manager's idiomatic way. Update only the lockfile changes you intended.
6. **Validate** - install fresh; run tests, lint, type-check, and a build. For security fixes, re-run the audit tool to confirm the advisory is resolved.
7. **Report** - per-package changes, advisories resolved, validation evidence, follow-up risks.

## Risk classification

| Class | Trigger | Required action |
| --- | --- | --- |
| `safe` | Patch upgrade, no changelog highlights | Just upgrade and validate |
| `attention` | Minor upgrade, deprecation notes, behavior nuance | Read changelog; note any caller code that should change |
| `breaking` | Major upgrade or "breaking" entry in changelog | Stop - escalate to `adk-build-migrate` |

This skill never knowingly applies a `breaking` change. If one is detected, surface it and recommend the migration skill.

## Action playbooks

### upgrade

- `npm`: `npm outdated` -> select; `npm install pkg@version` per chosen package; `npm dedupe`.
- `pnpm`: `pnpm outdated` -> `pnpm update <pkg>`; `pnpm dedupe`.
- `pip`: `pip list --outdated`; bump in `pyproject.toml`; `pip install -U <pkg>`; regenerate lock.
- `cargo`: `cargo outdated`; `cargo update -p <pkg>`.

### audit-fix

- `npm audit fix` (no `--force` without explicit user approval).
- `pnpm audit --fix`.
- `pip-audit -r requirements.txt --fix`.
- `cargo audit` (no auto-fix; produce upgrade plan).

### remove-unused

- Use `depcheck` (Node) / `pip-check-reqs` / `cargo-udeps` to find unused deps.
- Cross-check by grepping for the import. Static tools have false positives.
- Remove from manifest; reinstall to update lockfile; validate.

### dedupe

- `npm dedupe` / `pnpm dedupe`.
- Verify the lockfile diff - dedupe should not change resolved versions of direct deps.

### pin

- Switch a `^` / `~` range to an exact version (or vice versa).
- Document why in the commit message (e.g. "pin lib X to 4.7.2 - 4.8.0 broke Node 18 builds").

## Output format

```
## Deps action: <action>

## Per-Package Changes
- `pkg-a` 1.2.0 -> 1.2.3 [safe]
- `pkg-b` 4.7.0 -> 4.8.0 [attention - changelog: <highlights>]

## Advisories Resolved
- <CVE / GHSA id> - <package> - now <safe>

## Lockfile
- <N> entries changed
- Dedupe: <Y|N>

## Validation
- Install: <command> - PASS
- Tests: <command> - PASS / FAIL
- Lint: <command> - PASS / FAIL
- Type-check: <command> - PASS / FAIL
- Build: <command> - PASS / FAIL

## Follow-up Risks
- <bullet>

Need more detail on any package?
```

## Anti-patterns

- Running `npm audit fix --force` without explicit user approval.
- Bundling unrelated upgrades in one change. Group by risk class.
- Touching the lockfile by hand outside the package manager.
- Skipping changelog reads on `attention` changes.
- Marking a security fix done without re-running the audit tool.

## Examples

```
adk-build-deps upgrade --packages react,react-dom --scope ./
```

```
adk-build-deps audit-fix --scope packages/api
```

```
adk-build-deps remove-unused --scope ./
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-deps-clarifying-questions.md`) and reports the choices.

1. **Mode: inventory, upgrade, audit, dedupe, or remove-unused?** — _How to pick:_ Inventory = list-only, no changes. Upgrade = bump versions. Audit = flag security/license/staleness. Dedupe = collapse multiple installs of the same package. Remove-unused = prune deps with zero call sites.
2. **Upgrade scope: patch only, minor, major (breaking)?** — _How to pick:_ Patch = always safe to auto-apply with tests. Minor = safe with tests + changelog scan. Major = read every changelog, expect breakage, plan migration.
3. **Are there pinned-version constraints (peer deps, runtime, monorepo)?** — _How to pick:_ List them up front. The plan must respect every constraint or explicitly justify breaking one.

**Default report:** Dependency table (name / current / target / reason / risk) + recommended action per row + advisories list.

**Detailed report (on request or `--verbose`):** Add: per-dep changelog summary for upgrades, transitive-dep diff, license report, supply-chain risk per package, removal blast radius for prune.

**Artifact:** `dependency-report-or-diff` — Markdown report (audit/inventory mode) OR lockfile diff + changed files (upgrade/dedupe/remove mode).

**Artifact path:** .temp/reports/deps-<slug>.md (report), repo lockfile + manifests for actual changes.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/build-deps-clarifying-questions.md`) and reports the choices.

1. **Mode: inventory, upgrade, audit, dedupe, or remove-unused?** — _How to pick:_ Inventory = list-only, no changes. Upgrade = bump versions. Audit = flag security/license/staleness. Dedupe = collapse multiple installs of the same package. Remove-unused = prune deps with zero call sites.
2. **Upgrade scope: patch only, minor, major (breaking)?** — _How to pick:_ Patch = always safe to auto-apply with tests. Minor = safe with tests + changelog scan. Major = read every changelog, expect breakage, plan migration.
3. **Are there pinned-version constraints (peer deps, runtime, monorepo)?** — _How to pick:_ List them up front. The plan must respect every constraint or explicitly justify breaking one.

## Default vs detailed output

**Default report:** Dependency table (name / current / target / reason / risk) + recommended action per row + advisories list.

**Detailed report (on request or `--verbose`):** Add: per-dep changelog summary for upgrades, transitive-dep diff, license report, supply-chain risk per package, removal blast radius for prune.

**Artifact:** `dependency-report-or-diff` — Markdown report (audit/inventory mode) OR lockfile diff + changed files (upgrade/dedupe/remove mode).

**Artifact path:** .temp/reports/deps-<slug>.md (report), repo lockfile + manifests for actual changes.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/build-deps-anti-patterns.md` | Things to avoid when running this skill. |
| `references/build-deps-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/build-deps-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/build-deps-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/build-deps-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/build-deps-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/build-deps-persona.md` | The agent persona that drives this skill. |
| `references/build-deps-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/build-deps-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
