# Repo Analysis Playbook

Defines how to inspect a repo deeply enough to generate useful `ai-guidelines/` docs and per-agent AI scaffolding. The analysis must be evidence-driven: inspect the actual repo BEFORE deciding what to generate.

The playbook output is a single evidence summary written to `.temp/notes/adopt-ai-<repo-slug>-evidence.md`. The validator's Phase 2 `repo-inspected` gate blocks until that file exists with all sections populated.

## 1. Preflight

Start by checking:

- repo root and VCS state (`git rev-parse --show-toplevel`, `git status --porcelain`)
- existing `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, `.cursorrules`, `.cursor/rules/`, `ai-guidelines/`
- repo size and shape: single package, multi-package, monorepo, service repo, library, infra, docs, data
- whether existing AI files are clearly managed (have `<!-- adk:adopt:start -->` markers), custom (no markers), or mixed

If the repo already has heavy AI customization, plan a merge instead of a replace.

## 2. Inventory key signals

Inspect manifests, lockfiles, task runners, build files, and tooling configs.

### JavaScript / TypeScript

Read when present:

- `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`
- `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`
- `tsconfig.json`, `vite.config.*`, `next.config.*`, `vitest.config.*`, `jest.config.*`, `playwright.config.*`, `cypress.config.*`
- `.eslintrc*`, `eslint.config.*`, `.oxlintrc*`, `.prettierrc*`, `biome.json`

Infer: framework (React, Next.js, Vue, Nuxt, Angular, Svelte, Remix, Express, NestJS, Fastify, etc.), package manager, monorepo tooling, build scripts, test runners, lint and format tools, typecheck commands.

### Python

Read when present:

- `pyproject.toml`, `poetry.lock`, `requirements*.txt`, `Pipfile`, `tox.ini`, `pytest.ini`, `conftest.py`
- `.ruff.toml`, `ruff.toml`, `.flake8`, `mypy.ini`, `manage.py`

Infer: package manager (pip, Poetry, PDM, Pipenv, uv), framework (Django, Flask, FastAPI, Typer, Celery, Airflow), formatting / linting (Ruff, Black, Flake8, isort), tests (pytest, unittest, nose).

### Go

Read when present: `go.mod`, `go.sum`, `Makefile`, `.golangci.yml`, `.air.toml`.

Infer: module boundaries, build and test commands, linting, code generation, service entrypoints under `cmd/`.

### Rust

Read when present: `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `clippy.toml`.

Infer: workspace vs single crate, binary vs library crates, lint and format expectations from `cargo clippy` and `cargo fmt`, test shape from `cargo test`.

### JVM / Ruby / PHP / .NET / Infra

Read the platform-native files when present:

- `pom.xml`, `build.gradle*`, `settings.gradle*`
- `Gemfile`, `.rubocop.yml`
- `composer.json`
- `*.csproj`, `Directory.Build.props`
- `Dockerfile`, `docker-compose.yml`, `compose.yml`
- `terraform`, `helm`, `kustomize`, `ansible`, or deployment configs

Do not limit the analysis to one language. Many repos are mixed.

## 3. Detect repo type

Use the evidence to classify the repo:

- frontend application
- backend service or API
- full-stack application
- reusable library or SDK
- monorepo with multiple apps or packages
- infrastructure or platform repo
- docs repo
- data or ML repo

If multiple labels apply, say so. For example: "pnpm monorepo with a Next.js frontend and a Node service" or "Python service repo with FastAPI, Celery workers, and Terraform deployment".

## 4. Map top-level structure

Document the high-value directories and what they contain. Look for: `apps/`, `packages/`, `services/`, `libs/`, `src/`, `server/`, `client/`, `api/`, `web/`, `mobile/`, `tests/`, `__tests__/`, `spec/`, `e2e/`, `docs/`, `adr/`, `design/`, infra directories such as `terraform/`, `deploy/`, `charts/`.

Do not create a giant directory dump. Focus on directories that help an agent know where to work.

## 5. Extract real commands

The generated docs and hooks MUST use only real commands. Collect commands from:

- manifest scripts (`package.json` scripts, `pyproject.toml` `[tool.poetry.scripts]`, etc.)
- task runners like `make`, `just`, `turbo`, `nx`, `mage`, `invoke`
- CI configs (often slow / Docker-wrapped — prefer the local equivalent)
- project docs when they name the canonical commands

Capture at least: dev / local run, build, format, lint, typecheck, unit test, integration test, end-to-end test.

Also capture collaboration commands or conventions when present:

- commit message format
- branch naming rules
- PR description template or expected sections
- local review or pre-merge validation flow

For each command, note: exact command, where it came from, whether it is fast / medium / expensive, whether it is repo-wide or package-specific.

If there are multiple valid commands: prefer the canonical repo wrapper, prefer the fastest relevant one for hooks, document alternatives in `ai-guidelines/scripts-and-commands.md`.

## 6. Inspect collaboration conventions

