# Skill Wrapper Pattern

Every generated skill wrapper under `.claude/skills/<name>/SKILL.md` and `.cursor/skills/<name>/SKILL.md` is a thin pointer into `ai-guidelines/`. They are 10-30 lines each. Long instructions go in `ai-guidelines/`, NOT in the wrappers.

The wrappers are NOT a place to put guidance. The wrappers tell the agent which `ai-guidelines/` files to read for THIS task. That's the contract.

## Canonical shape (Markdown + YAML frontmatter)

```md
---
name: <task>
description: <One sentence describing what this skill does in this repo, ending with "using the repo-specific guidance in ai-guidelines/.">
---

# <Task title>

Read these files before <doing the task>:

- `<path-to-ai-guidelines>/README.md`
- `<path-to-ai-guidelines>/agent-behavior.md`
- `<path-to-ai-guidelines>/<relevant-guideline>.md`
- `<path-to-ai-guidelines>/workflows/<relevant-workflow>.md`

If the task is broad, cross-package, or high-risk, also read:

- `<path-to-ai-guidelines>/workflows/agentic-team.md`
```

`<path-to-ai-guidelines>` is `../../../ai-guidelines` from `.claude/skills/<name>/SKILL.md` (and the same depth from `.cursor/skills/<name>/SKILL.md`).

## Default catalog (7 wrappers per surface)

| Wrapper name | Title | Reads from `ai-guidelines/` |
| --- | --- | --- |
| `development` | Development | README + agent-behavior + coding-guidelines + testing-guidelines + workflows/development.md |
| `refactor` | Refactor | README + agent-behavior + coding-guidelines + testing-guidelines + workflows/refactor.md |
| `migrate` | Migrate | README + agent-behavior + tooling-and-dependencies + scripts-and-commands + workflows/migrate.md |
| `commit` | Commit | README + agent-behavior + scripts-and-commands + workflows/commit-and-pr.md |
| `add-pr-description` | Add PR Description | README + agent-behavior + scripts-and-commands + workflows/commit-and-pr.md |
| `review-local-changes` | Review Local Changes | README + agent-behavior + coding-guidelines + testing-guidelines + workflows/review-local-changes.md |
| `docs-generation` | Docs Generation | README + agent-behavior + documentation-guidelines + workflows/docs-generation.md |

## Worked example: `development` wrapper

```md
---
name: development
description: Build changes in this repository using the repo-specific guidance in ai-guidelines/. Use when planning or implementing code changes here.
---

# Development

Read these files before editing:

- `../../../ai-guidelines/README.md`
- `../../../ai-guidelines/agent-behavior.md`
- `../../../ai-guidelines/coding-guidelines.md`
- `../../../ai-guidelines/testing-guidelines.md`
- `../../../ai-guidelines/workflows/development.md`

If the task is broad, cross-package, or high-risk, also read:

- `../../../ai-guidelines/workflows/agentic-team.md`
```

## Worked example: `commit` wrapper

```md
---
name: commit
description: Prepare a commit in this repository using the repo-specific guidance in ai-guidelines/. Use when staging changes and writing a commit message.
---

# Commit

Read these files before staging or writing the commit message:

- `../../../ai-guidelines/README.md`
- `../../../ai-guidelines/agent-behavior.md`
- `../../../ai-guidelines/scripts-and-commands.md`
- `../../../ai-guidelines/workflows/commit-and-pr.md`

Run repo-native validation before committing. The exact commands are in `scripts-and-commands.md`.
```

## Cursor-specific frontmatter

Cursor wrappers may need additional frontmatter keys. The exact schema varies by Cursor version. Detect and inject what's needed; otherwise the same pattern as Claude works.

If the Cursor schema requires additional fields (e.g., `argument-hint`, `model`, `globs`), add them but keep the body short.

## Naming collisions

If the target environment already has another tool's `development` skill (or any other name in the catalog), prefix all generated skills with `<repo>-` (where `<repo>` is the kebab-case repo name). For example: `myproject-development`, `myproject-commit`.

The catalog stays the same; only the names get the prefix.

## What NOT to do

- Don't put the actual instructions in the wrapper. They live in `ai-guidelines/`.
- Don't list every `ai-guidelines/` file in every wrapper. Only the ones relevant to this task.
- Don't duplicate the workflow doc inline. Link to it.
- Don't include validation commands in the wrapper. They are in `scripts-and-commands.md`.
- Don't make wrappers longer than ~30 lines. If you need more, you're putting guidance in the wrong place.
