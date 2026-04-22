# `temp-folder` — validator

## Phase 1 — pre-execution
- [ ] `.gitignore` exists and contains `.temp/`.
- [ ] `.temp/` is a directory (not a file).

## Phase 2 — mid-flow
- [ ] Slug is kebab-case `[a-z0-9][a-z0-9-]*`, max 60 chars.
- [ ] `.temp/task-<slug>/` is a directory.

## Phase 3 — pre-handoff (when a skill is about to return its artifact)
- [ ] Artifact sub-path matches the canonical table.
- [ ] Parent dirs of the artifact exist.

## Phase 4 — post-execution
- [ ] No file written outside `.temp/` since this validator pass started.
- [ ] Git status shows `.temp/` is ignored (`git check-ignore .temp/<anything>`).