The generated `commit`, `add-pr-description`, and `review-local-changes` skills need evidence too. Inspect when present:

- recent `git log --oneline -50` for message style
- pull request templates (`.github/PULL_REQUEST_TEMPLATE.md`, `.gitlab/...`, `bitbucket/...`)
- `CONTRIBUTING.md`
- release / changelog docs
- `CODEOWNERS` or review instructions
- CI steps that act as merge gates

Infer:

- whether the repo prefers conventional commits, plain commits, or another style
- what a good PR summary should contain
- which validation steps should be referenced by commit / PR-related skills
- how local review is expected to work before opening a PR

## 7. Read representative code

Configs alone are not enough. Read source files that reveal actual conventions. Choose representative files from: app entrypoints, routing or controller layers, service or domain layers, models and schemas, state management or data fetching layers, shared utilities, tests, major package boundaries.

For large repos, sample intelligently. Do not read every file. Aim for ~5-15 representative files per detected stack, biased toward entrypoints and the most-referenced shared utilities.

## 8. Infer coding conventions

Look for patterns the repo actually uses:

- naming conventions (variable / function / file / type)
- file naming and directory layout
- import style and path aliases
- module boundaries
- state management patterns
- error handling
- logging
- validation
- dependency injection or factory patterns
- async patterns
- test organization
- typing discipline (strict / lenient; `any` usage)
- API client or server abstractions

Turn repeated patterns into guidance ONLY when they are clearly intentional or dominant. If the repo is inconsistent: document the dominant pattern, call out important inconsistencies, avoid overstating style rules that are not stable yet.

## 9. Infer testing conventions

From code and config, determine:

- test frameworks in use
- where tests live (collocated vs `tests/` vs `__tests__/`)
- naming patterns
- common fixtures, builders, mocks, helpers
- unit vs integration vs e2e split
- whether coverage tooling exists
- when snapshot, visual, or contract tests are used

Generated `testing-guidelines.md` should reflect current practice first, then add compatible best practices from research.

## 10. Infer architecture and data flow

Map the system in a way an implementation or debugging agent can use.

For frontend-heavy repos, trace flows such as: user action → local or server state update → API request → server handler → domain logic → persistence → response rendering.

For backend-heavy repos: request entrypoint → middleware/auth → controller/route → service/domain → repository/external integrations → persistence → response.

For async systems: event producers → queues/streams → workers → retries / error handling → downstream consumers.

If exact details are uncertain, label them as inferred instead of presenting them as facts.

## 11. Analyze existing docs

Read current repo docs when present: `README.md`, `CONTRIBUTING.md`, `docs/`, ADRs, onboarding docs, architecture notes.

Use them to: validate the detected stack, find official project terminology, find commands or workflows, spot gaps the generated `ai-guidelines/` should fill.

## 12. Run targeted web research

After the repo scan, research only what is relevant to the detected stack and tools (per `adopt-ai-research-protocol.md`). Examples: "Next.js 14 app router data fetching official docs", "FastAPI testing best practices official docs", "Vitest mock patterns official docs", "Ruff recommended config".

Do NOT research every technology in the repo equally. Prioritize the ones that shape day-to-day development and validation.

## 13. Produce the evidence summary

Before generating files, build the evidence summary file at `.temp/notes/adopt-ai-<repo-slug>-evidence.md`. It MUST include:

- repo type
- languages and frameworks
- package manager / build system
- commands selected for hooks and validation (with provenance per command)
- commit / PR conventions that should drive generated repo-local skills
- key directories and package boundaries
- major data flows
- coding and testing patterns
- external sources that influenced the guidance (per `adopt-ai-research-protocol.md`)

This summary makes it obvious WHY each generated file exists. The validator's Phase 2 `repo-inspected` gate blocks until every section is populated.

## Heuristics by repo shape

### Frontend app

Pay extra attention to: routing, state management, API clients, forms / validation, styling system, component boundaries, e2e coverage.

### Backend service

Pay extra attention to: request lifecycle, auth / authorization, service / repository layers, background jobs, schema / migrations, external integrations, operational checks.

### Monorepo

Pay extra attention to: workspace topology, shared packages, cross-package dependencies, package-specific commands, app vs library boundaries, per-package conventions vs global conventions.

### Library / SDK

Pay extra attention to: public API surface, versioning / release flow, examples, compatibility guarantees, docs and tests around the exported interface.

### Infra repo

Pay extra attention to: environments, modules, shared templates, plan / apply commands, policy / validation tooling, safe execution constraints.

## Red flags

Slow down and ask the user before generating strong guidance if:

- the repo has multiple competing stacks and no clear dominant path
- scripts exist but are stale or clearly broken
- there are large generated or vendor directories obscuring the real source
- the repo is mid-migration and half the patterns are legacy
- the current branch includes unrelated user work that changes the repo structure

When in doubt, prefer explicit notes in the generated docs over false certainty.
