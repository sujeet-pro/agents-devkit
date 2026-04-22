# Anti-patterns for `adk-adopt-ai-in-repo`

## Inspection anti-patterns

- Generating files without first running the full `repo-analysis-playbook.md` pass.
- Reading only `package.json` or `README.md` and calling that "deep analysis".
- Inferring stack from filenames alone instead of reading the actual code.
- Treating CI scripts as the source of canonical commands without checking the local manifest scripts (CI commands are often slow / Docker-wrapped).
- Reading every file. Sample intelligently per the playbook.

## Stack-detection anti-patterns

- Calling a Next.js app a "React app" (lose the Next-specific guidance).
- Calling a Vite + React app a "Webpack app" (different toolchain, different pre-delivery checks).
- Missing the package manager — picking `npm` when the repo uses `pnpm` and the lockfile proves it.
- Ignoring monorepo signals (`pnpm-workspace.yaml`, `turbo.json`, `nx.json`); generating a single-package guideline tree where multi-package would be correct.

## Research anti-patterns

- Researching every dependency. Research only the dominant detected stacks (per `adopt-ai-research-protocol.md`).
- Citing tutorials as "official docs". Always prefer the framework's own docs.
- Letting old web sources (>6 months for fast-moving libraries) influence the guidance without verification.

## Generation anti-patterns

- Inventing commands. Every command in `scripts-and-commands.md` MUST be real and runnable.
- Generating shell helpers. The constraint is Python — cross-platform and testable.
- Duplicating long instructions in both `AGENTS.md` AND `CLAUDE.md`. `CLAUDE.md` is a thin Claude-specific delta only.
- Putting full instructions inside skill wrappers. Wrappers point at `ai-guidelines/`; that's the contract.
- Generating skills that don't point into `ai-guidelines/` at all.
- Hard-coding paths that only work on macOS / one IDE / one shell.

## Merge anti-patterns

- Overwriting an existing user-authored `AGENTS.md` / `CLAUDE.md` without a merge.
- Replacing `.cursor/rules/*` files the user wrote.
- Deleting `ai-guidelines/` content the user added between runs.
- Ignoring `<!-- adk:adopt:start -->` / `<!-- adk:adopt:end -->` markers; they exist precisely so a refresh can find managed sections.
- Refresh runs that churn unchanged files (breaks the no-op-diff guarantee).

## Hook-wiring anti-patterns

- Wiring slow commands as pre-commit hooks (e2e, full test suite, full build). Pre-commit is for fast checks.
- Wiring commands that require environment setup (Docker, services running) as pre-commit. They will block the user.
- Wiring hooks the repo doesn't actually have a fast version of — invent the missing fast command first or skip the hook.
- Replacing existing husky / lefthook / pre-commit setup without checking with the user.

## Workflow anti-patterns

- Acting outside this skill's scope; route to:
  - `adk-build-feature` for implementing features in the bootstrapped repo (after this skill).
  - `adk-docs-write` for editing one of the generated `ai-guidelines/` files.
  - `adk-audit-repo` for auditing the existing scaffolding.
  - `adk-publish-commit` for crafting a commit message after the user has reviewed the generated tree.
- Routing to two skills at once instead of chaining.
- Skipping the validator phases.
- Auto-committing the generated tree without explicit user approval.
