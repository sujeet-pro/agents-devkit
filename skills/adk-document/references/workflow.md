# adk-document — workflow

Five phases. Markdown-first. Does NOT publish (that's `/adk-sync`).

## Phase 0 — context-gather

- If source is a URL, fan-out fetch.
- If source is a prior skill's output (passed as a file path), load it.
- Detect target audience from `--audience` or `overrides.defaults.adk-document.audience`.

## Phase 1 — advise

- Up to 3 questions: tone, length target, intended publication destination (informs sync metadata even though sync is separate).
- Recommend template per `--type`.

## Phase 2 — execute (per `--type` sub-flow)

- Pull `shared/personas/doc-writer.md` + the per-type template.
- Generate markdown to `.temp/adk/document/<task>/draft.md`.
- Cite every claim (`path:line` or URL).
- Honor `--write-to` (writes to `<repo>/<path>`, gated on user OK).

## Phase 3 — validate

- Length within target (warn if 2× over).
- Every non-trivial claim has a citation.
- No filler phrases (anti-pattern grep: "in conclusion", "it's worth noting", "robust", "scalable", "modern", "enterprise-grade").
- Voice consistency for the chosen audience.

## Phase 4 — report

- Diff vs existing file if `--write-to` was used.
- Suggest `/adk-sync --to <destination>` for publishing.

## Persona + guidelines

- `shared/personas/doc-writer.md` (always).
- Auto-load (by `--type`):
  - runbook / rca / incident-summary → `observability.md`
  - api-reference / migration-guide → `api-design.md`
  - RCA with security implications / ADR with auth → `security.md`
  - readme / onboarding for UI projects → `accessibility.md`
