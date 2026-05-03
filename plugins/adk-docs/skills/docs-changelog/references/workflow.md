# `docs-changelog` — workflow detail

## Phase 0 — prompt expansion

1. Resolve repo via `repos.md`.
2. Resolve `CHANGELOG.md` path: `~/.config/adk/docs.md.changelog_path`
   (default `CHANGELOG.md` at repo root). Stop with a fix-this message
   if the file is missing and the user asked for an `--fix` write.
3. Parse `<from-tag>` and `<to-tag>` from arguments. Defaults:
   - `<to-tag>` → `HEAD`.
   - If only one arg is given and it looks like a tag, treat as
     `<to-tag>` and set `<from-tag>` to the previous tag via
     `git describe --tags --abbrev=0 <to-tag>^`.
4. Pick slug: `changelog-<to-tag-normalized>` (e.g. `changelog-v1-2-0`).
   Create `.temp/task-<slug>/`.

## Phase 1 — preflight

1. `bin/adk-info --check`.
2. `git rev-parse <from-tag>^{commit}` and `<to-tag>^{commit}` —
   both must succeed. Stop with a fix-this message otherwise.
3. Read the first 100 lines of `CHANGELOG.md` to detect style per
   `references/keep-a-changelog-format.md`. Record in
   `detected-style.txt`.
4. Detect the existing "release header" pattern:
   - Keep a Changelog: `## [VERSION] - YYYY-MM-DD`.
   - semantic-release: `## [VERSION] (YYYY-MM-DD)`.
   - free-form: varies; mirror the most recent header.

## Phase 2 — gather evidence

1. `git log <from>..<to> --pretty=format:%H%x1f%s%x1f%b%x1e --no-merges > commits.txt`.
2. For each commit, extract:
   - SHA + subject + body.
   - Conventional Commits type + scope (if the repo uses Conventional).
   - Breaking-change signal: `!` in subject OR `BREAKING CHANGE:`
     footer in body.
   - PR reference: `#NNNN` or `(#NNNN)` suffix.
   - Ticket refs: `CHK-\d+`, `LIN-\d+`, `#\d+`.
3. Classify:
   - Conventional `feat` → `Added`.
   - Conventional `fix` → `Fixed`.
   - Conventional `docs` / `chore` / `ci` / `build` → `Changed` (or
     drop from changelog entirely if the repo's existing style
     excludes chore).
   - Conventional `perf` → `Changed`.
   - Conventional `refactor` → `Changed` (usually dropped from user-
     facing changelogs; user's call).
   - Free-form: classify by keyword heuristic (`fix` / `bug` →
     `Fixed`; `add` / `introduce` → `Added`; etc.).
4. Write `.temp/task-<slug>/classified.md` — table of commit → group
   → user-readable sentence (drafted) → PR link + breaking flag.

## Phase 3 — draft

1. Build `changelog-entry.md`:
   - Header line matching the existing release-header pattern.
   - Breaking changes section FIRST (if any) per
     `references/breaking-change-callout.md`.
   - Groups in the order used by the existing style (Keep a Changelog:
     Added / Changed / Deprecated / Removed / Fixed / Security).
   - Entries are one sentence each; imperative mood starting with a
     verb like "Adds", "Fixes", "Removes".
2. PR / commit reference at the end of each entry:
   - If Keep-a-Changelog-style uses `([#NNNN][])` footnote links,
     match it.
   - If semantic-release uses inline `([abc1234](<commit-url>))`,
     match it.
3. Leave a clean, one-blank-line separator between groups.

## Phase 4 — validate + optional `--fix`

1. Run `references/validator.md` gates.
2. If not `--fix`, stop with final report.
3. If `--fix`:
   - Locate the insertion point in `CHANGELOG.md`: immediately
     before the most-recent previous version block (after the
     top-of-file header / unreleased section).
   - Back up `CHANGELOG.md` to `.temp/task-<slug>/backup/CHANGELOG.md`.
   - Insert the new version block.
   - Re-validate: re-read the modified `CHANGELOG.md`, confirm the
     block landed cleanly and no other text was mutated.
   - `git add CHANGELOG.md` (stage only; do NOT commit).

## Loop control

- If the validator rejects 3× in a session, stop and surface.
- If the detected style is ambiguous, stop in `-i` mode and ask;
  under `--auto`, default to Keep a Changelog.
- If `<from>..<to>` has 0 commits, stop and surface.
