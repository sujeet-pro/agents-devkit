# Examples for `adk-adopt-ai-in-repo`

Concrete inputs the skill expects and the shape of what comes back.

## Trigger phrases

- "Onboard AI to this repo"
- "Bootstrap `ai-guidelines/` and skill wrappers in `<path>`"
- "Refresh the AI scaffolding after the v3 migration"
- "Add Cursor + Claude support to this repo"
- "Run `adk-adopt-ai-in-repo` here"

## Sample invocations

```
adk-adopt-ai-in-repo .
```

First-time bootstrap of the current repo, all stacks, hooks enabled, default-ask flow.

```
adk-adopt-ai-in-repo /path/to/myrepo --refresh --auto
```

Refresh existing scaffolding, no questions asked, picks documented defaults.

```
adk-adopt-ai-in-repo . --scope frontend --no-hooks
```

Generate scaffolding for the frontend slice only; do not write hook configs.

```
adk-adopt-ai-in-repo . --refresh --merge report-conflicts-only
```

Plan-only refresh: produce a merge plan but write nothing. Useful when many files exist and you want to inspect the plan first.

## Sample output (fresh-bootstrap, default-ask, abbreviated)

```
ADOPT-AI-BOOTSTRAPPED 24 files

## Adopt AI: /Users/me/projects/myrepo
- Mode: fresh-bootstrap
- Scope: all
- Hooks: wired
- Commit policy: leave-unstaged

## Detected stack
- Repo type: monorepo (pnpm workspace; 1 Next.js app + 2 Node services)
- Languages: TypeScript (95%), Python (5% — scripts/)
- Frameworks: Next.js 14 (apps/web), Express 4 (services/api), Express 4 (services/worker)
- Package manager: pnpm@9.4.0 (from packageManager field in package.json)
- Lint / format: oxlint + prettier (.oxlintrc.json + .prettierrc)
- Typecheck: tsc --noEmit (root tsconfig + per-package)
- Tests: vitest (unit), playwright (e2e in apps/web/e2e/)
- Build: turbo build (turbo.json)
- CI: GitHub Actions (.github/workflows/ci.yml — runs lint, typecheck, test, build)
- Commit convention: conventional commits (95% of last 50 commits)
- PR convention: .github/PULL_REQUEST_TEMPLATE.md present

## Generated file tree
- ai-guidelines/                                          NEW
  - README.md                                             NEW
  - agent-behavior.md                                     NEW
  - repo-summary.md                                       NEW
  - project-structure.md                                  NEW
  - architecture.md                                       NEW
  - data-flow.md                                          NEW
  - tooling-and-dependencies.md                           NEW
  - scripts-and-commands.md                               NEW
  - coding-guidelines.md                                  NEW
  - testing-guidelines.md                                 NEW
  - documentation-guidelines.md                           NEW
  - workflows/                                            NEW
    - development.md                                      NEW
    - refactor.md                                         NEW
    - migrate.md                                          NEW
    - commit-and-pr.md                                    NEW
    - review-local-changes.md                             NEW
    - docs-generation.md                                  NEW
    - agentic-team.md                                     NEW
    - refresh-guidelines.md                               NEW
  - scripts/                                              NEW
    - refresh_ai_guidelines.py                            NEW
    - run_project_checks.py                               NEW
- AGENTS.md                                               NEW
- CLAUDE.md                                               NEW
- .claude/skills/development/SKILL.md                     NEW
- .claude/skills/refactor/SKILL.md                        NEW
- .claude/skills/migrate/SKILL.md                         NEW
- .claude/skills/commit/SKILL.md                          NEW
- .claude/skills/add-pr-description/SKILL.md              NEW
- .claude/skills/review-local-changes/SKILL.md            NEW
- .claude/skills/docs-generation/SKILL.md                 NEW
- .cursor/skills/development/SKILL.md                     NEW
- .cursor/skills/refactor/SKILL.md                        NEW
- (... Cursor skill wrappers omitted ...)
- .cursor/rules/project-ai-guidelines.mdc                 NEW
- .cursor/hooks.json                                      NEW
- .claude/settings.json                                   NEW

## Skill catalog
- 7 skill wrappers per agent surface (.claude + .cursor)

## Hook coverage
- pre-commit: pnpm lint + pnpm format:check  → ai-guidelines/scripts/run_project_checks.py format-and-lint
- pre-push: pnpm typecheck + pnpm test       → ai-guidelines/scripts/run_project_checks.py typecheck-and-test
- refresh-after-stack-change: package.json, pnpm-lock.yaml, turbo.json  → suggests adk-adopt-ai-in-repo --refresh

## Validation
- Phase 1 (pre-execution): OK (git repo, write permission, clean tree)
- Phase 2 (mid-flow): OK (inspection complete, plan approved)
- Phase 3 (pre-handoff): OK (every link resolves, every command runs, hook configs parse)
- Phase 4 (post-execution): OK (24/24 files written, evidence summary captured)
- Validator log: .temp/notes/adopt-ai-myrepo-validator.md

## Manual follow-up
- Review and `git add` the generated tree (left unstaged per default policy).
- The e2e command (`pnpm --filter web e2e`) requires Playwright browsers — run `pnpm --filter web exec playwright install` once before relying on the hook.
- `services/worker/` has no test command — added a TODO in `scripts-and-commands.md`; consider adding vitest there.

Need more detail on any section? Pass --verbose or ask explicitly.
```

## Sample output (`--refresh`, abbreviated)

```
ADOPT-AI-REFRESHED 4 files (12 unchanged)

## Adopt AI: /Users/me/projects/myrepo
- Mode: refresh
- Scope: all
- Hooks: wired (settings unchanged)
- Merge aggressiveness: preserve-and-merge

## Diff summary
- ai-guidelines/scripts-and-commands.md     UPDATED (commands re-derived after package.json change)
- ai-guidelines/tooling-and-dependencies.md UPDATED (Vite version bump captured)
- AGENTS.md                                  UPDATED (managed section only; user-authored sections preserved)
- .cursor/hooks.json                         UPDATED (pnpm 9.5 → 10.0 path)
- (12 other files: SKIPPED-NO-CHANGE)

## Manual follow-up
- Review the AGENTS.md merge diff at .temp/notes/adopt-ai-myrepo-merge-diff.md before committing.
```
