# `code-write` — workflow detail

## Phase 0 — prompt expand

1. **Restate** the prompt in your own words. One sentence.
2. **Resolve the repo** by walking up from CWD to a `.git` directory and matching against `~/.config/adk/repos.md` (`repos[].path` first, then `git remote get-url`).
3. **Identify likely files**. Read the prompt for entity hints (component name, route name, table name). Use Grep + Glob to surface the candidate set. List them in the proposal.
4. **Pick task slug** via `bin/adk-task-slug "<prompt>"` (kebab-case, max 6 words).
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt` with the verbatim user prompt + ISO timestamp.
6. **Approval gate** unless `--auto`: show restated prompt + resolved repo + likely-files set. Ask "proceed?".

## Phase 1 — preflight

1. `git status`. If dirty, surface the dirty list and ask: stash, abort, or include?
2. `git rev-parse --abbrev-ref HEAD`. If on `main` / `master` / `develop`, prompt to create a feature branch (don't auto-create unless `--auto` AND the prompt named the branch).
3. Resolve test / typecheck / lint commands:
    - From `~/.config/adk/repos.md` `repos[].notes` if the user has documented them.
    - From `package.json scripts`, `pyproject.toml`, `Makefile`, `build.gradle`, `Cargo.toml`, `go.mod`.
    - Default fallbacks per stack live in `references/validation-recipes.md`.
4. Run **baseline check**: typecheck + lint + tests on HEAD. If red, STOP. Do not edit on top of pre-existing failures. Surface the red baseline in `plan.md` and ask the user how to proceed.

## Phase 2 — read first

1. Read every file in the candidate set from Phase 0. Use Read; do not skim with Grep alone for files about to be edited.
2. Read 1-2 adjacent test files to learn the test style + the framework's idioms in this repo.
3. Read the closest 1-hop dependencies of each target file (the modules they import or are imported by).
4. Read recent commits in the same area: `git log -n 10 -- <file>`. Note conventions in commit message style + diff shape.
5. Read `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `CONTRIBUTING.md` if present at repo root or any ancestor of the target files (see `references/repo-conventions-loader.md`).

## Phase 3 — plan

Write `.temp/task-<slug>/plan.md` (full shape in `references/output-format.md`):

- **Goal** — one sentence.
- **Scope** — the resolved repo + path subtree.
- **Files touched** — table: path, action (create/edit), one-line WHY.
- **Approach** — 3-6 bullets. Sequence of edits.
- **Edge cases** — table: condition, expected behavior, test pointer.
- **Test changes** — new test files; new tests in existing files; existing tests that may need updating.
- **Validation plan** — exact commands to run; expected exit code 0.
- **Out of scope (deliberate)** — bullet list of things you noticed but did not change, with reason.

Approval gate unless `--auto`. Under `--auto`, the plan is still written; just no gate.

## Phase 4 — implement

1. Spawn the `implementer` subagent (`agents/implementer.md` from `adk-code`) with:
    - `.temp/task-<slug>/plan.md`
    - `.temp/task-<slug>/prompt.txt`
    - The slug
    - The mode (`--auto` or `-i`)
2. The implementer follows its own protocol (read before write, edit per file, validate per file, hand off).
3. If the change introduces new behavior branches, also spawn the `test-engineer` subagent to author the new tests. Run them in parallel only if the test files are independent of the implementation files; otherwise sequence implementer → test-engineer.
4. Re-read each changed file after the agent reports done; confirm it actually contains what the report claims.

## Phase 5 — validate

1. Run typecheck (whole-package if monorepo; whole-repo if single-package).
2. Run lint with `--max-warnings 0` if the repo's CI does.
3. Run the test suite scoped to the affected package(s).
4. Capture stdout/stderr to `.temp/task-<slug>/validation/per-skill/code-write.md`.
5. If any check fails: read the failure, identify the cause, fix in the smallest possible follow-up edit, re-run. Iterate up to 3 times. After 3 failures of the same kind, STOP and surface to the user.

## Phase 6 — report

Write `.temp/task-<slug>/report.md` (full shape in `references/output-format.md`):

- **Result** — one sentence.
- **Files changed** — table: path, +N/-M, one-line WHY.
- **Validation evidence** — commands + exit codes.
- **Decisions made** — list of branches the skill auto-picked under `--auto` (or because trivial).
- **Residual risk / follow-ups** — bullet list, prioritized.
- **NOT done (deliberate)** — bullet list with reason.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question: "Need more detail on any decision?".

## Loop control

- After 3 failures of the same kind on the same validation step, STOP and surface to the user.
- If the implementer reports it had to touch a file outside the planned set, RE-CONFIRM before letting it proceed.
- If the validation suite times out (e.g. a flaky integration test), capture the timeout and treat as a red signal that needs operator attention; don't loop on it silently.
