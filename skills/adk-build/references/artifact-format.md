# Artifact Format

The deliverable from `adk-build` is the artifact described below. Working notes (plans, drafts, raw evidence) ALWAYS live under `.temp/` in the host repo. The artifact itself lives wherever this skill says it lives — sometimes under `.temp/`, sometimes in the repo proper, sometimes as a remote object (PR comment, Confluence page).

## Artifact type
`build-routing-decision`

## Format
Inline message.

## Path / Location
(none)

## .temp/ contract

All intermediate artifacts (plans, drafts, raw notes, cloned reference repos, scratch markdown) MUST be written under `.temp/` in the host repo, using these subfolders:

| Path | Purpose |
| --- | --- |
| `.temp/plans/<slug>.md` | Implementation, refactor, or migration plans |
| `.temp/drafts/<slug>.md` | Prose drafts before promotion |
| `.temp/reports/<slug>.md` | Reviews, audits, investigations |
| `.temp/reference-repos/<owner>__<repo>/` | Cloned external repos for research |
| `.temp/notes/<slug>.md` | Short-lived working notes |

`.temp/` is gitignored. Promote a file out of `.temp/` ONLY when it is the deliverable the user asked for, in the location they asked for it.

## Promotion rule

Once a draft / plan / report becomes the final deliverable that the user wants tracked, promote it from `.temp/` to its committed home (`docs/`, `README.md`, an ADR file, a Confluence page, etc.). Until then, leave it in `.temp/` so the next agent / session can find it.
