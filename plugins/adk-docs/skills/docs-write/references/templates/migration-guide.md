# Migration: <From> → <To>

> One-sentence summary of what's being replaced and why now. Cite the
> ADR or incident that triggered the migration.

- **From version / system:** exact identifier (e.g. `react@18.2`,
  `spring-boot@2.7`, `static-symmetric-auth@v1`).
- **To version / system:** exact identifier.
- **Effective date:** YYYY-MM-DD.
- **Owner:** team / handle.

## Why

3-5 sentences. What breaks in the old version? What's the new version
good at? Link to the upstream release notes / ADR / incident that
forced the move.

## Breaking changes

Table of every breaking change with the impact and the fix.

| Change | Impact | Fix |
| --- | --- | --- |
| `createFoo(arg)` renamed to `Foo.create(arg)` | compile error | search-replace across repo |
| default timeout changed 30s → 10s | silent failures on slow endpoints | set explicit `timeout = 30_000` |

Every row cites the upstream changelog / commit where possible.

## Before you start

Bullet checklist:

- [ ] All tests green on current version.
- [ ] No in-flight PRs that touch the migrating code.
- [ ] Feature-flag strategy decided (dual-stack vs big-bang).
- [ ] Rollback plan reviewed.

## Step-by-step

Numbered, imperative, one change per step. Each step independently
testable.

1. **Upgrade the dependency.** Exact command:
   `pnpm up react@19.0.0 react-dom@19.0.0` (copy from the repo's
   actual package-manager).
2. **Run the codemod.** Exact command from the upstream docs. Commit
   the mechanical changes as a separate commit.
3. **Fix the hand-migrations.** List the file patterns to review:
   `grep -rn "<old-api>" src/`. Replace per the breaking-change table.
4. **Run tests.** Exact command (`pnpm test`, `./gradlew test`).
5. **Run the lint + type-check.** Exact commands. Fix any new
   warnings.

## Rollback plan

Exact steps to return to the old version in < 10 minutes. Include
the git operations (reset / revert), the package-manager command, and
any feature-flag flips.

## Verification

How do you know the migration succeeded?

- [ ] All tests green.
- [ ] CI green on the PR.
- [ ] Smoke test against staging (command + expected output).
- [ ] No new errors in DD for 24h post-deploy.

## FAQ

Anticipated questions from the team. Answer each in 2-4 sentences.

### Can I migrate in parts?

Yes / no + the reason.

### What if I hit `<common error>`?

The cause + the fix.

## References

- Upstream release notes / migration guide (link; quote ≤15 words).
- The ADR that approved this migration.
- Related PRs / commits doing the actual migration work.
