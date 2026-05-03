# `code-write` — repo-conventions loader

Convention files in this priority order. The skill reads each that exists, loaded into context BEFORE Phase 4 (implement). The implementer subagent reads them again on its own to reinforce.

## File priority

| Priority | File | Why |
| --- | --- | --- |
| 1 | `AGENTS.md` (repo root) | The project's authoritative AI-instructions file (used by Cursor, Claude Code, Codex, etc.). Treat as gospel. |
| 2 | `CLAUDE.md` (repo root) | Claude-Code-specific instructions. Often a superset of `AGENTS.md`. |
| 3 | `.cursorrules` (repo root) | Cursor-specific instructions. Often older / superseded by `AGENTS.md`. Read it but prefer `AGENTS.md` when they conflict. |
| 4 | `CONTRIBUTING.md` (repo root) | Human-facing contribution guide. Slower to change, but authoritative on PR style. |
| 5 | `.github/CODEOWNERS` | Whose review the change will need. Useful for the report's "next steps" but not for the change itself. |
| 6 | `.eslintrc.*`, `.prettierrc.*`, `pyproject.toml [tool.ruff]`, `.editorconfig` | Style enforcement. Used to choose import order, quote style, indentation. |
| 7 | Recent commits in the changed area | Soft conventions (commit message style, refactor cadence, test placement). `git log -n 10 --pretty=full -- <file>`. |

## What to extract from each

### From `AGENTS.md` / `CLAUDE.md` / `.cursorrules`

- **Forbidden patterns.** Some repos forbid `any`, `console.log`, `moment` imports, `useEffect` for data fetching, etc. Honor these.
- **Required patterns.** "All routes use `asyncHandler`", "all responses use `OkResponse<T>`", "all dates formatted via `<RelativeTime>`".
- **Preferred libraries.** "Use `dayjs`, not `moment`". "Use `zod`, not `joi`".
- **Test conventions.** Naming, file location, mock policy.
- **Architecture rules.** Layer boundaries (e.g. "controllers may not import services directly — go through use-case classes").
- **Commit conventions.** Conventional Commits, gitmoji, custom format. Used by `code-write` only when it generates a commit message proposal in the report (it never commits — that's `adk-docs:docs-commit-message`).

### From `CONTRIBUTING.md`

- **PR template** location.
- **Required CI checks** (so we know what `code-write` should validate locally).
- **Branching model.** (Trunk-based, GitFlow, etc.) Used to default the new branch name.

### From `.eslintrc.*`, `.prettierrc.*`, etc.

- **Style enforcement** that the repo's lint will check. The implementer matches this preemptively.
- **Plugins enabled** — sometimes a plugin (e.g. `eslint-plugin-import`) enforces a specific import order; honor it.

### From `pyproject.toml [tool.ruff]`, `[tool.mypy]`, `[tool.black]`

- Same as ESLint/Prettier but for Python. Honor `line-length`, `target-version`, lint rules.

### From `.editorconfig`

- Indent style, indent size, end-of-line, charset. The implementer matches.

### From recent commits

- Style of subject lines.
- Average commit size — single-concern vs grab-bag.
- Whether tests live in the same diff as code (yes for trunk-based; sometimes split for feature-branch repos).

## Reading protocol

```bash
# Convention files
test -f AGENTS.md && cat AGENTS.md
test -f CLAUDE.md && cat CLAUDE.md
test -f .cursorrules && cat .cursorrules
test -f CONTRIBUTING.md && cat CONTRIBUTING.md

# Lint / format config (any that exists)
test -f .eslintrc.json && cat .eslintrc.json
test -f .eslintrc.cjs && cat .eslintrc.cjs
test -f .prettierrc && cat .prettierrc
test -f .prettierrc.json && cat .prettierrc.json
test -f pyproject.toml && cat pyproject.toml
test -f .editorconfig && cat .editorconfig

# Recent commits in target area
git log -n 10 --pretty=full -- "<file>"
```

In the skill, use the `Read` tool for these files (not `cat`); the above is just for the mental model.

## When conventions conflict

1. **`AGENTS.md` over `.cursorrules`.** The newer convention.
2. **Repo-level over team-level.** If the repo's `AGENTS.md` says X but a folder's local `AGENTS.md` says Y for that folder, the folder-level wins.
3. **Documented over inferred.** A documented rule in `AGENTS.md` beats a pattern observed across 3 commits.
4. **In doubt, ask one question.** Don't silently pick.

## What to put in `plan.md`

Under a `## Conventions consulted` section:

```markdown
## Conventions consulted
- AGENTS.md: "all routes use asyncHandler", "validate at boundary with zod"
- .editorconfig: 2-space indent, LF
- recent commits: subject line is "feat(scope): one-liner"
```

This makes review faster — the reviewer can check the convention citation against the diff.

## What to NOT do

- **Re-derive conventions from a single file.** Read at least 2-3 examples + the documented file.
- **Override a documented convention because you prefer your way.** This is autonomy-violation — the repo's owner already picked.
- **Skip these files because you've worked in this repo before.** Conventions evolve; re-read each session.
