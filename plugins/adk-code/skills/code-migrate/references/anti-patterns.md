# `code-migrate` — anti-patterns

## Reading shortcuts

- **Applying changes from a half-remembered migration guide.** Re-read every time. Versions diverge; the guide is the source of truth.
- **Reading the CHANGELOG instead of the migration guide.** CHANGELOGs summarize what changed; migration guides instruct on how to handle it. Read both, but the guide is authoritative.
- **Reading a blog post instead of the official guide.** Blog posts are often opinionated, partial, or out of date. Use them for context, not as the source.
- **Skipping the migration guide because "I've migrated X before".** The guide changes between versions. Even a 18 → 19 you did last year is different from 19 → 20.

## Bundling

- **Bundling 3 migrations in one PR** (React 18→19 + Webpack→Vite + Node 18→20). Each migration deserves its own task — independently revertible, independently reviewable.
- **Bundling required + optional changes in one diff.** Required = must apply for the new version to work. Optional = recommended for new behavior. Conflating them makes review harder ("is this needed for the upgrade or is this a style preference?").
- **Bundling the migration with feature work.** "While we're upgrading React, let me also rewrite the auth flow to use the new `use()` hook." That's a feature task; do it AFTER the migration lands.
- **Bundling the migration with refactors.** Same.

## Validation theatre

- **Skipping per-group validation; only running tests at the end.** A group failure is hard to localize when 5 groups have been applied. Validate after each.
- **Skipping the build step at the end.** Migrations affect the build (new bundler, new compiler, new runtime). The build is the most-valuable signal.
- **Skipping the smoke check for runtime changes.** A Node version bump that "passes all tests" can still fail at startup because of an ESM/CJS interop change.
- **Reporting "tests pass" without showing the count.** Always count + scope.

## Optional-change creep

- **Applying recommended-but-optional changes** without flagging them in the plan. The reviewer can't distinguish "needed for upgrade" from "we like the new style".
- **Adopting the new APIs throughout the codebase** when only the breaking-change items are required. That's a follow-up task.
- **"It's idiomatic now to use X."** That's `code-refactor` after the migration. Don't smuggle it in.

## Versioning shortcuts

- **"Migrate React → latest" without resolving "latest".** Resolve before running. The operator should know which version they're going to.
- **Skipping intermediate versions.** Migrating React 16 → 19 in one task is risky (and against the guide's recommendation, which usually says "migrate one major at a time"). Suggest 16→17, 17→18, 18→19 as separate tasks.
- **Migrating to an `alpha` / `beta` / `rc` release** without explicit operator opt-in. Production code lives on stable releases; surface the version status.

## Cascading scope changes

- **The migration cascades into a public API change of THIS repo.** That's not a `code-migrate` problem; it's a `code-api` problem. Stop, surface, recategorize.
- **The migration requires touching CI workflows, Dockerfiles, deployment configs.** Often required, but list each as its own item — they're not always in the migration guide and may have repo-specific implications.

## Inventory shortcuts

- **Skipping the inventory because "we'll see what breaks".** A migration without an inventory is a guess. The inventory is the source of truth for "what does this mean for our codebase?".
- **Inventorying with `grep -F <pattern>` and missing variant patterns.** Patterns may have variations (whitespace, line breaks, parametric names). Use AST-aware grep when available (e.g. `ts-morph`, `ast-grep`).

## Reporting

- **Hiding the items the migration guide flagged but we did not apply.** Always list, with reason. Reviewers want to know what was deliberately deferred.
- **Saying "migrated" without listing the rule-by-rule application.** The migration guide rules are the work-breakdown structure; the report should mirror them.
- **Burying the version diff.** Lead with "from X to Y" + the dependency-version diff (`package.json` / `build.gradle` before/after).
- **Overstating completeness.** "Migration done" when 4 of 12 guide rules were applied (the rest deferred) — say "partial migration: 4 of 12 rules applied; remaining 8 deferred for follow-up".

## Tooling assumptions

- **Assuming the new tool's CLI is a drop-in replacement** without reading the migration. Vitest is mostly Jest-compatible but has notable differences (mock semantics, `expect` differences, timers). Read.
- **Running tests on the OLD tool after migrating to the NEW tool** because the test runner is still pointing at Jest. Read the test config; verify the runner switched.
- **Skipping the `package.json` script change.** `npm test` should now run Vitest, not Jest; without updating the script, the migration is half-done.

## "Latest" is not a version

- **`"react": "latest"` in `package.json`.** Lock the version explicitly. Floating versions are a separate problem to solve in dependency hygiene; the migration task pins.
- **Updating the dependency BEFORE doing the source-code migration** in projects where the old code doesn't compile against the new dependency. The order is documented in the guide; follow it.
