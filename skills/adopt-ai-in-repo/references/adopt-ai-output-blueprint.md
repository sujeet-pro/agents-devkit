# Output Blueprint

The canonical generated file tree this skill writes into the target repo. The exact tree expands or shrinks based on the repo, but the layered model is always the same:

1. **Canonical knowledge** in `ai-guidelines/`.
2. **Concise root entrypoints** (`AGENTS.md`, `CLAUDE.md`).
3. **Thin per-agent skill wrappers** under `.claude/skills/` and `.cursor/skills/` that point into `ai-guidelines/`.
4. **Python maintenance helpers** under `ai-guidelines/scripts/`.
5. **Hooks** that route through the Python helpers.

## Canonical output tree

```text
ai-guidelines/
├── README.md
├── agent-behavior.md
├── repo-summary.md
├── project-structure.md
├── architecture.md
├── data-flow.md
├── tooling-and-dependencies.md
├── scripts-and-commands.md
├── coding-guidelines.md
├── testing-guidelines.md
├── documentation-guidelines.md
├── workflows/
│   ├── development.md
│   ├── refactor.md
│   ├── migrate.md
│   ├── commit-and-pr.md
│   ├── review-local-changes.md
│   ├── docs-generation.md
│   ├── agentic-team.md
│   └── refresh-guidelines.md
├── research/
│   └── sources.md
├── packages/    or services/    (optional, monorepo-only)
└── scripts/
    ├── refresh_ai_guidelines.py
    └── run_project_checks.py
```

Generated root and platform files:

```text
AGENTS.md
CLAUDE.md
.claude/
├── settings.json          (when wire-hooks is on)
└── skills/
    ├── development/SKILL.md
    ├── refactor/SKILL.md
    ├── migrate/SKILL.md
    ├── commit/SKILL.md
    ├── add-pr-description/SKILL.md
    ├── review-local-changes/SKILL.md
    └── docs-generation/SKILL.md
.cursor/
├── skills/
│   ├── development/SKILL.md
│   ├── refactor/SKILL.md
│   ├── migrate/SKILL.md
│   ├── commit/SKILL.md
│   ├── add-pr-description/SKILL.md
│   ├── review-local-changes/SKILL.md
│   └── docs-generation/SKILL.md
├── rules/
│   └── project-ai-guidelines.mdc
└── hooks.json               (when wire-hooks is on)
```

If the target environment already has conflicting skill names, a repo-specific prefix such as `<repo>-` is acceptable, but the capability set should stay the same.

## Per-file content expectations

### `ai-guidelines/README.md`

Landing page. Should include:

- repo type and stack summary (one-liner each)
- quick links to the main guideline files
- command index pointing to `scripts-and-commands.md`
- how to refresh the guidance (one line; reference `scripts/refresh_ai_guidelines.py`)
- which generated repo-local skills exist (a list pointing at `.claude/skills/` and `.cursor/skills/`)
- note that `ai-guidelines/` is the canonical source of repo-specific AI guidance

### `agent-behavior.md`

Repo-local operating model for generated skills:

- workflow family expectations (when to plan, when to slice, when to validate)
- communication style (lead with the answer, bullets, no preamble)
- principal-engineer lens (when to question new abstractions / dependencies)
- workspace conventions (where intermediate work goes — usually `.temp/`)
- when to split work across multiple agents

### `repo-summary.md`

What the repo builds or owns; primary apps / services / packages; main users / downstream consumers; highest-risk or highest-value areas.

### `project-structure.md`

Top-level directories that matter; apps / services / packages / libraries; where shared code lives; where tests live; where docs / CI / deployment files live; where an agent should usually start for common tasks.

For monorepos: summarize the topology first; then add per-package docs under `packages/` or `services/`.

### `architecture.md`

Major layers and boundaries; key dependencies between modules; integration points; where domain logic should live; any architectural patterns or constraints detected.

If the repo has a current ADR or design doc, align terminology with it.

### `data-flow.md`

Highest-value flows an implementation or debugging agent needs. For frontend: user action → state update → API → handler → domain → persistence → render. For backend: entrypoint → middleware → controller → service → repository → persistence → response. For async: producers → queues → workers → retries → consumers.

### `tooling-and-dependencies.md`

Languages and runtimes; frameworks; package managers; workspace tools; lint / format tools; test frameworks; build / release tooling; container or infra tooling. Separate "directly used daily" from "supporting infra / CI".

