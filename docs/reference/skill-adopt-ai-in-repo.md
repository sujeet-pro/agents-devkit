---
title: 'adopt-ai-in-repo'
description: 'Analyze the current repository deeply, detect its stack and collaboration conventions, research stack-specific best practices, and bootstrap cross-agent AI guidance — `ai-guidelines/` (canonical knowledge), `AGENTS.md` (neutral router), `CLAUDE.md` (Claude-specific delta), repo-local task skills under `.claude/skills/` and `.cursor/skills/`, and Python-based maintenance hooks. Use when onboarding AI to an existing repo or refreshing repo-aware agent scaffolding after the codebase has changed. Do not use for greenfield project scaffolding (use the repo''s own templates) or for adopting a single skill into an already-scaffolded repo (just edit the file).'
skill_name: adopt-ai-in-repo
category: task
---
# ADK Adopt AI In Repo

Standalone task skill. Bootstraps the canonical "AI scaffolding" inside a target repo so any agent (Claude, Cursor, Codex, Gemini, Antigravity, Junie, plain `AGENTS.md` reader) can work on it productively.

The output is layered: canonical repo knowledge in `ai-guidelines/`, thin root entrypoints (`AGENTS.md`, `CLAUDE.md`), thin per-agent skill wrappers that point into `ai-guidelines/`, and Python maintenance helpers under `ai-guidelines/scripts/`.

## When to use

- Onboarding AI to an existing repository for the first time.
- Refreshing existing AI scaffolding after a stack change, framework migration, or major refactor.
- Standardizing AI guidance across a fleet of repos (run once per repo).
- Fixing inconsistent / drifted AI files (`.cursorrules` + `AGENTS.md` + a hand-written `CLAUDE.md` that no longer agree).

## When NOT to use

