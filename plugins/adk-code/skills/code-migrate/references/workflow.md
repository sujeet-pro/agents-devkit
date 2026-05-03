# `code-migrate` — workflow detail

## Phase 0 — prompt expand

1. **Restate**: "Migrate `<repo>` from `<X>` to `<Y>`." One sentence.
2. **Resolve repo** via `cwd → .git → repos.md`.
3. **Confirm versions**: parse `<from>` and `<to>` precisely. "React 18 → 19" is unambiguous; "React → latest" is not — ask under `-i`; under `--auto`, resolve "latest" via WebFetch + record the resolved version in Decisions.
4. **Pick task slug**: usually `migrate-<tool>-<from>-to-<to>` (e.g. `migrate-react-18-19`, `migrate-jest-to-vitest`, `migrate-spring-boot-2-3`).
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt`.
6. **Approval gate** unless `--auto`.

## Phase 1 — preflight

1. `git status` — clean. Dirty → ask.
2. Branch — if on protected, prompt `migrate/<slug>`.
3. Resolve commands: typecheck + lint + tests + **build** (build matters for migrations).
4. **Baseline check**: typecheck + lint + tests + build all green. If red, STOP — migrating on a red baseline is unverifiable.
5. Snapshot the current dependency versions (from `package.json` / `pyproject.toml` / `build.gradle` / `Cargo.toml`) so the report can show the before/after.

## Phase 2 — read the upstream migration guide

1. **Identify the canonical guide**:
    - React: `https://react.dev/blog/...` + the upgrade guide for the specific version.
    - Vue: `https://vuejs.org/guide/migration/`.
    - Spring Boot: the GitHub wiki release notes for the target version.
    - Node: the release notes + the deprecation list.
    - Vitest from Jest: `https://vitest.dev/guide/migration.html`.
    - For tool replacements: the destination tool's "Migrating from X" page.
2. **WebFetch** the guide. Save the relevant breaking-change list.
3. **Curate** the guide into `.temp/task-<slug>/migration-notes.md`:
    - One section per breaking-change item.
    - Quote the rule (≤15 words) verbatim.
    - URL of the source.
    - One-line "what does this mean for our codebase?" — applies to us / partially / not at all.
4. **Approval gate** under `-i` before moving to inventory.

## Phase 3 — inventory

For each breaking-change item that "applies to us":

1. **Grep** for the affected pattern (function name, prop name, decorator, import path, config key).
2. **Record**:
    - Pattern (e.g. `useEffect(.., undefined)` for "useEffect cleanup-fn signature").
    - Match count.
    - File list.
    - 2-3 representative call-sites for the implementer to anchor on.
3. **Save** to `.temp/task-<slug>/migration-inventory.md`.

If a pattern's count is 0, mark it "no impact" — but include in the inventory so the report shows that you checked.

## Phase 4 — plan groups

1. **Group breaking-change items** by category. Examples:
    - All `useEffect` cleanup-fn signature changes → Group A.
    - All `withRouter` removals → Group B.
    - All `componentWillReceiveProps` → `getDerivedStateFromProps` migrations → Group C.
    - The `package.json` peerDependency bump → Group Z (last).
2. **Sequence**: low-blast-radius first; high-blast-radius last. Bump the dependency version *last* (after all source code is migrated) so each intermediate group's tests run on the OLD version + new patterns where backwards-compat allows. (Some migrations require the version bump first — read the guide; the right order is documented.)
3. **Write** `.temp/task-<slug>/plan.md`:
    - `## Migration` — from / to.
    - `## Groups` — table: group name, count of files, count of changes, validation strategy, sequence number.
    - `## Validation plan` — per-group commands + final commands.
    - `## Items NOT applied` — table: rule, reason, follow-up.
    - `## Out of scope (deliberate)` — bullet list.
4. **Approval gate** unless `--auto`. (This gate is high-value; the operator may reorder groups based on knowledge the skill doesn't have.)

## Phase 5 — execute group-by-group

For each group, in sequence:

1. **Apply the group's changes** via the implementer subagent. The implementer reads its own protocol (read-before-write, etc.) plus the migration-notes for the rule it's applying.
2. **Per-group validation**:
    - typecheck (fast, valuable signal)
    - relevant tests (scoped to the changed files where possible)
3. **If green**: log to `validation/per-skill/code-migrate.md` under that group's section. Continue.
4. **If red**: stop the chain. Surface the failure. Options:
    - Smallest possible follow-up edit to recover.
    - Revert the group; re-think.
    - Skip this group (rare — only with operator approval; document in NOT-applied).

## Phase 6 — final validation

1. **Full build** — `npm run build` / `./gradlew build` / `cargo build --release` / `mvn package` / etc. Migrations affect the build; this is required, not optional.
2. **Full test suite** — full repo (or full affected packages in a monorepo).
3. **Typecheck** — full.
4. **Lint** — full.
5. **Smoke check** (if applicable):
    - For Node version bumps: run a representative entry point (CLI invocation, server startup).
    - For framework migrations: build the app + start the dev server; confirm it starts cleanly.
    - For test-framework migrations: confirm a known passing test still passes under the new framework.
6. Capture all of the above to `.temp/task-<slug>/validation/per-skill/code-migrate.md`.

## Phase 7 — report

Write `.temp/task-<slug>/report.md`:

- **Migration** — from / to.
- **Files changed** — table summarizing.
- **Groups applied** — table: name, count, validation status.
- **Migration guide rules applied** — table: rule (quoted ≤15 words), file count.
- **Migration guide rules NOT applied** — table: rule, reason, follow-up.
- **Validation evidence** — final commands + exit codes.
- **Decisions** — every auto-pick.
- **Residual risk / follow-ups** — bullet list.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question.

## Loop control

- After 1 group failure, STOP and surface. Don't continue migrating; the failure may compound.
- If the migration guide is paywalled or unavailable, surface to the operator. The skill REQUIRES an authoritative source.
- If the migration involves user-facing behavior changes (e.g. a runtime semantic change), surface in the plan so the operator can prepare a migration PR description.
- If the migration changes a public API surface of THIS repo (e.g. the migration cascades into a library you publish), STOP — the cascade is a separate `code-api` task.

## When the migration is incomplete

A migration is rarely 100% done in one task. The migration guide may have:

- Items the codebase doesn't use (no impact).
- Items that are recommended but not required for this version (often skipped).
- Items that require a bigger redesign (deferred to a future task).

The report should be explicit about each:

- Required items: count of applied vs not applied.
- Optional items: applied / skipped (with reason).
- Recommended items deferred: list with follow-up suggestions.
