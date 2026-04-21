# Working Artifacts: the `.temp/` rule

When working inside any project, **all intermediate artifacts must be written
under `<project-root>/.temp/`**. This is non-negotiable and applies regardless
of which runtime, harness, or skill you are operating under.

## What counts as an intermediate artifact

- Plan files, restructure proposals, design documents.
- Drafts (prose, code outlines) that are not the final deliverable.
- Investigation reports, audit notes, review findings.
- Cloned reference repositories used for research.
- Short-lived working notes, scratch markdown, throwaway snippets.
- Any markdown file produced *during* a task that is not what the user asked
you to deliver.

## Required layout

Use these subfolders consistently so the next agent (or the human) can find
prior work:


| Path                                     | Purpose                                      |
| ---------------------------------------- | -------------------------------------------- |
| `.temp/plans/<slug>.md`                  | Implementation, refactor, or migration plans |
| `.temp/drafts/<slug>.md`                 | Prose drafts before promotion                |
| `.temp/reports/<slug>.md`                | Reviews, audits, investigations              |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research           |
| `.temp/notes/<slug>.md`                  | Short-lived working notes                    |


Slugs are kebab-case and may include the date when uniqueness matters
(`2026-04-20-login-redesign`).

## Rules

1. **Never** write intermediate artifacts to the repo root, `docs/`, the
  project's source tree, `~/Desktop`, `/tmp`, or anywhere outside `.temp/`.
2. **Never** commit `.temp/`. If a project does not already gitignore it, add
  `.temp/` to the project's `.gitignore` before writing anything to it.
3. If `.temp/` does not exist, create it on first use.
4. Only promote a file out of `.temp/` once it is the deliverable the user
  asked for, in the location they asked for it.
5. When a task is complete, leave the artifacts in place — they are durable
  context for follow-up sessions, not garbage.

## Why

This contract gives every agent (and every human) a single, predictable place
to find what was generated during a task: plans before they were executed,
research before it was distilled, drafts before they were promoted. It also
keeps the user's working tree clean, makes diffs reviewable, and prevents
accidental commits of intermediate scratch.