- Greenfield project scaffolding → use the repo's own `create-*` templates first; run this skill after the project exists.
- Adopting a single skill into a repo that already has the scaffolding → just add the skill file.
- Reviewing or auditing existing AI scaffolding → `@adk:audit-repo` (a.k.a. `adk-audit-repo`) (with focus on docs / conventions).
- Editing a single guideline file → `@adk:docs-write` (a.k.a. `adk-docs-write`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<repo-path>` | yes | Absolute or relative path to the target repo (default: current working directory) |
| `--refresh` | optional | Update existing scaffolding instead of treating the repo as a first-time bootstrap |
| `--no-hooks` | optional | Skip writing hook configs; still document the recommended hook commands |
| `--scope <stack>` | optional | Limit research and skill generation to one detected stack (default: all detected) |
| `--auto` | optional | Skip approval gates (still validates per `adopt-ai-validator.md`) |

## Workflow

1. **Confirm intent** — restate target repo, refresh / fresh-bootstrap mode, hook policy, scope. Approval gate unless `--auto`.
2. **Validator gate (Phase 1)** — pre-execution checks per `adopt-ai-validator.md`: target is a git repo, write permission, no in-progress merge, no untracked files in `ai-guidelines/` if refreshing.
3. **Inspect repo** — deeply analyze the repo per `repo-analysis-playbook.md`: manifests, lockfiles, CI, linters, formatters, tests, app entrypoints, major packages, representative source files, git/PR conventions.
4. **Validator gate (Phase 2: `repo-inspected`)** — every section of the playbook produced an evidence note in `.temp/notes/`.
5. **Detect stack and conventions** — classify repo type (frontend / backend / fullstack / library / monorepo / infra / docs / data), languages, frameworks, package manager, test runners, lint/format tools, build tooling, commit-message style, PR conventions.
6. **Research targeted external sources** — per `adopt-ai-research-protocol.md`, run focused web research only on the dominant detected stacks. Prefer official docs over generic blog advice.
7. **Plan output tree** — propose the file tree per `adopt-ai-output-blueprint.md`: `ai-guidelines/`, root `AGENTS.md` + `CLAUDE.md`, per-agent skill wrappers, hooks. Approval gate unless `--auto`.
8. **Validator gate (Phase 2: `plan-approved`)** — file tree + skill catalog + hook commands all named and approved.
9. **Generate `ai-guidelines/`** — write the canonical knowledge base files per the blueprint, populated from the evidence summary.
10. **Generate root entrypoints** — write or merge `AGENTS.md` (neutral router) and `CLAUDE.md` (Claude-specific delta). Preserve existing user-authored content per `adopt-ai-merge-strategy.md`.
11. **Generate skill wrappers** — write thin skill files under `.claude/skills/` and `.cursor/skills/` per the catalog (development, refactor, migrate, commit, add-pr-description, review-local-changes, docs-generation). Each wrapper is a thin pointer into `ai-guidelines/`.
12. **Wire hooks** (unless `--no-hooks`) — write `.cursor/hooks.json` and `.claude/settings.json` hook configs that call the Python helpers under `ai-guidelines/scripts/`. Use real repo-native commands derived from the actual scripts / task runners.
13. **Validate (Phase 3: pre-handoff)** — every check in `adopt-ai-validator.md` Phase 3: every linked file exists, every command in `scripts-and-commands.md` runs cleanly (or is documented as expensive / requires-setup), every skill wrapper points at a real `ai-guidelines/` file, hook configs parse.
14. **Validate (Phase 4: post-execution)** — file tree generated, skill catalog complete, hook configs valid, summary report written to `.temp/reports/`.
15. **Report** — per `adopt-ai-output-format.md`: status banner, detected stack, generated file tree, skill catalog, hook coverage, remaining manual follow-up.

## Operating principles

- **Treat the repo as the source of truth.** Infer everything from the code and config first; reach for external docs second.
- **Keep canonical knowledge in `ai-guidelines/`.** Generated skill wrappers are thin pointers, not copies.
- **`AGENTS.md` is neutral; `CLAUDE.md` is a thin Claude delta.** Do NOT duplicate long instructions in both.
- **Hooks use real commands.** Derive `lint`, `format`, `build`, `typecheck`, `test` commands from the repo's own scripts / task runners. Never invent.
- **Python helpers, not shell.** Maintenance helpers under `ai-guidelines/scripts/` are Python — easier to test and to keep cross-platform than shell.
- **Preserve existing user content.** Merge into managed sections; never overwrite custom files blindly.
- **Refresh-safe.** Re-running the skill on the same repo with `--refresh` converges; it does not regenerate or churn unchanged files.

## Default skill catalog

These skills get a thin wrapper under `.claude/skills/` and `.cursor/skills/`. Each one points into `ai-guidelines/` for the actual instructions. Pre-fix with the repo's own short token (e.g., `myproject-`) only when name collisions exist with another tool's skills.

| Wrapper name | Points at |
| --- | --- |
| `development` | `ai-guidelines/workflows/development.md` + coding / testing guidelines |
| `refactor` | `ai-guidelines/workflows/refactor.md` + coding / testing guidelines |
| `migrate` | `ai-guidelines/workflows/migrate.md` + tooling / commands guidelines |
| `commit` | `ai-guidelines/workflows/commit-and-pr.md` + commands guidelines |
| `add-pr-description` | `ai-guidelines/workflows/commit-and-pr.md` + commands guidelines |
| `review-local-changes` | `ai-guidelines/workflows/review-local-changes.md` + coding / testing guidelines |
| `docs-generation` | `ai-guidelines/workflows/docs-generation.md` + documentation guidelines |

The skill wrappers are 10-30 lines each. They are NOT a place to put long instructions — those live in `ai-guidelines/`.

## Default hook catalog

When hooks are enabled (default; `--no-hooks` to skip), the skill wires:

- **Pre-commit** — fast lint + format on changed files (uses repo-native command).
- **Pre-push** — typecheck + smallest-relevant test (uses repo-native command).
- **Refresh-after-stack-change** — when `package.json` / `pyproject.toml` / `go.mod` / etc. changes, suggest re-running this skill with `--refresh`.

All hook commands route through `ai-guidelines/scripts/run_project_checks.py` so the actual command set lives in one place.

## Output format

Full report shape lives in `adopt-ai-output-format.md`. The default report leads with status banner, detected stack, generated file tree, skill catalog, hook coverage, and remaining manual follow-up.

## Anti-patterns

See `adopt-ai-anti-patterns.md` for the full list. Key ones:

- Generating a `ai-guidelines/` tree without first reading the repo (vibes-based scaffolding).
- Inventing commands that aren't in the repo's own scripts / task runners.
- Duplicating long instructions in both `AGENTS.md` AND `CLAUDE.md`.
- Generating shell helpers when the constraint is "Python-based maintenance helpers".
- Overwriting existing user-authored AI files without merge.
- Generating skills that don't point into `ai-guidelines/` (defeats the canonical-knowledge model).
- Skipping the validator phases.

## Examples

```
adk-adopt-ai-in-repo .
```

First-time bootstrap of the current repo, all stacks, hooks enabled, default-ask flow.

```
adk-adopt-ai-in-repo /path/to/repo --refresh --auto
```

Refresh existing scaffolding, no questions asked, picks documented defaults.

```
adk-adopt-ai-in-repo . --scope frontend --no-hooks
```

Generate scaffolding for the frontend package only; do not write hook configs.

See `adopt-ai-examples.md` for full output samples.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the documented default (see `adopt-ai-clarifying-questions.md`) and reports the choices.

1. **What is the target repo path?** — _How to pick:_ Default = current directory. Override only if working on a sibling repo.
2. **Fresh bootstrap or `--refresh` an existing setup?** — _How to pick:_ If `ai-guidelines/` does not exist → fresh. If it exists → refresh (preserves user content). The skill auto-detects by default.
3. **Wire hooks (`.cursor/hooks.json`, `.claude/settings.json`) or skip with `--no-hooks`?** — _How to pick:_ Default = wire hooks. Skip if the repo has its own husky / lefthook / pre-commit setup that you do not want to disturb.
4. **Scope: all detected stacks or a single one (e.g., frontend, backend)?** — _How to pick:_ Default = all. Narrow only when the repo is a monorepo and you only own one slice.

## Default vs detailed output

**Default report:** Status banner + detected stack + generated file tree + skill catalog + hook coverage + manual follow-up.

**Detailed report (on request or `--verbose`):** Add: full evidence summary from `repo-analysis-playbook.md`, per-file rationale, command-validation output, merge diff for any preserved user content, full hook config inline.

**Artifact:** `ai-scaffolding` — a tree of files under the target repo (`ai-guidelines/`, `AGENTS.md`, `CLAUDE.md`, `.claude/skills/*`, `.cursor/skills/*`, hook configs). The artifact lives IN the target repo (not under `.temp/`); only the evidence summary, validator log, and merge-diff notes go under `.temp/`.

**Artifact paths:**
- Generated tree: in the target repo (per `adopt-ai-output-blueprint.md`).
- Evidence summary: `.temp/notes/adopt-ai-<repo-slug>-evidence.md`.
- Validator log: `.temp/notes/adopt-ai-<repo-slug>-validator.md`.
- Final report: `.temp/reports/adopt-ai-<repo-slug>.md`.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/interaction-contract.md` | Default-ask, explained-options, `--auto` contract every skill must follow (global, identical across skills). |
| `references/adopt-ai-persona.md` | The repo-AI-bootstrapper persona (mission, focus areas, hard rules, status banner). |
| `references/adopt-ai-constitution.md` | Constitution: shared ADK baseline + skill-specific non-negotiables for repo bootstrapping. |
| `references/adopt-ai-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/adopt-ai-output-format.md` | Default vs detailed report shapes; status banner; verbosity rules. |
| `references/adopt-ai-artifact-format.md` | The deliverable's format and where it lives (in-repo tree + `.temp/` evidence + reports). |
| `references/adopt-ai-anti-patterns.md` | Things to avoid when running this skill. |
| `references/adopt-ai-examples.md` | Trigger phrases, sample invocations, sample output. |
| `references/repo-analysis-playbook.md` | Repo inspection heuristics, stack detection, evidence gathering — the deep-analysis playbook. |
| `references/adopt-ai-research-protocol.md` | How to run targeted external research on the detected stack; source ordering; stop conditions. |
| `references/adopt-ai-output-blueprint.md` | Canonical generated file tree and content expectations for `ai-guidelines/` + root + skill wrappers. |
| `references/adopt-ai-skill-wrapper-pattern.md` | The thin-wrapper pattern for `.claude/skills/*` and `.cursor/skills/*` files. |
| `references/adopt-ai-hook-bootstrap.md` | Hook config patterns (Claude `.claude/settings.json`, Cursor `.cursor/hooks.json`) and the Python helper layout under `ai-guidelines/scripts/`. |
| `references/adopt-ai-merge-strategy.md` | How to preserve user-authored content when refreshing existing AI files. |
| `references/adopt-ai-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) the skill MUST run. |

<!-- adk:references:end -->
