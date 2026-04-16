# Sources And Attribution

## Purpose
Track where ADK ideas came from and how they affect:
- published skills
- project-only maintenance skills
- docs and attribution

## Files
- `registry.json`: machine-readable source registry

## Rules
- Only record sources that were actually read or materially influenced behavior.
- Do not guess license or provenance details. If not verified, mark them as pending verification.
- When a source changes user-facing behavior, update:
  - `registry.json`
  - `NOTICE.md`
  - README or docs attribution if relevant

## Minimum Metadata Per Source
- source id
- kind
- URL
- branch or version when applicable
- local clone path when applicable
- role in ADK
- mapped published skills
- mapped project skills
- status

## Update Process
1. Clone or refresh the source in `.temp/reference-repos/` when it is a repository.
2. Compare the source against the current ADK behavior.
3. Decide the update scope using `../update-scope-policy.md`.
4. Apply the smallest correct change.
5. Refresh attribution if the visible behavior changed.
