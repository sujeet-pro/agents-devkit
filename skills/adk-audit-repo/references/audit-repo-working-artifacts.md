# Working Artifacts (.temp/ rule)

All intermediate artifacts must be written under `<project-root>/.temp/`. Non-negotiable regardless of runtime or harness.

## Required layout


| Path                                     | Purpose                                      |
| ---------------------------------------- | -------------------------------------------- |
| `.temp/plans/<slug>.md`                  | Implementation, refactor, or migration plans |
| `.temp/drafts/<slug>.md`                 | Prose drafts before promotion                |
| `.temp/reports/<slug>.md`                | Reviews, audits, investigations              |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos                        |
| `.temp/notes/<slug>.md`                  | Short-lived working notes                    |


Slugs are kebab-case; date-prefixed when uniqueness matters (`2026-04-20-login-redesign`).

## Rules

1. Never write intermediate artifacts outside `.temp/` (not repo root, not `docs/`, not source tree, not `~/Desktop`, not `/tmp`).
2. Never commit `.temp/`. If the project does not gitignore it, add it before writing.
3. Create `.temp/` on first use if missing.
4. Promote a file out of `.temp/` only when it is the deliverable in the location the user asked for.
5. Leave artifacts in place when the task is complete; they are durable context for follow-ups.