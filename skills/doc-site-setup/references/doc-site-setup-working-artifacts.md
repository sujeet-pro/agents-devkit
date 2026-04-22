# Working Artifacts (.temp/ rule)

All intermediate artifacts must be written under `<project-root>/.temp/`. Non-negotiable regardless of runtime or harness.

## Required layout
| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Setup plan (packages, config, content scaffold, prj-* install matrix) |
| `.temp/drafts/<slug>.md` | Drafted page content before promotion into `<content-dir>/` |
| `.temp/reports/<slug>.md` | Validation reports, audits, investigations |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos used as reference |
| `.temp/notes/<slug>.md` | Short-lived working notes (e.g. discovered docs candidates, harness folders detected) |

Slugs are kebab-case; date-prefixed when uniqueness matters (`2026-04-21-doc-site-setup`).

## Rules
1. Never write intermediate artifacts outside `.temp/` (not repo root, not `docs/`, not source tree, not `~/Desktop`, not `/tmp`).
2. Never commit `.temp/`. If the project does not gitignore it, add it before writing.
3. Create `.temp/` on first use if missing.
4. Promote a file out of `.temp/` only when it is the deliverable in the location the user asked for (e.g. a drafted `getting-started/README.md` only moves into `<content-dir>/guide/getting-started/README.md` once approved).
5. Leave artifacts in place when the task is complete; they are durable context for follow-ups (the next agent can read your setup plan).