### `scripts-and-commands.md`

MUST be command-accurate. For each selected command, include:

- exact command
- category: dev, build, format, lint, typecheck, test, e2e, docs, release, review, migration
- scope: repo-wide, package-specific, or service-specific
- expected cost: fast, medium, expensive
- whether hooks should use it
- when a human or agent should run it manually

If multiple packages have different commands, document them clearly instead of forcing one fake universal command.

Also capture commit and PR-related conventions when discoverable: commit message style, branch naming, PR template / expected sections, local review workflow.

### `coding-guidelines.md`

Most important day-to-day file for implementation agents. Include: naming conventions, directory / module organization, common abstractions, state management or service patterns, error handling, validation, logging, dependency boundaries, file-level anti-patterns to avoid.

The guidance combines: observed repo patterns + validated external best practices that fit the repo.

### `testing-guidelines.md`

Test frameworks and where tests live; preferred test granularity; fixture / mocking patterns; common setup helpers; what to test before shipping a change; which commands are fastest for local validation; when to run broader integration / e2e coverage.

### `documentation-guidelines.md`

Where docs live; naming and structure conventions; when to update docs; what kinds of changes require doc updates; how to keep terminology aligned with the codebase.

## Workflow docs

### `workflows/development.md`

How to understand the target area; when to plan first; which repo docs to read first; which commands to run before and after edits; when to use multiple agents; how to validate and summarize the work.

### `workflows/refactor.md`

How to analyze scope and blast radius; how to preserve behavior; when to add or run tests before refactoring; how to validate between steps; how to keep the refactor incremental.

### `workflows/migrate.md`

How to research official migration guides; how to map breaking changes to the repo; how to plan migrations in waves; how to validate after each wave; what manual follow-up to document.

### `workflows/commit-and-pr.md`

The repo's commit-message convention; how to infer scope from changed areas; what to include in commit bodies; how to build PR descriptions from branch-level changes; how to document testing in commit / PR summaries.

### `workflows/review-local-changes.md`

Review priorities in this repo; common bug patterns in the detected stack; what tests / checks matter most; when architecture or data-flow review matters more than style; how to reference `scripts-and-commands.md` during review.

### `workflows/docs-generation.md`

Where docs should be placed; repo terminology to reuse; how to verify examples and commands; how to keep docs aligned with implementation.

### `workflows/agentic-team.md`

When to split work across multiple agents; useful role splits (research, implementation, validation, review); how to divide monorepo work by app or package; how to synthesize findings back into one coherent plan.

### `workflows/refresh-guidelines.md`

When `ai-guidelines/` is likely stale; which changes should trigger refresh; how hooks or manual refresh should work; what to verify after refresh.

## Root docs

### `AGENTS.md`

Keep it short. Include:

- read `ai-guidelines/README.md` first
- read `ai-guidelines/agent-behavior.md` for workflow / communication expectations
- use the relevant workflow doc
- use the generated repo-local skills when available
- run repo-native validation commands before concluding
- prefer multiple agents for broad / risky work
- note that this file is the neutral router for Cursor, Codex, and other agents

### `CLAUDE.md`

Keep it short and Claude-specific. Include:

- read `ai-guidelines/README.md` first
- prefer repo-local skills in `.claude/skills/`
- use `ai-guidelines/agent-behavior.md` and `ai-guidelines/workflows/agentic-team.md` for larger work
- keep repo knowledge centralized in `ai-guidelines/`
- keep `AGENTS.md` as the neutral cross-agent entrypoint

## Skill wrapper pattern

See `adopt-ai-skill-wrapper-pattern.md` for the canonical thin-wrapper Markdown shape.

## Markers

Every generated file (Markdown + JSON) carries opening/closing markers around the managed section:

```
<!-- adk:adopt:start -->
... managed content ...
<!-- adk:adopt:end -->
```

In JSON files use a `// adk:adopt:start` / `// adk:adopt:end` pair if the format allows comments, OR an `_adk_adopt: { managed: true, version: <n> }` key. Without markers, the merge strategy treats the file as user-authored.

## Merge strategy

When files already exist: preserve user-authored content per `adopt-ai-merge-strategy.md`. Update only clearly-managed sections. If a file has no markers, append a new managed section rather than replacing.

If the repo already has a better structure than this blueprint, ADAPT to it while keeping `ai-guidelines/` as the canonical knowledge source.
